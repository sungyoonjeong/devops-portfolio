# ============================================================
# PF3 monitor.py 컨테이너화
# 빌드: docker build -t pf3-monitor .
# 실행: docker run -d --name pf3 \
#         -e SLACK_WEBHOOK_URL="https://hooks.slack.com/..." \
#         -v /:/host:ro -e DISK_PATH=/host \
#         pf3-monitor
# 참고: /proc 기반인 CPU·메모리는 컨테이너 안에서도 호스트 값이 읽히지만,
#       디스크는 컨테이너 파일시스템을 보게 되므로 호스트 루트를 /host로
#       읽기전용 마운트해서 측정한다.
# 주의: Dockerfile은 명령 뒤 인라인 주석 불가 - 주석은 반드시 줄 시작에서만
# ============================================================

# 풀 이미지 대신 slim - 필요한 것만 (PF2 멀티스테이지와 같은 원칙)
FROM python:3.11-slim

# 이후 명령들의 작업 디렉토리 (monitor.log도 여기 쌓임)
WORKDIR /app

# 외부 의존성 2개. --no-cache-dir로 이미지 용량 절약
RUN pip install --no-cache-dir psutil requests

# 소스는 마지막에 복사 - 코드만 바뀌면 pip 레이어는 캐시 재사용
COPY monitor.py .

# 컨테이너 시작 시 모니터링 실행 (5분 주기 무한루프)
CMD ["python3", "monitor.py"]
