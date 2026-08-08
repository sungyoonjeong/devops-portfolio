# ──────────────────────────────────────────────
# Stage 1: builder — Go 소스를 컴파일하는 단계
# golang:1.22-alpine을 쓰는 이유: alpine은 Alpine Linux 기반으로 용량이 작고,
# Go 컴파일러만 있으면 되므로 빌드 전용 이미지로 적합하다
# ──────────────────────────────────────────────
FROM golang:1.22-alpine AS builder

# 컨테이너 내 작업 디렉토리 지정 — 이후 COPY·RUN은 모두 /app 기준으로 실행
WORKDIR /app

# 의존성 정의 파일만 먼저 복사하는 이유: Docker 레이어 캐시 활용
# 이 두 파일이 바뀌지 않으면 RUN go mod download 레이어가 캐시히트 → 빌드 속도 향상
# go.sum을 반드시 같이 복사한다: go.sum은 각 모듈의 체크섬(해시)을 담고 있어서,
# 이게 있어야 다운로드한 모듈이 변조되지 않았는지 검증된다(공급망 보안).
# go.mod만 복사하면 go mod download가 검증 없이 받아오게 된다.
COPY go.mod go.sum ./

# 의존 모듈 다운로드 — go.sum 기준으로 체크섬 검증까지 수행
RUN go mod download

# 나머지 소스 전체 복사 (main.go 등)
COPY . .

# 정적 바이너리로 컴파일
# CGO_ENABLED=0: C 라이브러리 의존성 제거 → alpine 이미지에서도 실행 가능한 순수 Go 바이너리
# GOOS=linux: 크로스 컴파일 시 명시 (macOS에서 빌드해도 리눅스 바이너리 생성)
# -o server: 출력 파일 이름을 'server'로 지정
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

# ──────────────────────────────────────────────
# Stage 2: final — 실행만 하는 최소 이미지
# alpine:3.19: Go 컴파일러·소스코드 없이 바이너리만 담음 → 이미지 크기 ~10MB
# builder 이미지(~300MB)를 최종 이미지에서 완전히 제외하는 것이 멀티스테이지의 핵심
# ──────────────────────────────────────────────
FROM alpine:3.19

# 전용 비특권 유저 생성 — 컨테이너를 root로 돌리지 않기 위해
# 기본값(USER 미지정)은 root라, 컨테이너가 탈출당하면 호스트 권한까지 위험해진다
# -D: 비밀번호 없이 생성, -H: 홈 디렉토리 불필요(앱만 실행), -s /sbin/nologin: 로그인 셸 차단
RUN adduser -D -H -s /sbin/nologin app

WORKDIR /app

# builder 스테이지에서 만들어진 바이너리만 복사 — 소스·컴파일러·캐시는 포함 안 됨
# --chown으로 소유권을 app 유저에게 넘겨, 아래 USER 전환 후에도 정상 실행되게 한다
COPY --from=builder --chown=app:app /app/server .

# 이 시점 이후의 모든 명령과 컨테이너 프로세스는 app 유저 권한으로 실행된다
# 8080은 1024보다 큰 비특권 포트라 root가 아니어도 바인딩 가능
USER app

# 컨테이너가 8080 포트를 사용한다는 문서화 역할 (실제 포트 바인딩은 docker-compose에서)
EXPOSE 8080

# 컨테이너 시작 시 실행할 기본 명령
CMD ["./server"]
