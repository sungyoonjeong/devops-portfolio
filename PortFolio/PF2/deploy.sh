#!/bin/bash
# deploy.sh: 빌드 → 보안 스캔 → 재시작 → 헬스체크를 한 번에 수행하는 배포 자동화 스크립트

# set -e: 이후 명령 중 하나라도 실패(exit code != 0)하면 즉시 스크립트 전체 종료
# 중간 단계가 실패했는데 배포가 계속 진행되는 사고를 막는 안전 장치
set -e

# 이미지 이름과 태그 설정
IMAGE="pf2"
# git의 현재 커밋 해시 앞 7자리를 태그로 사용
# 이유: 어떤 코드로 만든 이미지인지 git 히스토리와 1:1 추적 가능 (이미지 버전 관리)
TAG=$(git rev-parse --short HEAD)

# ── Step 1: Docker 이미지 빌드 ──
echo "▶ [1/4] Build: $IMAGE:$TAG"
# Dockerfile 기준으로 이미지 빌드, -t로 이름:태그 지정
docker build -t "$IMAGE:$TAG" .

# ── Step 2: Trivy 보안 스캔 ──
echo "▶ [2/4] Trivy Scan"

# 스캔 결과를 저장할 디렉토리 생성 (없으면 자동 생성)
mkdir -p trivy-reports

# REPORT_FILE: 커밋 해시와 날짜를 조합해 스캔마다 고유한 파일명 생성
# 예: trivy-reports/pf2-6750b6c-20260621.json
REPORT_FILE="trivy-reports/${IMAGE}-${TAG}-$(date +%Y%m%d).json"

# trivy image: 컨테이너 이미지의 OS 패키지·라이브러리 취약점(CVE)을 스캔
# --exit-code 0: 취약점이 발견돼도 스크립트를 종료하지 않음 (0이면 경고만, 1이면 중단)
#               프로덕션에서는 --exit-code 1로 설정해 HIGH/CRITICAL 발견 시 배포 차단
# --severity HIGH,CRITICAL: 높은 위험도(HIGH, CRITICAL) 취약점만 보고
# --format json: 결과를 JSON 형식으로 출력 (파싱·보관 용이)
# --output: JSON 결과를 파일로 저장
trivy image --exit-code 0 --severity HIGH,CRITICAL --format json --output "$REPORT_FILE" "$IMAGE:$TAG"

# 터미널에도 표(table) 형식으로 출력해 바로 확인 가능하도록 별도 실행
trivy image --exit-code 0 --severity HIGH,CRITICAL "$IMAGE:$TAG"

echo "  스캔 결과 저장: $REPORT_FILE"

# ── Step 3: 기존 컨테이너 종료 후 새 컨테이너 시작 ──
echo "▶ [3/4] Restart"
# docker compose down: 실행 중인 모든 서비스(app+nginx) 컨테이너 정지 및 제거
docker compose down
# docker compose up -d: 새 이미지로 컨테이너를 백그라운드(-d, detached)로 시작
docker compose up -d

# ── Step 4: 헬스체크 ──
echo "▶ [4/4] Health Check"
# 컨테이너가 완전히 뜰 때까지 3초 대기 (너무 빨리 curl하면 connection refused)
sleep 3
# curl -f: HTTP 응답이 4xx·5xx이면 실패로 처리 (set -e와 함께 스크립트 종료)
# localhost/health로 nginx → app 경로 전체를 한 번에 검증
curl -f http://localhost/health && echo " Deploy OK"
