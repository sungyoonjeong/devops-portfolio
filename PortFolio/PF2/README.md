# PF2 — Go + Docker 마이크로서비스 배포 자동화

> 작업 기간: 2026-06-21  
> 기술 스택: `Go 1.22` `Docker` `Docker Compose` `nginx` `Trivy` `Bash`

---

## 프로젝트 개요

Go로 작성한 HTTP 서버를 Docker 컨테이너로 패키징하고, nginx 리버스프록시와 함께 `deploy.sh` 한 줄로 배포까지 완료하는 자동화 파이프라인을 구축했다.

**핵심 목표**
- 멀티스테이지 빌드로 최종 이미지 크기를 ~10MB로 최소화
- nginx를 앞단에 두어 Go 서버를 외부에 직접 노출하지 않는 구조 설계
- Trivy로 이미지 보안 취약점을 배포 전에 자동 스캔하고 JSON 파일로 기록
- 빌드 → 스캔 → 재시작 → 헬스체크를 스크립트 하나로 자동화

---

## 디렉토리 구조

```
PF2/
├── main.go                            Go HTTP 서버 (/health, /metrics 엔드포인트)
├── go.mod                             Go 모듈 선언 (module pf2, go 1.22)
├── Dockerfile                         멀티스테이지 빌드 (golang:1.22-alpine → alpine:3.19)
├── docker-compose.yml                 app + nginx 서비스 정의
├── nginx/
│   └── nginx.conf                     리버스프록시 설정 (80 → 8080)
├── deploy.sh                          배포 자동화 스크립트
├── trivy-reports/
│   └── pf2-<commit>-<date>.json       Trivy 스캔 결과 (배포마다 자동 생성)
└── README.md
```

---

## 아키텍처

```
외부 클라이언트
      │
      │ HTTP :80
      ▼
┌─────────────┐
│    nginx    │  리버스프록시 — 외부 유일한 진입점
└──────┬──────┘
       │ HTTP :8080 (도커 내부 네트워크)
       ▼
┌─────────────┐
│   Go 앱     │  외부 직접 노출 없음 (expose만, ports 미사용)
└─────────────┘
```

