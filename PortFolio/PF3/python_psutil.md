# 🐍 DevOps Python 완전 정리 — psutil·requests·subprocess·logging

> PF3 (서버 이상 감지 + Slack 자동 알림) 구현을 위한 Python 모듈 완전 가이드

---

## 목차
1. [왜 이걸 배우는가](#1-왜-이걸-배우는가)
2. [psutil — 서버 메트릭 수집](#2-psutil--서버-메트릭-수집)
3. [requests — Slack 알림 발송](#3-requests--slack-알림-발송)
4. [subprocess — 쉘 명령어 실행](#4-subprocess--쉘-명령어-실행)
5. [logging — 로그 파일 기록](#5-logging--로그-파일-기록)
6. [time·datetime — 주기 실행·시간 기록](#6-timedatetime--주기-실행시간-기록)
7. [전체 통합 코드](#7-전체-통합-코드)
8. [자주 하는 실수](#8-자주-하는-실수)

---

## 1. 왜 이걸 배우는가

### 문제 상황
```
서버 운영 중 갑자기 CPU가 100%가 됐다.
누가 알아채나? → 사람이 직접 확인해야 함
새벽 3시에 디스크가 꽉 찼다 → 아침에야 발견

→ 사람이 보지 않아도 자동으로 감지하고
  Slack으로 알림을 보내는 시스템이 필요
```

### 해결책: PF3
```
monitor.py 실행 → 5분마다 자동으로:
  ① psutil로 CPU·메모리·디스크 수치 읽기
  ② 임계값 초과 확인
  ③ 초과 시 requests로 Slack 알림 발송
  ④ logging으로 로그 파일에 기록
```

### 사용하는 모듈 5개

| 모듈 | 역할 | 설치 |
|------|------|------|
| `psutil` | CPU·메모리·디스크·프로세스 정보 읽기 | pip install |
| `requests` | HTTP 요청 (Slack Webhook 호출) | pip install |
| `subprocess` | 쉘 명령어 실행 (df, ps, free 등) | 기본 내장 |
| `logging` | 로그 파일 기록 | 기본 내장 |
| `time·datetime` | 주기적 실행, 시간 기록 | 기본 내장 |

### 설치

```bash
pip install psutil requests
```

---

## 2. psutil — 서버 메트릭 수집

### psutil이란?
**P**rocess and **S**ystem **util**ities의 줄임말.  
Python에서 시스템 정보(CPU·메모리·디스크·네트워크·프로세스)를  
한 줄로 읽을 수 있게 해주는 라이브러리입니다.

```python
import psutil
```

---

### CPU 사용률

```python
# 1초 간격으로 CPU 사용률 측정 (권장)
cpu = psutil.cpu_percent(interval=1)
print(f"CPU: {cpu}%")  # CPU: 23.5%

# interval=0 이면 마지막 호출 이후 사용률 (첫 호출은 0.0 반환)
cpu = psutil.cpu_percent(interval=0)

# 코어별 사용률 (percpu=True)
per_core = psutil.cpu_percent(interval=1, percpu=True)
print(per_core)  # [12.5, 34.2, 8.1, 45.3] ← 4코어 예시

# CPU 코어 수
logical  = psutil.cpu_count()          # 논리 코어 (하이퍼스레딩 포함)
physical = psutil.cpu_count(logical=False)  # 물리 코어
print(f"논리: {logical}, 물리: {physical}")
```

---

### 메모리 사용률

```python
mem = psutil.virtual_memory()

print(mem.total)    # 전체 메모리 (bytes)
print(mem.used)     # 사용 중 (bytes)
print(mem.free)     # 여유 (bytes)
print(mem.percent)  # 사용률 (%) ← 주로 이것만 씀

# bytes → GB 변환
total_gb = mem.total / (1024 ** 3)
used_gb  = mem.used  / (1024 ** 3)
print(f"메모리: {used_gb:.1f}GB / {total_gb:.1f}GB ({mem.percent}%)")

# 스왑 메모리
swap = psutil.swap_memory()
print(f"스왑: {swap.percent}%")
```

---

### 디스크 사용률

```python
# 특정 경로의 디스크 사용률
disk = psutil.disk_usage('/')

print(disk.total)    # 전체 (bytes)
print(disk.used)     # 사용 중 (bytes)
print(disk.free)     # 여유 (bytes)
print(disk.percent)  # 사용률 (%) ← 주로 이것만 씀

total_gb = disk.total / (1024 ** 3)
used_gb  = disk.used  / (1024 ** 3)
print(f"디스크: {used_gb:.1f}GB / {total_gb:.1f}GB ({disk.percent}%)")

# 파티션 목록
partitions = psutil.disk_partitions()
for p in partitions:
    print(p.device, p.mountpoint, p.fstype)
```

---

### 프로세스 정보

```python
# 실행 중인 모든 프로세스
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    print(proc.info)

# CPU 많이 쓰는 상위 5개 프로세스
procs = []
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
    try:
        procs.append(proc.info)
    except psutil.NoSuchProcess:
        pass

top5 = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:5]
for p in top5:
    print(f"PID: {p['pid']}, 이름: {p['name']}, CPU: {p['cpu_percent']}%")
```

---

### 네트워크 정보

```python
# 네트워크 I/O 통계
net = psutil.net_io_counters()
print(f"수신: {net.bytes_recv / 1024 / 1024:.1f}MB")
print(f"송신: {net.bytes_sent / 1024 / 1024:.1f}MB")
```

---

## 3. requests — Slack 알림 발송

### requests란?
Python에서 HTTP 요청(GET, POST 등)을 보내는 라이브러리입니다.  
Slack Webhook에 POST 요청을 보내면 Slack 채널에 메시지가 옵니다.

```python
import requests
```

---

### Slack Webhook 설정 방법

```
1. slack.com 접속 → 로그인 (없으면 무료 가입)
2. api.slack.com/apps 접속
3. [Create New App] 클릭
4. [From scratch] 선택
5. App Name: "서버모니터링" 입력
6. 워크스페이스 선택 → [Create App]
7. 왼쪽 메뉴 [Incoming Webhooks] 클릭
8. [Activate Incoming Webhooks] 토글 → ON
9. 스크롤 내려서 [Add New Webhook to Workspace]
10. 알림 받을 채널 선택 (#general 또는 새 채널)
11. [Allow] 클릭
12. Webhook URL 복사 (https://hooks.slack.com/services/...)
```

---

### 기본 메시지 전송

```python
import requests

SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

def send_slack(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK, json=payload)
    return response.status_code  # 200이면 성공

send_slack("테스트 메시지입니다!")
```

---

### 에러 처리 포함 버전

```python
def send_slack(message):
    """Slack 알림 발송 (에러 처리 포함)"""
    try:
        response = requests.post(
            SLACK_WEBHOOK,
            json={"text": message},
            timeout=5  # 5초 안에 응답 없으면 포기
        )
        if response.status_code == 200:
            print("✅ Slack 알림 전송 완료")
            return True
        else:
            print(f"❌ Slack 전송 실패: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 네트워크 연결 오류")
        return False
    except requests.exceptions.Timeout:
        print("❌ 요청 시간 초과")
        return False
    except Exception as e:
        print(f"❌ 알 수 없는 오류: {e}")
        return False
```

---

### 이모지 포함 메시지

```python
# 상태별 메시지 포맷
def format_alert(metric, value, threshold):
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    messages = {
        "cpu":    f"🔴 CPU 위험 알림\n시간: {now}\n현재: {value:.1f}% (임계값: {threshold}%)",
        "memory": f"🟡 메모리 경고\n시간: {now}\n현재: {value:.1f}% (임계값: {threshold}%)",
        "disk":   f"⚠️  디스크 주의\n시간: {now}\n현재: {value:.1f}% (임계값: {threshold}%)",
    }
    return messages.get(metric, f"알림: {metric} = {value}")
```

---

## 4. subprocess — 쉘 명령어 실행

### subprocess란?
Python에서 쉘 명령어를 직접 실행하고 결과를 받는 모듈입니다.  
`df -h`, `ps aux`, `free -m` 같은 명령어를 Python 안에서 실행합니다.

```python
import subprocess
```

---

### 기본 사용법

```python
# run(): 명령어 실행하고 결과 받기
result = subprocess.run(
    ["df", "-h"],           # 명령어를 리스트로 (공백으로 분리)
    capture_output=True,    # 출력 결과 캡처
    text=True               # bytes가 아닌 string으로 반환
)

print(result.stdout)        # 정상 출력
print(result.stderr)        # 에러 출력
print(result.returncode)    # 종료 코드 (0 = 성공)
```

---

### 자주 쓰는 명령어 실행 예시

```python
def run_command(cmd):
    """쉘 명령어 실행 후 결과 반환"""
    result = subprocess.run(
        cmd,
        shell=True,           # 문자열로 명령어 전달 (shell=True)
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# 디스크 사용량
disk_info = run_command("df -h /")
print(disk_info)

# 메모리 사용량
mem_info = run_command("free -m")
print(mem_info)

# CPU 많이 쓰는 프로세스 상위 5개
top_procs = run_command("ps aux --sort=-%cpu | head -6")
print(top_procs)

# 특정 프로세스 실행 확인
nginx_status = run_command("pgrep -x nginx")
if nginx_status:
    print("nginx 실행 중")
else:
    print("nginx 중지됨")
```

---

### shell=True vs 리스트 방식

```python
# shell=True: 문자열로 명령어 전달 (간편하지만 보안 주의)
subprocess.run("df -h /", shell=True, ...)

# 리스트 방식: 더 안전 (권장)
subprocess.run(["df", "-h", "/"], ...)

# 파이프(|) 쓸 때는 shell=True 필요
subprocess.run("ps aux | grep python", shell=True, ...)
```

---

## 5. logging — 로그 파일 기록

### logging이란?
프로그램 실행 내역을 파일에 기록하는 모듈입니다.  
`print()`는 화면에만 출력되지만, `logging`은 파일에도 저장됩니다.

```python
import logging
```

---

### 로그 레벨 5단계

```
DEBUG    → 상세한 디버그 정보 (개발 중)
INFO     → 일반 정보 (정상 동작)
WARNING  → 경고 (문제 가능성)
ERROR    → 에러 (기능 일부 실패)
CRITICAL → 심각한 에러 (프로그램 중단 위험)

심각도: DEBUG < INFO < WARNING < ERROR < CRITICAL
```

---

### 기본 설정

```python
import logging

# 로그 설정
logging.basicConfig(
    level=logging.INFO,                    # INFO 이상만 기록
    format='%(asctime)s [%(levelname)s] %(message)s',  # 형식
    handlers=[
        logging.FileHandler('monitor.log'),  # 파일에 기록
        logging.StreamHandler()              # 화면에도 출력
    ]
)

logger = logging.getLogger(__name__)
```

---

### 사용법

```python
logger.debug("디버그: CPU 측정 시작")         # 기록 안 됨 (INFO 이상만)
logger.info("정보: CPU 23.5% - 정상")         # ✅ 기록됨
logger.warning("경고: 메모리 78% - 주의")      # ✅ 기록됨
logger.error("에러: Slack 전송 실패")          # ✅ 기록됨
logger.critical("심각: 디스크 99% - 즉시 대응") # ✅ 기록됨
```

**로그 파일 출력 예시:**
```
2026-06-01 10:20:35,123 [INFO] CPU 23.5% - 정상
2026-06-01 10:25:35,456 [WARNING] 메모리 78.3% - 주의
2026-06-01 10:30:35,789 [ERROR] Slack 전송 실패: 연결 오류
```

---

### 로그 파일 크기 제한 (실무 패턴)

```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'monitor.log',
    maxBytes=5 * 1024 * 1024,  # 5MB 초과 시 새 파일
    backupCount=3               # 최대 3개 보관
)
# monitor.log, monitor.log.1, monitor.log.2, monitor.log.3
```

---

## 6. time·datetime — 주기 실행·시간 기록

### 주기적 실행

```python
import time

# 5분마다 실행
while True:
    check_server()            # 서버 확인
    time.sleep(5 * 60)        # 5분 대기 (300초)

# 시간 단위
time.sleep(1)       # 1초
time.sleep(60)      # 1분
time.sleep(300)     # 5분
time.sleep(3600)    # 1시간
```

---

### 현재 시간 기록

```python
from datetime import datetime

now = datetime.now()
print(now)                                    # 2026-06-01 10:20:35.123456
print(now.strftime("%Y-%m-%d %H:%M:%S"))     # 2026-06-01 10:20:35
print(now.strftime("%m/%d %H:%M"))           # 06/01 10:20

# 로그 메시지에 시간 포함
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
message = f"[{timestamp}] CPU 92.5% - 위험"
print(message)
```

---

## 7. 전체 통합 코드

아래가 PF3의 핵심 파일입니다. `monitor.py`로 저장하세요.

```python
# monitor.py
# PF3: 서버 이상 감지 + Slack 자동 알림 시스템

import psutil
import requests
import subprocess
import logging
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

# ──────────────────────────────────────
# 설정
# ──────────────────────────────────────
SLACK_WEBHOOK    = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
CPU_THRESHOLD    = 80.0
MEMORY_THRESHOLD = 85.0
DISK_THRESHOLD   = 80.0
CHECK_INTERVAL   = 300  # 5분 (초)

# ──────────────────────────────────────
# 로그 설정
# ──────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        RotatingFileHandler('monitor.log', maxBytes=5*1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ──────────────────────────────────────
# 1. 메트릭 수집
# ──────────────────────────────────────
def get_metrics():
    cpu    = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk   = psutil.disk_usage('/').percent
    return cpu, memory, disk

# ──────────────────────────────────────
# 2. Slack 알림
# ──────────────────────────────────────
def send_slack(message):
    try:
        response = requests.post(
            SLACK_WEBHOOK,
            json={"text": message},
            timeout=5
        )
        if response.status_code == 200:
            logger.info("Slack 알림 전송 완료")
        else:
            logger.error(f"Slack 전송 실패: {response.status_code}")
    except Exception as e:
        logger.error(f"Slack 오류: {e}")

# ──────────────────────────────────────
# 3. 임계값 확인
# ──────────────────────────────────────
def check_and_alert(cpu, memory, disk):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alerted = False

    if cpu > CPU_THRESHOLD:
        msg = f"🔴 CPU 위험\n시간: {now}\n현재: {cpu:.1f}% (임계값: {CPU_THRESHOLD}%)"
        logger.warning(f"CPU 위험: {cpu:.1f}%")
        send_slack(msg)
        alerted = True

    if memory > MEMORY_THRESHOLD:
        msg = f"🟡 메모리 경고\n시간: {now}\n현재: {memory:.1f}% (임계값: {MEMORY_THRESHOLD}%)"
        logger.warning(f"메모리 경고: {memory:.1f}%")
        send_slack(msg)
        alerted = True

    if disk > DISK_THRESHOLD:
        msg = f"⚠️ 디스크 주의\n시간: {now}\n현재: {disk:.1f}% (임계값: {DISK_THRESHOLD}%)"
        logger.warning(f"디스크 주의: {disk:.1f}%")
        send_slack(msg)
        alerted = True

    if not alerted:
        logger.info(f"정상 | CPU: {cpu:.1f}% | 메모리: {memory:.1f}% | 디스크: {disk:.1f}%")

# ──────────────────────────────────────
# 4. 메인 실행
# ──────────────────────────────────────
def main():
    logger.info("서버 모니터링 시작")
    logger.info(f"임계값 → CPU: {CPU_THRESHOLD}% | 메모리: {MEMORY_THRESHOLD}% | 디스크: {DISK_THRESHOLD}%")
    logger.info(f"점검 주기: {CHECK_INTERVAL}초 ({CHECK_INTERVAL//60}분)")

    # 1회 실행 (테스트)
    cpu, memory, disk = get_metrics()
    check_and_alert(cpu, memory, disk)

    # 주기적 실행 (while 루프)
    # 아래 주석 해제하면 5분마다 자동 실행
    # while True:
    #     cpu, memory, disk = get_metrics()
    #     check_and_alert(cpu, memory, disk)
    #     time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
```

---

### 실행 방법

```bash
# 1회 테스트 실행
python3 monitor.py

# 백그라운드에서 계속 실행 (while 루프 주석 해제 후)
nohup python3 monitor.py &

# 로그 실시간 확인
tail -f monitor.log
```

---

## 8. 자주 하는 실수

### 실수 1: interval=0 이면 CPU가 0.0
```python
# 잘못된 방법 (첫 호출 시 항상 0.0 반환)
cpu = psutil.cpu_percent(interval=0)

# 올바른 방법
cpu = psutil.cpu_percent(interval=1)  # 1초 기다림
```

### 실수 2: bytes를 GB로 변환 안 함
```python
# 잘못된 방법
print(psutil.virtual_memory().total)  # 8589934592 (bytes, 읽기 어려움)

# 올바른 방법
total_gb = psutil.virtual_memory().total / (1024 ** 3)
print(f"{total_gb:.1f}GB")  # 8.0GB
```

### 실수 3: Slack URL을 코드에 직접 입력
```python
# 나쁜 방법 (GitHub에 올리면 URL 노출!)
SLACK_WEBHOOK = "https://hooks.slack.com/services/실제URL"

# 좋은 방법: 환경변수 사용
import os
SLACK_WEBHOOK = os.environ.get("SLACK_WEBHOOK_URL", "")
# 터미널에서: export SLACK_WEBHOOK_URL="실제URL"
```

### 실수 4: 예외 처리 없이 requests 호출
```python
# 나쁜 방법 (네트워크 오류 시 프로그램 전체 중단)
requests.post(SLACK_WEBHOOK, json=payload)

# 좋은 방법 (try-except로 감싸기)
try:
    requests.post(SLACK_WEBHOOK, json=payload, timeout=5)
except Exception as e:
    logger.error(f"Slack 오류: {e}")
    # 프로그램은 계속 실행됨
```

---

## GitHub 커밋

```bash
git add monitor.py
git commit -m "feat: PF3 기초 - psutil 서버 메트릭 수집 + Slack 알림"
git push origin main
```

---

