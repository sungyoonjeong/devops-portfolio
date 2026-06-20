# DevOps 기술면접 완전정복 — 신입 면접 마스터 가이드

> 작성: 2026-06-20 · 대상: DevOps 엔지니어 신입 면접 (9월 공채)  
> 원칙: 질문 보고 **2분 이내 소리내어 답한다**. 면접은 글이 아니라 말이다.  
> 답변 구조: **① 정의(한 줄) → ② 동작 원리 → ③ 실무/포트폴리오 연결**

---

## 이 자료 쓰는 법

적지 말고 **입으로** 답한다. 아래 모범답안은 키워드 뼈대다 — 통째로 외우지 말고 이 뼈대를 살로 붙여 내 말로 만든다. 면접관은 "이 사람 실제로 써봤나"를 보기 때문에, 반드시 내 포트폴리오(PF1~PF3)와 연결해서 끝내야 한다.

녹음 → 다시 듣기로 말버릇·시간초과·횡설수설을 체크한다. 막힌 건 ★ 달고 3일 후 재도전.

---

# 1. OS / Linux

## 1-1. 프로세스 vs 스레드 vs 컨텍스트 스위칭

### 핵심 개념

**프로세스**는 실행 중인 프로그램 인스턴스다. 운영체제가 각 프로세스에 독립된 메모리 공간(코드·데이터·힙·스택)과 PCB(Process Control Block)를 할당한다. 프로세스끼리는 메모리를 공유하지 않아 하나가 죽어도 다른 프로세스에 영향이 없다(고립성).

**스레드**는 프로세스 내의 실행 흐름 단위다. 같은 프로세스 안의 스레드들은 코드·데이터·힙을 공유하고, 스택만 각자 따로 갖는다. 공유 덕분에 스레드 간 통신은 빠르지만, 동기화를 잘못 하면 경쟁 조건(Race Condition)이나 데드락이 생긴다.

```
프로세스 A                    프로세스 B
┌─────────────────┐          ┌─────────────────┐
│  코드 (공유)     │          │  코드 (공유)     │
│  데이터 (공유)   │          │  데이터 (공유)   │
│  힙 (공유)      │          │  힙 (공유)      │
│  ┌───┐  ┌───┐  │          │  스택           │
│  │스택│  │스택│  │          │  (스레드 1개)   │
│  │T1 │  │T2 │  │          └─────────────────┘
│  └───┘  └───┘  │
│  (멀티스레드)    │
└─────────────────┘
   메모리 완전 분리 ←→ 격리됨
```

**컨텍스트 스위칭**은 CPU가 실행 중인 작업(프로세스 or 스레드)을 바꿀 때, 현재 상태(레지스터·PC·메모리 맵 등)를 PCB에 저장하고 다음 작업의 상태를 복원하는 과정이다. 이 과정 자체가 오버헤드다. 프로세스 전환은 메모리 맵 교체·캐시 무효화(TLB flush)까지 동반해서 스레드 전환보다 훨씬 비싸다.

### 면접 2분 답변 뼈대

"프로세스는 독립된 메모리 공간을 갖는 실행 단위고, 스레드는 프로세스 내에서 메모리를 공유하는 실행 흐름입니다. 프로세스는 격리성이 강해 안전하지만 무겁고, 스레드는 공유 덕분에 빠르지만 동기화가 필요합니다. 컨텍스트 스위칭은 CPU가 작업을 전환할 때 레지스터·PC 등 현재 상태를 저장하고 다음 상태를 복원하는 과정인데, 프로세스 전환이 스레드보다 비쌉니다. Docker 컨테이너가 결국 namespace와 cgroups로 격리된 프로세스라는 사실이 이 개념과 연결됩니다."

### 심화 — 사용자 모드 vs 커널 모드

CPU는 두 가지 모드로 동작한다. **사용자 모드**는 응용 프로그램이 실행되는 제한된 권한 공간이고, **커널 모드**는 OS가 하드웨어에 직접 접근할 수 있는 특권 공간이다. 응용 프로그램이 파일을 읽거나 소켓을 열 때는 시스템 콜(syscall)을 통해 커널 모드로 진입한다. `strace`가 이 시스템콜을 추적하는 도구다.

---

## 1-2. 데드락 (Deadlock)

### 발생 4조건 (전부 동시 성립해야 발생)

| 조건 | 설명 |
|------|------|
| ① 상호배제 | 자원은 한 번에 하나만 점유 가능 |
| ② 점유와 대기 | 자원을 들고 있으면서 다른 자원을 기다림 |
| ③ 비선점 | 다른 프로세스가 들고 있는 자원을 강제로 빼앗을 수 없음 |
| ④ 순환대기 | A→B→C→A 식으로 자원 요청이 원형 고리를 이룸 |

### 해결 전략

- **예방(Prevention):** 4조건 중 하나를 애초에 깬다. 예: 락 획득 순서를 항상 동일하게 강제하면 순환대기가 불가능해진다.
- **회피(Avoidance):** 은행원 알고리즘처럼 할당 전에 안전 상태인지 검사 후 허용.
- **탐지 후 복구(Detection & Recovery):** 주기적으로 자원 할당 그래프를 검사, 데드락 탐지 시 프로세스 중단 또는 자원 강제 회수.

### 면접 2분 답변 뼈대

"데드락은 상호배제·점유와 대기·비선점·순환대기 4조건이 동시에 성립할 때 발생합니다. 가장 실용적인 예방 방법은 락 획득 순서를 코드 전체에서 일관되게 고정하는 겁니다. 그러면 순환대기가 구조적으로 불가능해집니다."