Go 서버는 `expose`만 선언하여 도커 내부 네트워크에서만 접근 가능하고, 외부 트래픽은 반드시 nginx를 통해서만 들어온다. 이 구조를 리버스프록시 패턴이라 하며, Go 서버를 외부 공격으로부터 보호하고 nginx에서 SSL 종료·접근 로그·로드밸런싱을 일괄 처리할 수 있다.

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/health` | 서버 생존 여부 확인 (헬스체크) |
| GET | `/metrics` | 누적 요청 수 · 가동 시간 조회 |

**`/health` 응답 예시**
```json
{
  "status": "ok",
  "timestamp": "2026-06-21T10:38:06+09:00"
}
```

**`/metrics` 응답 예시**
```json
{
  "requests_total": 42,
  "uptime_seconds": 300
}
```

`requests_total`은 `sync/atomic`으로 관리한다. 웹 서버는 요청을 동시에 여러 고루틴에서 처리하기 때문에 일반 정수 증감(`i++`)은 race condition이 발생할 수 있다. `atomic.AddInt64`는 CPU 수준에서 원자적 연산을 보장하여 뮤텍스 없이도 안전하게 카운터를 증감한다.

---

## 멀티스테이지 빌드

Dockerfile은 두 단계로 나뉜다.

**Stage 1 — builder (빌드 전용)**
```
golang:1.22-alpine  약 300MB
Go 컴파일러 + 소스코드 + 캐시 포함
→ CGO_ENABLED=0 GOOS=linux go build -o server .
```

**Stage 2 — final (실행 전용)**
```
alpine:3.19  약 7MB
바이너리(server) 하나만 복사
→ 최종 이미지 약 10MB
```

Stage 1은 최종 이미지에 포함되지 않는다. Go 컴파일러, 소스코드, 빌드 캐시 등 실행에 불필요한 모든 것이 제거되어 이미지 크기가 ~300MB → ~10MB로 줄어든다. 이미지가 작을수록 레지스트리 push/pull 속도, 컨테이너 시작 시간, 보안 공격 표면이 모두 개선된다.

`CGO_ENABLED=0`은 C 라이브러리 의존성을 완전히 제거하여 정적 바이너리를 생성한다. alpine에는 일반 리눅스의 glibc가 없기 때문에 C 의존성이 있는 동적 바이너리는 alpine에서 실행 시 에러가 난다. 정적 바이너리는 필요한 모든 코드가 바이너리 안에 포함되어 어떤 환경에서도 실행된다.

**레이어 캐시 최적화**

```dockerfile
COPY go.mod ./          # 의존성 정의만 먼저 복사
RUN go mod download     # 의존성 다운로드 → 캐시 레이어 생성
COPY . .                # 소스 복사 (자주 바뀜)
RUN go build ...
```

`go.mod`를 소스보다 먼저 복사하는 이유는 Docker 레이어 캐시를 활용하기 위해서다. `go.mod`가 변경되지 않으면 `go mod download` 레이어는 캐시히트하여 의존성 재다운로드를 생략한다. `main.go`만 수정했을 때 빌드 시간이 수십 초 단축된다.

---

## 보안 스캔 (Trivy)

`deploy.sh`는 이미지 빌드 직후 Trivy로 취약점을 자동 스캔하고, 결과를 JSON 파일과 터미널 두 곳에 동시에 출력한다.

```bash
# JSON 파일로 저장 (커밋 해시 + 날짜 조합으로 고유 파일명 생성)
trivy image --exit-code 0 --severity HIGH,CRITICAL --format json \
  --output "trivy-reports/${IMAGE}-${TAG}-$(date +%Y%m%d).json" "$IMAGE:$TAG"

