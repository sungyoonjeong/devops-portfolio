# ============================================================
# monitor.py
# 목적: 서버 CPU·메모리·디스크를 감지하고 Slack으로 알림 발송
# 실행: python3 monitor.py
# ============================================================


# ── 모듈 불러오기 ────────────────────────────────────────────

import psutil        # 서버 시스템 정보(CPU·메모리·디스크) 읽는 외부 라이브러리
import requests      # HTTP 요청 보내는 외부 라이브러리 (Slack에 POST 요청할 때 사용)
import logging       # 로그를 파일과 화면에 기록하는 Python 기본 내장 모듈
import time          # time.sleep()으로 일정 시간 대기할 때 사용하는 기본 내장 모듈
from datetime import datetime          # 현재 시간을 가져올 때 사용
from logging.handlers import RotatingFileHandler  # 로그 파일 크기 제한 기능


# ── 설정값 ───────────────────────────────────────────────────

# Slack Webhook URL: Slack에서 발급받은 주소를 여기에 입력
# 이 URL로 POST 요청을 보내면 Slack 채널에 메시지가 옴
SLACK_WEBHOOK = "https://hooks.slack.com/services/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"

# 임계값: 이 수치를 초과하면 Slack 알림 발송
CPU_THRESHOLD    = 80.0  # CPU 사용률이 80% 넘으면 알림
MEMORY_THRESHOLD = 85.0  # 메모리 사용률이 85% 넘으면 알림
DISK_THRESHOLD   = 80.0  # 디스크 사용률이 80% 넘으면 알림

# 점검 주기: 몇 초마다 서버 상태를 확인할지 설정
CHECK_INTERVAL = 300  # 300초 = 5분마다 확인


# ── 로그 설정 ─────────────────────────────────────────────────

# basicConfig: 로그의 기본 동작 방식을 설정
logging.basicConfig(
    level=logging.INFO,  # INFO 이상(INFO·WARNING·ERROR·CRITICAL)만 기록, DEBUG는 무시

    # format: 로그 한 줄의 형식 지정
    # %(asctime)s   → 시간 (2026-06-01 10:20:35,123)
    # %(levelname)s → 로그 레벨 (INFO, WARNING, ERROR 등)
    # %(message)s   → 실제 메시지 내용
    format='%(asctime)s [%(levelname)s] %(message)s',

    handlers=[  # handlers: 로그를 어디에 출력할지 지정 (여러 곳 동시 가능)

        # RotatingFileHandler: 로그를 파일에 기록, 크기 제한 있음
        RotatingFileHandler(
            'monitor.log',              # 로그 파일 이름
            maxBytes=5 * 1024 * 1024,   # 최대 5MB (넘으면 새 파일 생성)
            backupCount=3               # 최대 3개 파일 보관 (monitor.log, monitor.log.1, monitor.log.2)
        ),

        logging.StreamHandler()  # StreamHandler: 터미널 화면에도 동시 출력
    ]
)

# getLogger: 이 파일 전용 로거 객체 생성
# __name__ = 현재 파일 이름 (monitor.py이면 "monitor")
logger = logging.getLogger(__name__)


# ── 함수 1: 서버 메트릭 수집 ──────────────────────────────────

def get_metrics():
    """CPU·메모리·디스크 사용률을 측정해서 반환하는 함수"""

    # cpu_percent(interval=1): 1초 동안 측정한 CPU 사용률 반환 (0.0 ~ 100.0)
    # interval=0 이면 첫 호출 시 항상 0.0 반환되므로 반드시 1 이상 사용
    cpu = psutil.cpu_percent(interval=1)

    # virtual_memory(): 메모리 전체 정보를 담은 객체 반환
    # .percent: 그 중 사용률(%)만 꺼냄
    memory = psutil.virtual_memory().percent

    # disk_usage('/'): 루트(/) 경로의 디스크 정보를 담은 객체 반환
    # .percent: 그 중 사용률(%)만 꺼냄
    disk = psutil.disk_usage('/').percent

    # 세 값을 동시에 반환 (다중 반환값)
    # 호출하는 쪽에서 cpu, memory, disk = get_metrics() 로 받음
    return cpu, memory, disk


# ── 함수 2: Slack 알림 발송 ───────────────────────────────────