---

## 1-3. 가상 메모리 / 페이징

**가상 메모리**는 물리 메모리(RAM)보다 큰 주소 공간을 프로세스에게 제공하기 위해, 페이지 단위로 디스크(스왑)와 실제 메모리 사이를 교환하는 기법이다.

핵심 용어:
- **페이지 폴트**: 접근한 주소가 현재 RAM에 없어 디스크에서 불러와야 할 때 발생. 비싼 연산이다.
- **TLB(Translation Lookaside Buffer)**: 가상→물리 주소 변환 캐시. TLB 히트면 빠르고, 미스면 페이지 테이블 탐색 필요.
- **Thrashing**: 스왑이 너무 잦아 CPU가 페이지 폴트 처리에만 매달려 실제 작업을 못 하는 상태. `vmstat 1`로 `si/so`(swap in/out) 값이 높으면 징조다.

---

## 1-4. Linux 실전 트러블슈팅 ⭐ (면접 최빈출)

DevOps 면접에서 가장 많이 물어보는 구간이다. "이론만 아는 사람"과 "실제로 진단해 본 사람"을 여기서 가른다. 명령어를 외우는 게 아니라 **왜 이 순서인지** 설명할 수 있어야 한다.

### Q. 서버 CPU 100%일 때 어떻게 진단하나요? (단골 중 단골)

면접관이 기대하는 답은 **순서가 있는 루틴**이다. 추측부터 하면 감점.

```
Step 1: top / htop
  → CPU 점유 상위 프로세스, PID 확인
  → "%us" (사용자 모드) vs "%sy" (커널 모드) 비율 확인
     - %us 높음 → 앱 코드 문제 (무한루프, GC 폭증)
     - %sy 높음 → 시스템콜 폭증 (I/O, 소켓)

Step 2: top -H -p <PID>
  → 해당 프로세스 내 어느 스레드가 CPU를 잡아먹는지

Step 3: strace -p <PID>
  → 실시간 시스템콜 추적
  → 같은 syscall이 반복 → 무한루프 또는 재시도 폭발
  → read/write 블로킹 → I/O 대기

Step 4: ss -tulnp (소켓·연결 상태)
  → ESTABLISHED 수 폭증 → 연결 폭주 or 커넥션 풀 고갈
  → CLOSE_WAIT 다수 → 클라이언트가 FIN을 보냈는데 서버가 소켓을 안 닫음

Step 5: lsof -p <PID>
  → 열린 파일·소켓 목록 → 파일 디스크립터 누수 확인

Step 6: /proc/<PID>/status, vmstat 1 5
  → VmRSS(실제 메모리), VmSwap(스왑 사용)
  → vmstat: "wa"(CPU I/O 대기), "si/so"(스왑)

Step 7: 원인 결론 → 조치
  → 앱 무한루프  : 해당 스레드 종료 or 앱 재기동 후 코드 수정
  → GC 폭증     : JVM 힙 튜닝, 메모리 누수 확인
  → I/O 대기    : 디스크/DB 병목 → iostat, slow query log
  → 트래픽 폭주  : 로드밸런서 스케일아웃, Rate Limit 적용
```

**면접 답변 뼈대:** "먼저 `top`으로 CPU를 잡아먹는 PID를 찾고, `top -H`로 스레드 레벨까지 좁힙니다. `strace`로 어떤 시스템콜이 반복되는지 보면 무한루프인지 I/O 대기인지 구분되고, `ss`로 소켓 상태까지 확인해서 원인을 특정합니다. PF2 Go 서버에서 실제로 이 루틴을 써봤습니다."

---

### Q. 디스크가 꽉 찼다 / I/O가 느리다

```bash
# 디스크 용량 확인
df -h                         # 어느 파티션이 꽉 찼나
du -sh /var/log/*             # 범인 디렉터리 (로그가 대부분)
du -ah / | sort -rh | head -20  # 용량 큰 파일 상위 20개

# I/O 병목
iostat -x 1                   # %util이 100% 근처면 디스크 포화
                              # await(ms): 요청 대기 시간 높으면 병목
iotop                         # 어느 프로세스가 I/O를 쓰는지

# 조치
# 로그 로테이션 설정 (logrotate)
# 불필요한 코어덤프 제거 (rm /var/core/*)
# 볼륨 추가 or EBS 확장
```

---

### Q. 포트가 이미 사용 중 / 충돌

```bash
ss -tulnp | grep :8080        # 포트 8080 점유 프로세스 확인
lsof -i :8080                 # 동일한 확인 (파일 기반)
kill -9 <PID>                 # 강제 종료 (SIGKILL)
# 재기동 후 다시 ss로 확인
```

`netstat`보다 `ss`가 더 빠르고 현대적인 도구다. 면접에서 `ss`를 쓰면 최신 실무 감각을 어필할 수 있다.

---

### Q. 메모리가 부족하다 (OOM)

```bash
free -h                       # 전체 메모리·스왑 현황
cat /var/log/syslog | grep OOM  # OOM Killer 발동 흔적
dmesg | grep -i "out of memory"

# OOM Killer가 프로세스를 강제 종료했을 때:
# → /proc/<PID>/oom_score 확인 (높을수록 먼저 킬됨)
# 조치: 메모리 누수 앱 수정, 스왑 추가, 인스턴스 업스케일
```

---

# 2. 네트워크 (CCNP 자신감 구간 — 깊이 있게 답해야)