# 터미널에 표(table) 형식으로 동시 출력
trivy image --exit-code 0 --severity HIGH,CRITICAL "$IMAGE:$TAG"
```

스캔 결과 파일: `trivy-reports/pf2-6750b6c-20260621.json`

---

### 스캔 결과 요약 (2026-06-21, pf2:6750b6c)

| 대상 | CRITICAL | HIGH | 비고 |
|------|----------|------|------|
| alpine 3.19.9 (OS 패키지) | 0 | 2 | musl/musl-utils, EOSL 버전 |
| app/server (Go stdlib 1.22.12) | 1 | 14 | 전부 fixed 상태, 버전 업으로 해결 가능 |
| **합계** | **1** | **16** | |

> **EOSL 경고**: alpine 3.19.9는 End of Service Life(공식 지원 종료) 버전이다. 보안 업데이트가 더 이상 제공되지 않으므로 alpine:3.20 이상으로 업그레이드가 필요하다.

---

### Alpine OS 취약점 (2건 HIGH)

#### CVE-2026-40200 — musl, musl-utils
| 항목 | 내용 |
|------|------|
| 심각도 | HIGH (CVSS 7.8) |
| 영향 패키지 | musl 1.2.4_git20230717-r5, musl-utils 1.2.4_git20230717-r5 |
| 수정 버전 | 1.2.4_git20230717-r6 |
| 상태 | fixed (패치 존재) |
| CWE | CWE-670 (Always-Incorrect Control Flow Implementation) |
| 공개일 | 2026-04-10 |

**취약점 설명**: musl libc의 `qsort` 함수에서 스택 기반 메모리 손상이 발생한다. 정렬 대상 배열의 원소 수가 약 700만 개를 초과할 때 double-word 연산이 잘못 구현되어 스택 메모리가 손상된다. 이를 통해 임의 코드 실행(Arbitrary Code Execution)과 서비스 거부(DoS)가 가능하다.

**해결 방법**: Dockerfile에서 `FROM alpine:3.19` → `FROM alpine:3.20` 이상으로 업그레이드.

---

### Go stdlib 취약점 (15건: CRITICAL 1, HIGH 14)

모든 취약점의 영향 패키지는 `stdlib@1.22.12`이다. Go 버전을 올리면 일괄 해결된다.

#### CVE-2025-68121 — CRITICAL (CVSS 10.0)
| 항목 | 내용 |
|------|------|
| 패키지 | crypto/tls |
| 수정 버전 | 1.24.13, 1.25.7, 1.26.0-rc.3 |
| CWE | CWE-295 (Improper Certificate Validation) |
| 공개일 | 2026-02-05 |

**취약점 설명**: TLS 세션 재개(session resumption) 중 인증서 검증이 잘못 수행된다. `Config.Clone` 후 `ClientCAs` 또는 `RootCAs`를 변경하거나 `GetConfigForClient`를 사용하는 경우, 재개된 핸드셰이크가 실패해야 할 때도 성공할 수 있다. 클라이언트가 원래라면 연결하지 않았을 서버와 세션을 재개하거나, 서버가 검증 실패해야 할 클라이언트와 세션을 재개할 수 있다. CVSS 10.0(최고점)으로 실무에서는 즉시 패치 대상이다.

---

#### CVE-2025-61726 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | net/url |
| 수정 버전 | 1.24.12, 1.25.6 |
| CWE | CWE-770 (Allocation of Resources Without Limits) |

**취약점 설명**: `net/url` 패키지가 쿼리 파라미터 수에 제한을 두지 않는다. `http.Request.ParseForm`으로 수많은 고유 파라미터를 포함한 대용량 폼을 파싱할 때 과도한 메모리를 소비하여 DoS를 유발할 수 있다.

---

#### CVE-2025-61729 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | crypto/x509 |
| 수정 버전 | 1.24.11, 1.25.5 |
| CWE | CWE-295 |

**취약점 설명**: `HostnameError.Error()`가 에러 문자열을 구성할 때 출력할 호스트 수에 제한이 없고, 문자열을 반복 연결(quadratic runtime)하여 구성한다. 악의적으로 조작된 인증서로 과도한 CPU·메모리를 소비시킬 수 있다.

---

#### CVE-2026-25679 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | net/url |
| 수정 버전 | 1.25.8, 1.26.1 |
| CWE | CWE-425 (Direct Request / Forced Browsing) |

**취약점 설명**: `url.Parse`가 호스트/authority 컴포넌트의 IPv6 리터럴을 잘못 파싱하여 일부 유효하지 않은 URL을 허용한다.

---

#### CVE-2026-32280 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | crypto/x509, crypto/tls |
| 수정 버전 | 1.25.9, 1.26.2 |
| CWE | CWE-770 |

**취약점 설명**: 인증서 체인 구성(chain building) 중 `VerifyOptions.Intermediates`에 다수의 중간 인증서가 전달되면 작업량이 올바르게 제한되지 않아 DoS를 유발한다. `crypto/x509`와 `crypto/tls` 직접 사용자 모두 영향을 받는다.

---

#### CVE-2026-32281 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | crypto/x509 |
| 수정 버전 | 1.25.9, 1.26.2 |
| CWE | CWE-295 |

**취약점 설명**: 정책 매핑이 매우 많은 인증서가 포함된 체인의 정책 검증이 비효율적으로 처리되어 DoS를 유발한다. 신뢰된 루트 CA가 발급한 체인에서만 영향을 받는다.

---

#### CVE-2026-32283 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | crypto/tls |
| 수정 버전 | 1.25.9, 1.26.2 |
| CWE | CWE-770 |

**취약점 설명**: TLS 연결의 한 쪽이 핸드셰이크 이후 단일 레코드에 여러 개의 키 업데이트 메시지를 전송하면 연결이 데드락 상태에 빠져 리소스를 무제한으로 소비한다. TLS 1.3에서만 영향을 받는다.

---

#### CVE-2026-33811 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | net |
| 수정 버전 | 1.25.10, 1.26.3 |
| CWE | CWE-415 (Double Free) |

**취약점 설명**: cgo DNS 리졸버로 `LookupCNAME`을 사용할 때, 매우 긴 CNAME 응답이 C 메모리의 double-free와 크래시를 유발한다.

---

#### CVE-2026-33814 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | net/http (HTTP/2 transport) |
| 수정 버전 | 1.25.10, 1.26.3 |
| CWE | CWE-835 (Loop with Unreachable Exit Condition) |

**취약점 설명**: HTTP/2 SETTINGS 프레임 처리 시 `SETTINGS_MAX_FRAME_SIZE` 값이 0이면 transport가 CONTINUATION 프레임을 무한 루프로 기록하여 응답 불능 상태가 된다.

---

#### CVE-2026-39820 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | net/mail |
| 수정 버전 | 1.25.10, 1.26.3 |
| CWE | CWE-770 |

**취약점 설명**: `ParseAddress`, `ParseAddressList`, `ParseDate`에 조작된 입력이 전달되면 과도한 CPU 소비와 메모리 할당이 발생하여 DoS를 유발한다.

---

#### CVE-2026-39823 — HIGH
| 항목 | 내용 |
|------|------|
| 패키지 | html/template |
| 수정 버전 | 1.25.10, 1.26.3 |
| CWE | CWE-79 (XSS) |

**취약점 설명**: `<meta>` 태그의 `content` 속성 안에 URL을 삽입할 때, `=` 기호 주변에 ASCII 공백이 있으면 이스케이프가 제대로 처리되지 않아 XSS(Cross-Site Scripting)가 가능하다.

---

#### CVE-2026-39825 — HIGH
| 항목 | 내용 |
|------|------|
| 패키지 | net/http (ReverseProxy) |
| 수정 버전 | 1.25.10, 1.26.3 |

**취약점 설명**: `ReverseProxy`가 `Rewrite` 함수나 `Director` 함수에 보이지 않는 쿼리 파라미터를 포함한 요청을 전달할 수 있다. `urlmaxqueryparams` 제한을 고려하지 않아 파라미터가 숨겨진 채로 백엔드에 전달된다.

---

#### CVE-2026-39836 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | net |
| 수정 버전 | 1.25.10, 1.26.3 |
| CWE | CWE-476 (NULL Pointer Dereference) |

**취약점 설명**: `Dial`과 `LookupPort` 함수가 Windows에서 NUL(0) 문자를 포함한 입력을 받으면 패닉이 발생한다.

---

#### CVE-2026-42499 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | net/mail |
| 수정 버전 | 1.25.10, 1.26.3 |

**취약점 설명**: RFC 5322 이메일 주소 파싱 중 `consumePhrase`에 조작된 입력이 전달되면 DoS가 발생한다.

---

#### CVE-2026-42504 — HIGH (CVSS 7.5)
| 항목 | 내용 |
|------|------|
| 패키지 | mime |
| 수정 버전 | 1.25.11, 1.26.4 |
| CWE | CWE-407 (Inefficient Algorithmic Complexity) |
| 공개일 | 2026-06-02 (가장 최근) |

**취약점 설명**: 유효하지 않은 인코딩된 단어가 다수 포함된 악의적으로 조작된 MIME 헤더를 디코딩할 때 과도한 CPU를 소비한다.

---

### 취약점 조치 계획

| 조치 | 해결 CVE | 방법 |
|------|----------|------|
| alpine 3.20 이상으로 업그레이드 | CVE-2026-40200 (2건) | `FROM alpine:3.20` |
| Go 1.26.4 이상으로 업그레이드 | stdlib 취약점 전체 (15건) | `FROM golang:1.26-alpine` |
| 프로덕션 배포 차단 설정 | CRITICAL 발견 시 배포 중단 | `--exit-code 1` |

> **현재 `--exit-code 0` 설정 이유**: 포트폴리오 실습 환경이므로 경고만 출력하고 배포를 계속 진행한다. 프로덕션에서는 `--exit-code 1`로 설정하여 CRITICAL 발견 시 파이프라인을 즉시 중단시킨다.

---

## 실행 방법

### 사전 요구사항

- Docker, Docker Compose
- Go 1.22 이상
- Trivy
- git

### 1. Go 서버 직접 실행 (Docker 없이)

```bash
go run main.go
curl http://localhost:8080/health
curl http://localhost:8080/metrics
```

### 2. Docker 단독 실행

```bash
docker build -t pf2:test .
docker run -p 8080:8080 pf2:test
curl http://localhost:8080/health
```

### 3. docker-compose로 nginx 포함 전체 실행

```bash
docker compose up -d
curl http://localhost/health    # 포트 80 — nginx 통과 확인
```

### 4. 배포 자동화 스크립트 실행

```bash
./deploy.sh
```

스크립트는 다음 순서로 실행된다.

```
1. docker build        — 현재 커밋 해시를 태그로 이미지 빌드
2. trivy image (JSON)  — HIGH·CRITICAL 취약점 스캔, trivy-reports/ 에 저장
3. trivy image (table) — 터미널에 동일 결과를 표 형식으로 출력
4. docker compose down — 기존 컨테이너 전체 종료 및 제거
5. docker compose up   — 새 이미지로 컨테이너 재시작
6. curl /health        — 헬스체크 통과 확인 → "Deploy OK"
```

---

## 이미지 태그 전략

```bash
TAG=$(git rev-parse --short HEAD)   # 예: 6750b6c
docker build -t pf2:$TAG .
```

`latest` 태그 대신 커밋 해시를 태그로 사용한다. 이 이미지가 어떤 코드로 만들어졌는지 `git log`로 즉시 추적 가능하며, 문제 발생 시 이전 커밋의 이미지로 롤백하는 것도 가능하다. 이 패턴은 GitOps의 기본 원칙(코드와 배포 상태의 1:1 추적)과 일치한다.

Trivy 스캔 결과 파일도 동일한 커밋 해시를 포함하여 `pf2-6750b6c-20260621.json` 형태로 저장되므로, 이미지·코드·보안 스캔 결과를 하나의 커밋으로 묶어 추적할 수 있다.

---

## 면접 포인트 요약

| 질문 | 핵심 답변 |
|------|-----------|
| 왜 멀티스테이지 빌드를 썼나요? | 컴파일러·소스를 최종 이미지에서 제거해 ~300MB → ~10MB 축소. 공격 표면 최소화. |
| 왜 Go 서버를 직접 외부에 노출하지 않았나요? | nginx를 앞단에 두어 SSL 종료·접근 로그·로드밸런싱을 일괄 처리하고 보안 레이어를 분리 |
| Trivy 스캔에서 취약점이 나왔는데 어떻게 할 건가요? | alpine과 Go 버전을 최신으로 올리면 17건 전부 해결 가능. 프로덕션에서는 --exit-code 1로 CRITICAL 발견 시 배포 차단 |
| 스캔 결과를 파일로 저장하는 이유는? | 커밋 해시·날짜 조합으로 배포 이력별 보안 상태를 추적하고, CI/CD에서 아티팩트로 업로드하거나 PR 코멘트로 자동 첨부 가능 |
| `set -e`를 왜 넣었나요? | 중간 단계 실패 시 즉시 종료. 빌드 실패한 이미지가 배포되는 사고 방지 |
| 이미지 태그를 커밋 해시로 쓰는 이유는? | 배포 이미지와 소스코드를 1:1 추적 가능. 롤백 시 정확한 버전 특정 가능. GitOps 원칙과 일치 |
| CGO_ENABLED=0이 뭔가요? | C 라이브러리 의존성 제거. alpine처럼 glibc 없는 환경에서도 실행 가능한 정적 바이너리 생성 |