def send_slack(message):
    """Slack Webhook으로 메시지를 전송하는 함수"""

    # try: 실행 중 오류가 생겨도 프로그램이 멈추지 않도록 감싸기
    try:
        # requests.post: HTTP POST 요청을 Slack Webhook URL로 전송
        response = requests.post(
            SLACK_WEBHOOK,            # 요청을 보낼 URL
            json={"text": message},   # 보낼 데이터: {"text": "메시지 내용"}
            timeout=5                 # 5초 안에 응답 없으면 포기 (무한 대기 방지)
        )

        # status_code: 서버가 응답한 HTTP 상태 코드
        # 200 = 성공, 그 외 = 실패
        if response.status_code == 200:
            logger.info("Slack 알림 전송 완료")  # 성공 로그 기록
        else:
            # f-string: 변수를 문자열 안에 넣는 방법 (f"..." 안에 {변수})
            logger.error(f"Slack 전송 실패: {response.status_code}")  # 실패 로그

    # except: try 블록에서 오류 발생 시 여기서 처리
    except requests.exceptions.ConnectionError:
        # ConnectionError: 인터넷 연결 없을 때 발생
        logger.error("네트워크 연결 오류 - Slack 전송 실패")

    except requests.exceptions.Timeout:
        # Timeout: timeout=5 초과 시 발생
        logger.error("요청 시간 초과 - Slack 전송 실패")

    except Exception as e:
        # Exception: 위에서 잡지 못한 나머지 모든 오류
        # as e: 오류 내용을 변수 e에 저장
        logger.error(f"알 수 없는 오류: {e}")


# ── 함수 3: 임계값 확인 + 알림 ───────────────────────────────

def check_and_alert(cpu, memory, disk):
    """측정값이 임계값을 초과하면 로그 기록 + Slack 알림 발송"""

    # datetime.now(): 현재 날짜와 시간을 가져옴
    # .strftime("형식"): 원하는 형식의 문자열로 변환
    # %Y = 4자리 연도, %m = 2자리 월, %d = 2자리 일
    # %H = 24시간 시, %M = 분, %S = 초
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 알림이 발송됐는지 추적하는 변수 (나중에 "정상" 메시지 출력 여부 결정)
    alerted = False

    # CPU 임계값 초과 확인
    if cpu > CPU_THRESHOLD:  # cpu가 80.0보다 크면
        # f-string으로 알림 메시지 조합
        # \n = 줄바꿈
        # :.1f = 소수점 첫째 자리까지 표시 (예: 92.5%)
        msg = f"🔴 CPU 위험 알림\n시간: {now}\n현재: {cpu:.1f}% (임계값: {CPU_THRESHOLD}%)"
        logger.warning(f"CPU 위험: {cpu:.1f}%")  # WARNING 레벨로 로그 기록
        send_slack(msg)   # Slack 알림 발송
        alerted = True    # 알림 발송됐음을 표시

    # 메모리 임계값 초과 확인
    if memory > MEMORY_THRESHOLD:  # memory가 85.0보다 크면
        msg = f"🟡 메모리 경고\n시간: {now}\n현재: {memory:.1f}% (임계값: {MEMORY_THRESHOLD}%)"
        logger.warning(f"메모리 경고: {memory:.1f}%")
        send_slack(msg)
        alerted = True

    # 디스크 임계값 초과 확인
    if disk > DISK_THRESHOLD:  # disk가 80.0보다 크면
        msg = f"⚠️  디스크 주의\n시간: {now}\n현재: {disk:.1f}% (임계값: {DISK_THRESHOLD}%)"
        logger.warning(f"디스크 주의: {disk:.1f}%")
        send_slack(msg)
        alerted = True

    # alerted가 False면 → 세 지표 모두 정상
    if not alerted:
        # INFO 레벨로 정상 상태 로그 기록
        logger.info(f"정상 | CPU: {cpu:.1f}% | 메모리: {memory:.1f}% | 디스크: {disk:.1f}%")


# ── 메인 실행 ─────────────────────────────────────────────────

def main():
    """프로그램 시작점 - 모니터링 실행"""

    # 시작 로그 기록
    logger.info("=" * 50)
    logger.info("서버 모니터링 시작")
    logger.info(f"임계값 → CPU: {CPU_THRESHOLD}% | 메모리: {MEMORY_THRESHOLD}% | 디스크: {DISK_THRESHOLD}%")
    logger.info(f"점검 주기: {CHECK_INTERVAL}초 ({CHECK_INTERVAL // 60}분)")
    # // = 정수 나누기 (소수점 버림): 300 // 60 = 5
    logger.info("=" * 50)

    # ── 1회 실행 (테스트용) ──
    cpu, memory, disk = get_metrics()  # 메트릭 수집
    check_and_alert(cpu, memory, disk) # 임계값 확인 + 알림

    # ── 주기적 실행 (실제 운영용) ──
    #아래 주석 해제하면 5분마다 자동 반복
    while True:                           # 무한루프 시작
        cpu, memory, disk = get_metrics() # 메트릭 수집
        check_and_alert(cpu, memory, disk)# 확인 + 알림
        time.sleep(CHECK_INTERVAL)        # 5분 대기 후 다시 반복


# ── 진입점 ────────────────────────────────────────────────────

# if __name__ == "__main__":
# → 이 파일을 직접 실행할 때만 main() 호출
# → 다른 파일에서 import해서 쓸 때는 main() 자동 실행 안 됨
# → Python 파일의 표준 진입점 패턴
if __name__ == "__main__":
    main()  # main 함수 호출 → 프로그램 시작