## 2-1. TCP 3-way Handshake

```
클라이언트                          서버
    │                               │
    │──── SYN (seq=x) ─────────────►│   연결 요청
    │                               │
    │◄─── SYN-ACK (seq=y, ack=x+1) ─│   수락 + 서버 시퀀스 동기화
    │                               │
    │──── ACK (ack=y+1) ────────────►│   확인
    │                               │
    │           데이터 전송          │
```

**왜 3번인가:** 양방향 시퀀스 번호를 서로 확인하기 위해. 2번이면 서버→클라이언트 방향 확인이 안 된다.

**종료는 4-way (FIN/ACK × 2):** FIN → ACK → FIN → ACK. TIME_WAIT 상태가 한동안 유지되는 이유는 마지막 ACK가 소실됐을 때 재전송할 수 있도록 대기하는 것.

**면접 답변 뼈대:** "TCP는 신뢰성 있는 연결을 위해 3-way handshake를 합니다. 클라이언트가 SYN을 보내 연결 의사를 밝히고, 서버가 SYN-ACK로 수락하며 자신의 시퀀스 번호를 알립니다. 클라이언트가 ACK로 확인하면 연결이 확립됩니다. 3번인 이유는 양방향 시퀀스를 서로 확인해야 하기 때문입니다. L4 로드밸런서가 이 TCP 레벨에서 분배 결정을 내립니다."

---

## 2-2. HTTP vs HTTPS (TLS)

### HTTP/1.1 vs HTTP/2 vs HTTP/3

| 버전 | 특징 |
|------|------|
| HTTP/1.1 | 요청 하나씩 순서대로 (HOL Blocking). Keep-Alive로 연결 재사용 |
| HTTP/2 | 멀티플렉싱 — 하나의 TCP 연결에서 여러 요청 병렬 처리. 헤더 압축(HPACK). 서버 푸시. |
| HTTP/3 | TCP → UDP 기반 QUIC으로 교체. 연결 설정 지연(RTT) 감소. 패킷 손실에 강함. |

### HTTPS = HTTP + TLS

```
TLS 핸드셰이크 순서:
1. ClientHello (지원하는 암호 스위트 목록)
2. ServerHello + 인증서 전송
3. 클라이언트 → 인증서 검증 (CA 체인)
4. 세션키 교환 (RSA or ECDHE)
5. 이후 대칭키(AES 등)로 암호화 통신
```

TLS 1.3부터는 핸드셰이크가 1-RTT로 줄었다(이전 1.2는 2-RTT).

**면접 답변 뼈대:** "HTTPS는 HTTP에 TLS 암호화를 더한 것입니다. 클라이언트와 서버가 TLS 핸드셰이크로 서버 인증서를 검증하고 세션키를 교환한 뒤, 이후 통신은 대칭키로 암호화합니다. 기밀성·무결성·인증 세 가지를 보장합니다."

---

## 2-3. DNS 동작 원리

```
브라우저에 www.example.com 입력

1. 브라우저 캐시 확인 → 없으면
2. OS /etc/hosts 확인 → 없으면
3. 로컬 DNS 리졸버(통신사 or 8.8.8.8) 질의
4. 리졸버 → 루트 네임서버 (.com을 누가 아는가?)
5. 루트 → TLD 네임서버(.com 담당) 주소 응답
6. 리졸버 → TLD 네임서버 질의
7. TLD → example.com의 authoritative 네임서버 주소 응답
8. 리졸버 → authoritative 질의 → IP 응답
9. 리졸버가 TTL 동안 캐싱 후 브라우저에 응답
```

**연결:** "AWS Route53은 authoritative DNS 역할을 합니다. 가중치·지연·장애조치 라우팅 정책은 이 IP 응답 단계에서 동작합니다."

---

## 2-4. 로드밸런서 L4 vs L7

```
                     ┌─────────────────┐
클라이언트 ──────────►│   Load Balancer  │──────────► 서버들
                     └─────────────────┘
                       L4: IP:Port 기반
                       L7: URL/Header 기반
```

| 항목 | L4 (Transport) | L7 (Application) |
|------|----------------|------------------|
| 판단 기준 | IP 주소 + Port | HTTP URL·헤더·쿠키·메서드 |
| 속도 | 빠름 (패킷 내용 안 봄) | 상대적으로 느림 (패킷 파싱) |
| 기능 | 단순 분배 | URL 기반 라우팅, SSL 종료, WAF |
| AWS 예시 | NLB | ALB |
| 예시 | TCP 80→서버 분배 | `/api`→A서버, `/static`→B서버 |

**면접 답변 뼈대:** "L4는 IP와 포트만 보고 분배해서 빠르지만 HTTP 내용을 모릅니다. L7은 HTTP URL·헤더까지 보기 때문에 `/api`는 API 서버로, `/static`은 CDN으로 보내는 세밀한 라우팅이 가능합니다. AWS에서 ALB가 L7이고 NLB가 L4입니다. K8s Ingress도 L7 로드밸런싱입니다."

---

## 2-5. NAT와 VPC 서브넷 설계

**왜 Public/Private 서브넷을 나누는가**

```
인터넷
    │
    ▼
인터넷 게이트웨이 (IGW)
    │
    ▼
┌─────────────────────────────────────┐
│  VPC (10.0.0.0/16)                  │
│                                     │
│  Public Subnet (10.0.1.0/24)        │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  ALB (L7)   │  │ NAT Gateway  │  │
│  └──────┬──────┘  └──────┬───────┘  │
│         │                │아웃바운드  │
│  Private Subnet (10.0.2.0/24)       │
│  ┌─────────────┐  ┌──────────────┐  │
│  │  EC2 (앱)   │  │  RDS (DB)    │  │
│  └─────────────┘  └──────────────┘  │
│   인터넷에서 직접 접근 불가           │
└─────────────────────────────────────┘
```

DB와 내부 서버는 인터넷에 직접 노출하지 않는다. Private 서브넷의 EC2가 패키지 설치 등 외부 통신이 필요할 때는 NAT Gateway를 거쳐 단방향 아웃바운드만 허용한다.

**보안그룹 vs NACL**

| 항목 | 보안그룹 (Security Group) | NACL |
|------|--------------------------|------|
| 상태 | Stateful (응답 자동 허용) | Stateless (인/아웃 각각 설정) |
| 적용 | 인스턴스 레벨 | 서브넷 레벨 |
| 규칙 | 허용만 (거부 없음) | 허용·거부 모두 |

---

# 3. Docker

## 3-1. 컨테이너 vs VM

```
VM 구조                         컨테이너 구조
┌──────────┐  ┌──────────┐     ┌──────────┐  ┌──────────┐
│ App A    │  │ App B    │     │ App A    │  │ App B    │
│ Guest OS │  │ Guest OS │     │          │  │          │
│ (Linux)  │  │(Windows) │     └────┬─────┘  └────┬─────┘
├──────────┴──┴──────────┤          │              │
│     Hypervisor          │     ┌────▼──────────────▼──┐
├─────────────────────────┤     │  컨테이너 런타임(Docker) │
│     Host OS             │     ├──────────────────────┤
├─────────────────────────┤     │       Host OS        │
│     Hardware            │     ├──────────────────────┤
└─────────────────────────┘     │      Hardware        │
                                └──────────────────────┘
부팅: 수십 초                    부팅: 밀리초 단위
크기: GB                        크기: MB~수백MB
격리: 강함 (OS 레벨)             격리: 약함 (커널 공유)
                                (namespace + cgroups)
```

**컨테이너의 격리 원리:**
- **namespace**: 각 컨테이너에게 독립된 PID, 네트워크, 파일시스템, 사용자 공간처럼 보이게 한다.
- **cgroups (control groups)**: CPU, 메모리, 디스크 I/O 등 자원 사용량을 제한한다.

---

## 3-2. Docker 이미지 레이어 구조

```
       ┌───────────────────────────────┐
       │  컨테이너 레이어 (R/W)         │  ← 실행 중 변경사항 (임시)
       ├───────────────────────────────┤
       │  레이어 4: COPY app .         │  ← 읽기 전용
       │  레이어 3: RUN pip install    │  ← 읽기 전용
       │  레이어 2: COPY requirements  │  ← 읽기 전용
       │  레이어 1: FROM python:3.11   │  ← 읽기 전용 (베이스)
       └───────────────────────────────┘
```

Union FS가 이 레이어들을 합쳐서 하나의 파일시스템처럼 보여준다.

**레이어 캐시 최적화 — Dockerfile 작성 순서가 중요하다**

자주 바뀌는 내용일수록 뒤에 위치해야 캐시를 최대한 재사용한다:

```dockerfile
# 나쁜 예 — app 코드가 바뀔 때마다 pip install이 재실행됨
FROM python:3.11-slim
COPY . .
RUN pip install -r requirements.txt

# 좋은 예 — requirements.txt 안 바뀌면 pip install 레이어 캐시 재사용
FROM python:3.11-slim
COPY requirements.txt .        # ← 거의 안 바뀜
RUN pip install -r requirements.txt
COPY . .                       # ← 자주 바뀜 (뒤로)
```

---

## 3-3. 멀티스테이지 빌드 (면접 어필 포인트)

```dockerfile
# Stage 1: 빌드 환경 (컴파일러·도구 전부 포함)
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o server .

# Stage 2: 실행 환경 (빌드 도구 없이 바이너리만)
FROM alpine:3.19
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]
```

빌드 도구(Go 컴파일러 등)는 최종 이미지에 포함되지 않아 이미지 크기가 극적으로 줄어든다. PF2에서 실제로 적용했다.

---

## 3-4. Docker Compose와 볼륨

**Docker Compose**: 여러 컨테이너를 하나의 YAML로 정의하고 `docker compose up`으로 한 번에 실행한다. PF2의 app + nginx 구성이 여기 해당.

**볼륨**: 컨테이너가 죽어도 데이터가 살아있게 호스트 디렉터리 or Docker 볼륨에 마운트한다. DB 데이터는 반드시 볼륨으로 분리해야 한다.

---

## 3-5. Trivy 보안 스캔

```bash
# 이미지 취약점 스캔
trivy image myapp:latest

# CI/CD 파이프라인에서:
# CRITICAL 취약점 발견 시 빌드 실패 처리
trivy image --exit-code 1 --severity CRITICAL myapp:latest
```

**면접 답변:** "빌드 직후 Trivy로 이미지를 스캔해서 CRITICAL 취약점이 있으면 파이프라인을 실패시켰습니다. 스캔 결과는 README에 첨부해서 면접관이 바로 볼 수 있게 했습니다."

---

# 4. Kubernetes

## 4-1. K8s 아키텍처 (전체 그림)

```
┌─────────────────────── Control Plane ───────────────────────┐
│                                                              │
│  API Server ── etcd (상태 저장소)                            │
│      │                                                       │
│  Scheduler (Pod 배치 결정)  Controller Manager (자가복구)     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
          │ kubectl 명령 / 상태 조회
┌─────────▼──────────────────── Worker Node ──────────────────┐
│                                                              │
│  kubelet (Pod 상태 유지)   kube-proxy (네트워크 규칙)         │
│                                                              │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │    Pod     │  │    Pod     │  │    Pod     │             │
│  │ Container  │  │ Container  │  │ Container  │             │
│  └────────────┘  └────────────┘  └────────────┘             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**각 컴포넌트 역할:**
- **API Server**: 모든 K8s 명령의 진입점. `kubectl`이 여기로 요청을 보낸다.
- **etcd**: 클러스터 전체 상태(Pod 수·설정·시크릿 등)를 저장하는 분산 키-값 저장소. 이게 죽으면 클러스터 전체가 마비된다.
- **Scheduler**: 새 Pod을 어느 노드에 배치할지 결정한다(리소스·어피니티 고려).
- **Controller Manager**: "선언된 상태 = 실제 상태"를 유지한다. ReplicaSet이 Pod 3개를 선언했는데 하나가 죽으면 새로 만든다.
- **kubelet**: 각 노드에서 실행되며, API Server 지시를 받아 컨테이너를 기동·종료한다.

---

## 4-2. Pod가 죽으면 어떻게 되나요?

```
Pod 죽음 감지 (kubelet이 보고)
    │
    ▼
ReplicaSet Controller 감지
(현재 실행 수 < 선언된 수)
    │
    ▼
새 Pod 생성 요청 → Scheduler가 노드 배치
    │
    ▼
해당 노드의 kubelet이 컨테이너 기동
    │
    ▼
readinessProbe 통과 시 Service 엔드포인트에 추가
```

핵심은 **ReplicaSet이 자가복구를 담당**한다는 것. Pod 자체는 복구 능력이 없고, ReplicaSet(또는 Deployment)이 선언된 복제본 수를 유지한다.

**면접 답변 뼈대:** "Pod가 죽으면 kubelet이 감지해서 API Server에 보고하고, ReplicaSet Controller가 선언된 복제본 수와 현재 수의 차이를 발견해 새 Pod를 생성합니다. Scheduler가 노드를 배치하고, readinessProbe를 통과해야 Service 엔드포인트에 추가되어 트래픽을 받습니다."

---

## 4-3. Service 종류와 차이

| 타입 | 접근 범위 | 사용 상황 |
|------|-----------|-----------|
| **ClusterIP** | 클러스터 내부만 | 마이크로서비스 간 통신. 기본값. |
| **NodePort** | 노드의 IP:포트로 외부 접근 | 테스트·개발용. 30000~32767 포트. |
| **LoadBalancer** | 클라우드 LB를 생성해 외부 노출 | 프로덕션 외부 노출. AWS NLB/ALB 자동 생성. |
| **ExternalName** | DNS CNAME으로 외부 서비스 연결 | RDS·외부 API를 K8s 내부 이름으로 접근. |

```
외부 트래픽
    │
    ▼
LoadBalancer Service (AWS ALB/NLB)
    │
    ▼
Ingress (L7 라우팅 — /api → API Service, /web → Web Service)
    │
    ▼
ClusterIP Service → Pod들
```

**Ingress**: Service는 아니지만 함께 알아야 한다. L7 HTTP 라우팅을 담당하며, 하나의 LB로 여러 서비스에 도메인/경로 기반 분배가 가능하다.

---

## 4-4. RBAC (Role-Based Access Control)

```
┌─────────────┐   바인딩    ┌───────────────┐
│  Subject    │◄───────────│ RoleBinding /  │
│  (사용자·   │            │ ClusterRoleBinding│
│   SA·그룹)  │            └───────┬────────┘
└─────────────┘                    │ 참조
                                   ▼
                           ┌───────────────┐
                           │  Role /       │
                           │  ClusterRole  │
                           │  (권한 정의)  │
                           └───────────────┘
```

- **Role**: 특정 namespace 안에서만 유효한 권한 집합.
- **ClusterRole**: 클러스터 전체에 걸쳐 유효.
- **RoleBinding**: Subject(사용자·ServiceAccount)에 Role을 연결.
- **ServiceAccount**: Pod에 부여하는 K8s 내부 신원. Pod가 API Server에 접근할 때 쓴다.

```yaml
# 예: dev namespace의 pod만 read할 수 있는 Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

**면접 답변 뼈대:** "RBAC는 누가 무엇을 할 수 있는지를 Role로 정의하고, RoleBinding으로 Subject(사용자·SA)에 연결하는 방식입니다. namespace 범위면 Role, 클러스터 전체면 ClusterRole을 씁니다. PF-K8s에서 개발자용·운영자용 ServiceAccount를 분리해서 운영자만 배포 권한을 갖도록 설정했습니다."

---

## 4-5. Deployment 롤링 업데이트 / 롤백

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1   # 동시에 내릴 수 있는 최대 Pod 수
    maxSurge: 1         # 동시에 추가로 띄울 수 있는 최대 Pod 수
```

배포 중 구버전 Pod를 하나 내리고 신버전 Pod를 하나 올리는 과정을 반복한다. 서비스 중단 없이 배포 가능.

```bash
kubectl rollout undo deployment/myapp           # 이전 버전으로 롤백
kubectl rollout history deployment/myapp        # 배포 이력 확인
kubectl rollout status deployment/myapp         # 현재 배포 상태
```

---

## 4-6. HPA (Horizontal Pod Autoscaler)

CPU 사용률이 임계치를 넘으면 자동으로 Pod 수를 늘린다.

```yaml
apiVersion: autoscaling/v2
kind: HPA
metadata:
  name: myapp-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: myapp
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60    # CPU 60% 초과 시 스케일아웃
```

---

## 4-7. ConfigMap과 Secret

**ConfigMap**: 환경변수·설정 파일처럼 변경 가능한 비밀 아닌 설정을 Pod 외부로 분리.

**Secret**: DB 패스워드·API 키처럼 민감한 정보. base64 인코딩(암호화 아님 — 주의). 실제 보안을 위해선 Vault나 AWS Secrets Manager와 연동.

```bash
# Secret 생성
kubectl create secret generic db-secret \
  --from-literal=password=mypassword

# Pod에서 환경변수로 주입
env:
- name: DB_PASSWORD
  valueFrom:
    secretKeyRef:
      name: db-secret
      key: password
```

---

# 5. CI/CD

## 5-1. CI/CD 파이프라인 설계 (직접 설계 요청 대비)

면접관이 화이트보드에 "CI/CD를 직접 설계해보세요"라고 할 때의 답:

```
개발자 코드 push (main/develop 브랜치)
    │
    ▼
[CI] GitHub Actions 트리거
    ├─ lint (코드 스타일 검사)
    ├─ test (단위·통합 테스트)
    ├─ build (Docker 이미지 빌드)
    ├─ scan (Trivy 취약점 스캔 — CRITICAL 있으면 실패)
    └─ push (ECR에 이미지 푸시, commit SHA 태그)
         │
         ▼
    [승인 게이트] (프로덕션 환경 → Environment Protection Rule)
         │ 운영자 Approve
         ▼
[CD] ArgoCD가 Git 변경 감지 (GitOps)
    └─ K8s에 롤링 업데이트 배포
         │
         ▼
[모니터링] Prometheus → Grafana → AlertManager
    └─ 배포 후 에러율·레이턴시 이상 감지 시 Slack 알림
```

**면접 답변 뼈대:** "CI는 코드 push 시 자동으로 lint·테스트·빌드·Trivy 스캔까지 실행하고, CRITICAL 취약점이 있으면 실패시킵니다. 이미지는 commit SHA로 태깅해서 어느 코드가 어느 이미지인지 추적 가능하게 합니다. 프로덕션 배포는 Environment Protection Rule로 승인 게이트를 달고, ArgoCD가 Git 상태를 보고 K8s에 자동 동기화합니다."

---

## 5-2. Blue-Green 배포 vs Canary 배포

```
Blue-Green 배포:
                      ┌─────────────────┐
                 100% │  Blue (구버전)   │ ← 현재 라이브
로드밸런서 ──────────►├─────────────────┤
                 0%   │  Green (신버전)  │ ← 새로 배포·테스트
                      └─────────────────┘
                   전환 후:
                 0%   │  Blue (구버전)   │ ← 대기 (롤백용)
로드밸런서 ──────────►├─────────────────┤
                 100% │  Green (신버전)  │ ← 라이브
                      └─────────────────┘

Canary 배포:
                 95%  │  구버전          │
로드밸런서 ──────────►├──────────────────┤
                 5%   │  신버전 (카나리)  │ ← 소수 유저에게만
```

| 항목 | Blue-Green | Canary |
|------|------------|--------|
| 방식 | 두 환경 전환 (스위치) | 트래픽 비율 조절 |
| 롤백 속도 | 즉시 (스위치 원복) | 비율만 되돌림 |
| 비용 | 리소스 2배 필요 | 점진적으로 증가 |
| 위험 노출 | 전환 전까지 0 | 점진적 노출 |
| 적합 상황 | 큰 변경·DB 마이그레이션 | 새 기능 A/B 테스트 |

**면접 답변 뼈대:** "Blue-Green은 동일한 환경을 두 벌 두고 한 번에 스위치하는 방식이라 롤백이 즉시 가능하지만 리소스가 2배 듭니다. Canary는 신버전에 트래픽을 5%→10%→100% 식으로 점진적으로 늘려서 실제 사용자 반응을 보면서 안전하게 배포합니다."

---

## 5-3. GitOps (ArgoCD)

GitOps는 **Git을 단일 진실원천(Single Source of Truth)**으로 삼아 인프라와 앱 배포를 관리하는 방식이다.

```
개발자 → Git에 K8s manifests push
              │
              ▼
         ArgoCD (클러스터 내에서 Git 상태 감시)
              │ 차이 감지
              ▼
         K8s에 자동 동기화 (apply)
```

**GitOps의 장점:** 배포 이력이 Git 커밋 이력과 동일하다. 누가 언제 무엇을 배포했는지 추적 가능. 롤백 = 이전 커밋으로 revert.

**ArgoCD vs Flux:** 둘 다 GitOps 툴인데, ArgoCD는 GUI 대시보드가 있어서 시각적으로 동기화 상태를 확인할 수 있다.

---

# 6. IaC (Infrastructure as Code)

## 6-1. IaC를 왜 쓰나요

"수동으로 콘솔 클릭하면 되는데 왜 코드로 쓰나요?" — 이 질문의 진짜 의도는 협업과 재현성이다.

**핵심 이유 3가지:**
1. **버전관리 + 코드리뷰**: 인프라 변경이 Git PR로 기록·검토된다. 누가 언제 무엇을 바꿨는지 추적 가능.
2. **재현성**: 동일한 코드로 dev·staging·prod 환경을 동일하게 만들 수 있다. 수작업은 환경마다 미묘하게 다른 "드리프트"가 생긴다.
3. **자동화**: 파이프라인에서 인프라까지 자동 생성·파괴 가능. 비용 절감(테스트 환경 자동 삭제 등).

---

## 6-2. Terraform State란

```
코드 (main.tf)  ────►  terraform plan  ────►  terraform apply
                              │
                              ▼ 비교
                        terraform.tfstate
                        (실제 인프라 ↔ 코드 매핑)
```

`tfstate`는 Terraform이 실제로 만든 리소스와 코드를 연결하는 매핑 파일이다. `plan`은 이 파일을 보고 현재 상태와 선언된 상태의 차이를 계산한다.

**팀 협업 시 원격 백엔드가 필수인 이유:**

```hcl
terraform {
  backend "s3" {
    bucket         = "my-tfstate-bucket"
    key            = "prod/terraform.tfstate"
    region         = "ap-northeast-2"
    dynamodb_table = "terraform-lock"  # 동시 apply 방지 락
  }
}
```

로컬에 tfstate를 두면 팀원 A와 B가 동시에 apply할 때 충돌 위험이 있다. S3 + DynamoDB 락으로 동시성 제어.

---

## 6-3. Ansible vs Terraform 역할 구분

| 항목 | Terraform | Ansible |
|------|-----------|---------|
| 목적 | 인프라 프로비저닝 (EC2 생성·VPC 구성) | 서버 설정 자동화 (패키지 설치·앱 배포) |
| 방식 | 선언형 (결과 상태 선언, 방법은 TF가 결정) | 절차형 (순서대로 Playbook 실행) |
| 상태 관리 | tfstate로 추적 | 상태 없음 (매번 재실행 가능 — idempotent) |
| 연동 | TF로 EC2 생성 → 출력(IP)을 Ansible 인벤토리에 전달 | |

PF-IaC에서의 역할 분담: Terraform이 VPC·EC2·RDS를 만들고 → Ansible이 그 EC2에 Docker 설치·Nginx 설정·앱 배포를 자동화.

---

# 7. AWS / Cloud (SAA 준비와 연동)

## 7-1. SAA 핵심 서비스 면접 답변

### EC2 vs ECS vs EKS

| 서비스 | 무엇을 관리하나 | 사용 상황 |
|--------|----------------|-----------|
| EC2 | 직접 서버 관리 (OS·미들웨어) | 레거시·세밀한 제어 필요 시 |
| ECS | AWS가 컨테이너 오케스트레이션 관리 | 간단한 컨테이너 앱, K8s 학습 전 단계 |
| EKS | 관리형 K8s (Control Plane은 AWS가) | K8s 표준 + AWS 통합 |

### RDS Multi-AZ vs Read Replica

| 항목 | Multi-AZ | Read Replica |
|------|----------|--------------|
| 목적 | 고가용성 (HA) | 읽기 성능 향상 |
| 복제 방식 | 동기 (Standby에 실시간 동기) | 비동기 |
| 페일오버 | 자동 (DNS 전환, 수십 초) | 수동 승격 필요 |
| 쓰기 가능 여부 | Primary만 | Primary만 (Replica는 읽기 전용) |

### S3 스토리지 클래스 (비용 최적화)

```
접근 빈도 높음  → Standard
접근 빈도 불규칙 → Intelligent-Tiering (자동 이동)
30일 미접근     → Standard-IA
90일 미접근     → Glacier Instant Retrieval
1년 이상 보관   → Glacier Deep Archive
```

---

## 7-2. 서버리스 면접 질문

### Lambda + API Gateway

**Lambda**는 서버 없이 코드를 실행하는 FaaS(Function as a Service). 요청이 올 때만 실행되고, 실행 시간(100ms 단위)만 과금한다.

콜드 스타트 문제: Lambda 인스턴스가 없을 때 첫 요청에 지연이 발생한다. 해결책: Provisioned Concurrency(미리 인스턴스 유지).

**API Gateway + Lambda 패턴:**
```
클라이언트 → API Gateway (REST/HTTP API) → Lambda → DynamoDB
```

마이크로서비스를 서버 없이 구성하는 패턴. EC2 비용 없이 트래픽에 따라 자동 스케일.

### SQS vs SNS

| 항목 | SQS | SNS |
|------|-----|-----|
| 모델 | 큐(Queue) — 폴링 방식 | 토픽(Topic) — 발행/구독 |
| 목적 | 메시지 버퍼링, 비동기 처리 | 팬아웃(하나 → 여러 구독자에게 동시 전달) |
| 메시지 유지 | 최대 14일 | 전달 후 삭제 |

패턴: SNS → 여러 SQS 구독 (팬아웃). 이미지 업로드 이벤트 → SNS → SQS(리사이즈)·SQS(메타데이터 저장)·SQS(알림) 병렬 처리.

---

# 8. 포트폴리오 질문 (STAR 답변 프레임)

면접에서 가장 깊이 파고드는 구간. **STAR 프레임**으로 답한다:
- **S**ituation: 상황 (왜 만들었나)
- **T**ask: 내가 맡은 과제
- **A**ction: 구체적으로 어떻게 했나 (기술 선택 이유 포함)
- **R**esult: 결과 (수치·개선점)

## PF2 — Go + Docker 배포 자동화

**Q. 왜 Go를 선택했나요?**

"서버 바이너리로 컴파일되어 컨테이너 이미지 크기가 극단적으로 작아지기 때문입니다. Python이나 Node.js는 인터프리터와 의존성을 다 포함해야 하지만, Go는 멀티스테이지 빌드로 alpine 기반 이미지에 바이너리 하나만 넣으면 됩니다. 실제로 이미지 크기가 __MB 수준이었고, 기동 시간도 밀리초 단위였습니다. DevOps에서 배포 속도와 이미지 효율이 중요하다는 판단에서 Go를 선택했습니다."

**Q. 이미지 보안은 어떻게 관리했나요?**

"빌드 직후 Trivy로 이미지를 스캔하고, CRITICAL 취약점이 있으면 deploy.sh가 중단되도록 했습니다. 스캔 결과 리포트를 README에 첨부해서 면접관이 바로 확인할 수 있게 했습니다. 실제 프로덕션에서는 GitHub Actions에 Trivy step을 붙여 파이프라인 자체에서 막는 게 표준입니다."

**Q. deploy.sh에서 무엇을 자동화했나요?**

"docker build → trivy image scan → docker tag → ECR push → container stop → container start → /health 엔드포인트로 헬스체크까지 7단계를 자동화했습니다. 헬스체크가 3회 실패하면 이전 버전으로 자동 롤백하도록 했습니다."

---

## PF3 — Python 서버 모니터링

**Q. 모니터링에서 어떤 메트릭을 봤고 왜 그걸 선택했나요?**

"CPU 사용률, 메모리 사용률, 디스크 I/O, 열린 파일 디스크립터 수를 선택했습니다. CPU와 메모리는 서버 과부하의 가장 직접적인 지표고, 디스크 I/O는 DB·로그 집약적 작업에서 병목이 자주 생기기 때문입니다. 파일 디스크립터는 소켓 누수를 조기에 발견하기 위해 포함했습니다. Slack Webhook으로 임계치 초과 시 즉시 알림이 오게 했고, PF1에서는 psutil 대신 Prometheus Exporter로 전환할 예정입니다."

---

## PF1 — End-to-End 파이프라인 (8월 완성 후)

**Q. 코드 push 한 번으로 배포까지 자동화했다고 하셨는데, 구체적인 수치가 있나요?**

(완성 후 실제 수치로 채울 것)
- 배포 소요 시간: _분 (이전 수동 배포 대비 _% 감소)
- 장애 감지 응답 시간: Prometheus AlertManager 기준 _초 이내
- Trivy 스캔으로 파이프라인 단계에서 차단한 취약점: _ 건

---

# 9. 실전 면접 팁

## 모르는 질문이 나왔을 때

"잠깐 생각할 시간을 주시겠어요?"라고 말하는 게 "모르겠습니다"보다 훨씬 낫다. 생각하면서 "이 개념은 ~와 연관된 것 같은데, 구체적인 구현은 경험이 없어서 말씀드리기 어렵습니다. 하지만 제가 아는 범위에서 추론하면 ~"으로 사고 과정을 보여주는 게 좋다.

## 포트폴리오 질문에서 수치를 못 대면

면접관이 "결과가 어떻게 됐나요?"라고 물을 때 "좋아졌습니다"로 끝내면 감점이다. 구체적인 수치 — 배포 시간, 이미지 크기, 응답 레이턴시, 에러율 — 를 PF 완성 시 반드시 측정해두자.

## 기술 트렌드 질문 대비

**DevOps/Cloud Native 트렌드:**
- FinOps (클라우드 비용 최적화)
- Platform Engineering (개발자 셀프서비스 플랫폼)
- Supply Chain Security (SBOM, Sigstore)
- eBPF 기반 관찰성 도구 (Cilium, Tetragon)

---

# 일일 트래커 (6/20부터 매일 1문제)

| 날짜 | 질문 | 상태 | 약점★ |
|------|------|------|-------|
| 6/20 | 프로세스 vs 스레드 + 컨텍스트 스위칭 | ⬜ | |
| 6/21 | 데드락 4조건 + 해결 전략 | ⬜ | |
| 6/22 | 서버 CPU 100% 진단 루틴 (순서대로) | ⬜ | |
| 6/23 | TCP 3-way handshake + TIME_WAIT 이유 | ⬜ | |
| 6/24 | HTTP vs HTTPS (TLS 핸드셰이크 순서) | ⬜ | |
| 6/25 | 로드밸런서 L4 vs L7 + AWS NLB/ALB | ⬜ | |
| 6/26 | 컨테이너 vs VM (격리 원리: namespace·cgroups) | ⬜ | |
| 6/27 | Docker 이미지 레이어 + 멀티스테이지 빌드 | ⬜ | |
| 6/28 | IaC를 쓰는 이유 + Terraform State | ⬜ | |
| 6/29 | VPC Public/Private 서브넷 분리 이유 | ⬜ | |
| 6/30 | DNS 동작 원리 + Route53 라우팅 정책 | ⬜ | |
| 7/7~ | K8s Pod 라이프사이클 (Phase 3 학습 후) | ⬜ | |
| 7/8~ | K8s Service 종류와 차이 | ⬜ | |
| 7/9~ | RBAC 설명 | ⬜ | |
| 8/6~ | CI/CD 파이프라인 설계 (Phase 5 학습 후) | ⬜ | |
| 8/7~ | Blue-Green vs Canary | ⬜ | |
| 8/8~ | GitOps + ArgoCD | ⬜ | |

> ★ 표시한 건 3일 후 재도전. PF 완성 때마다 포트폴리오 질문 칸 채울 것.
