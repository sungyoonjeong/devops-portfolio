# 📊 PF3 — 서버 이상 감지 + Slack 자동 알림 시스템
> 완전 정리 문서 | 코드 설명 포함 | 2026.06.06

---

## 목차
1. [프로젝트 개요](#1-프로젝트-개요)
2. [시스템 아키텍처](#2-시스템-아키텍처)
3. [파일 구조](#3-파일-구조)
4. [환경 설정](#4-환경-설정)
5. [monitor.py — Python 메트릭 수집 + Slack 알림](#5-monitorpy--python-메트릭-수집--slack-알림)
6. [log_analyzer.py — 로그 분석 + 리포트 생성](#6-log_analyzerpy--로그-분석--리포트-생성)
7. [monitor.sh — Bash 서버 상태 점검](#7-monitorsh--bash-서버-상태-점검)
8. [cleanup.sh — 오래된 로그 자동 삭제](#8-cleanupsh--오래된-로그-자동-삭제)
9. [전체 실행 방법](#9-전체-실행-방법)
10. [면접 설명 스크립트](#10-면접-설명-스크립트)
11. [트러블슈팅](#11-트러블슈팅)

---

## 1. 프로젝트 개요

### 만든 이유 (스토리)

```
자동으로 감지하고 즉시 알림을 보내는 시스템 만들어보고 싶었음
→ PF3 제작
```

### 핵심 기능 4가지

```
① Python으로 CPU·메모리·디스크 수치를 5분마다 수집
② 임계값 초과 시 Slack으로 즉시 알림 발송
③ 로그 파일 실시간 분석 + 패턴 감지 + 리포트 자동 생성
④ Bash로 서버 상태 수집 + 오래된 로그 자동 정리
```

### 기술 스택

| 도구 | 역할 |
|------|------|
| Python 3 | 메트릭 수집·분석 엔진 |
| psutil | 시스템 정보(CPU·메모리·디스크) 수집 라이브러리 |
| requests | Slack Webhook HTTP 요청 |
| re (정규식) | 로그 파싱·패턴 추출 |
| logging | 구조화된 로그 기록 |
| Bash | 서버 상태 점검 스크립트 |
| Slack Webhook | 실시간 알림 수신 |

---

## 2. 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                    서버 (WSL2/Linux)                  │
│                                                       │
│  ┌─────────────┐      ┌──────────────────────────┐   │
│  │ monitor.sh  │      │      monitor.py           │   │
│  │  (Bash)     │      │      (Python)             │   │
│  │             │      │                          │   │
│  │ CPU/MEM/    │      │ psutil → 메트릭 수집     │   │
│  │ DISK 수집   │      │ 임계값 확인              │   │
│  └──────┬──────┘      └──────────┬───────────────┘   │
│         │                        │                    │
│         ▼                        ▼                    │
│  ┌─────────────┐      ┌──────────────────────────┐   │
│  │monitor_bash │      │      monitor.log          │   │
│  │   .log      │      │  (구조화된 로그)           │   │
│  └─────────────┘      └──────────┬───────────────┘   │
│                                  │                    │
│                       ┌──────────▼───────────────┐   │
│                       │    log_analyzer.py        │   │
│                       │                          │   │
│                       │  로그 분석·패턴 감지      │   │
│                       │  report.txt 생성          │   │
│                       └──────────────────────────┘   │
│                                                       │
│  ┌─────────────┐                                      │
│  │ cleanup.sh  │ → 7일 이상 된 .log 파일 자동 삭제    │
│  └─────────────┘                                      │
└─────────────────────────────────────────────────────┘
                          │
                          │ HTTP POST (Slack Webhook)
                          ▼
               ┌──────────────────┐
               │   Slack 채널     │
               │  🔴 CPU 위험!   │
               │  현재: 92.5%    │
               └──────────────────┘
```

### 데이터 흐름

```
1. monitor.py 실행 (5분마다 자동)
   → psutil로 CPU·메모리·디스크 수집
   → monitor.log에 기록
   → 임계값 초과 시 Slack 알림 발송

2. log_analyzer.py 실행 (로그 변경 감지 시 자동)
   → monitor.log 읽기
   → 통계·패턴 분석
   → report.txt 생성

3. monitor.sh 실행 (수동 또는 cron)
   → Bash 명령어로 서버 상태 수집
   → monitor_bash.log에 기록

4. cleanup.sh 실행 (수동 또는 cron)
   → 7일 이상 된 .log 파일 찾기
   → 자동 삭제
```

---

## 3. 파일 구조

```
devops-portfolio/
└── PortFolio/
    └── PF3/
        ├── monitor.py          ← Python 메트릭 수집 + Slack 알림
        ├── log_analyzer.py     ← 로그 분석 + 리포트 생성
        ├── monitor.sh          ← Bash 서버 상태 점검
        ├── cleanup.sh          ← 오래된 로그 자동 삭제
        ├── monitor.log         ← Python 로그 (자동 생성)
        ├── monitor_bash.log    ← Bash 로그 (자동 생성)
        └── report.txt          ← 분석 리포트 (자동 생성)
```

---

## 4. 환경 설정

### 필수 패키지 설치

```bash
pip install psutil requests
```

### Slack Webhook 설정

```
1. slack.com 로그인
2. api.slack.com/apps 접속
3. Create New App → From scratch
4. App Name: "서버모니터링"
5. Incoming Webhooks → Activate → ON
6. Add New Webhook to Workspace
7. 채널 선택 (#실습) → Allow
8. Webhook URL 복사
   https://hooks.slack.com/services/T.../B.../...
```

### monitor.py에 URL 입력

```python
SLACK_WEBHOOK = "https://hooks.slack.com/services/복사한URL"
```

### 실행 권한 부여

```bash
chmod +x monitor.sh cleanup.sh
```

---

## 5. monitor.py — Python 메트릭 수집 + Slack 알림

### 전체 코드 + 한 줄 주석

```python
# ============================================================
# monitor.py
# 목적: 서버 CPU·메모리·디스크를 감지하고 Slack으로 알림 발송
# 실행: python3 monitor.py
# ============================================================

import psutil        # 시스템 정보(CPU·메모리·디스크) 읽는 외부 라이브러리
import requests      # HTTP 요청 보내는 외부 라이브러리 (Slack POST 요청)
import logging       # 로그를 파일과 화면에 기록하는 Python 기본 내장 모듈
import time          # time.sleep()으로 일정 시간 대기할 때 사용
from datetime import datetime          # 현재 시간 가져올 때 사용
from logging.handlers import RotatingFileHandler  # 로그 파일 크기 제한 기능

# ── 설정값 ──────────────────────────────────────────────────
SLACK_WEBHOOK    = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
CPU_THRESHOLD    = 80.0  # CPU 80% 넘으면 알림
MEMORY_THRESHOLD = 85.0  # 메모리 85% 넘으면 알림
DISK_THRESHOLD   = 80.0  # 디스크 80% 넘으면 알림
CHECK_INTERVAL   = 300   # 300초 = 5분마다 점검

# ── 로그 설정 ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,  # INFO 이상(INFO·WARNING·ERROR)만 기록
    format='%(asctime)s [%(levelname)s] %(message)s',
    # %(asctime)s   = 시간 (2026-06-06 10:20:35,123)
    # %(levelname)s = 로그 레벨 (INFO, WARNING 등)
    # %(message)s   = 실제 메시지
    handlers=[
        RotatingFileHandler(
            'monitor.log',              # 로그 파일 이름
            maxBytes=5 * 1024 * 1024,   # 최대 5MB
            backupCount=3               # 최대 3개 파일 보관
        ),
        logging.StreamHandler()         # 터미널에도 동시 출력
    ]
)
logger = logging.getLogger(__name__)  # 이 파일 전용 로거 객체 생성


def get_metrics():
    """CPU·메모리·디스크 사용률 측정해서 반환"""
    cpu    = psutil.cpu_percent(interval=1)    # 1초 동안 측정 (0이면 오차)
    memory = psutil.virtual_memory().percent   # 전체 메모리 중 사용률
    disk   = psutil.disk_usage('/').percent    # 루트(/) 디스크 사용률
    return cpu, memory, disk


def send_slack(message):
    """Slack Webhook으로 메시지 전송 (에러 처리 포함)"""
    try:
        response = requests.post(
            SLACK_WEBHOOK,
            json={"text": message},   # Slack이 요구하는 JSON 형식
            timeout=5                  # 5초 안에 응답 없으면 포기
        )
        if response.status_code == 200:
            logger.info("Slack 알림 전송 완료")
        else:
            logger.error(f"Slack 전송 실패: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.error("네트워크 연결 오류 - Slack 전송 실패")
    except requests.exceptions.Timeout:
        logger.error("요청 시간 초과 - Slack 전송 실패")
    except Exception as e:
        logger.error(f"알 수 없는 오류: {e}")


def check_and_alert(cpu, memory, disk):
    """임계값 초과 시 로그 기록 + Slack 알림 발송"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 현재 시각 문자열
    alerted = False  # 알림 발생 여부 추적

    if cpu > CPU_THRESHOLD:
        msg = f"🔴 CPU 위험 알림\n시간: {now}\n현재: {cpu:.1f}% (임계값: {CPU_THRESHOLD}%)"
        logger.warning(f"CPU 위험: {cpu:.1f}%")
        send_slack(msg)
        alerted = True

    if memory > MEMORY_THRESHOLD:
        msg = f"🟡 메모리 경고\n시간: {now}\n현재: {memory:.1f}% (임계값: {MEMORY_THRESHOLD}%)"
        logger.warning(f"메모리 경고: {memory:.1f}%")
        send_slack(msg)
        alerted = True

    if disk > DISK_THRESHOLD:
        msg = f"⚠️  디스크 주의\n시간: {now}\n현재: {disk:.1f}% (임계값: {DISK_THRESHOLD}%)"
        logger.warning(f"디스크 주의: {disk:.1f}%")
        send_slack(msg)
        alerted = True

    if not alerted:  # 세 지표 모두 정상이면
        logger.info(f"정상 | CPU: {cpu:.1f}% | 메모리: {memory:.1f}% | 디스크: {disk:.1f}%")


def main():
    """프로그램 시작점"""
    logger.info("=" * 50)
    logger.info("서버 모니터링 시작")
    logger.info(f"임계값 → CPU: {CPU_THRESHOLD}% | 메모리: {MEMORY_THRESHOLD}% | 디스크: {DISK_THRESHOLD}%")
    logger.info(f"점검 주기: {CHECK_INTERVAL}초 ({CHECK_INTERVAL // 60}분)")
    logger.info("=" * 50)

    # 1회 즉시 실행 (테스트)
    cpu, memory, disk = get_metrics()
    check_and_alert(cpu, memory, disk)

    # 5분마다 반복 실행 (주석 해제하면 활성화)
    # while True:
    #     cpu, memory, disk = get_metrics()
    #     check_and_alert(cpu, memory, disk)
    #     time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
```

### 핵심 개념 설명

**psutil.cpu_percent(interval=1)**
```
interval=1: 1초 동안 측정
interval=0: 이전 호출 이후 사용률 (첫 호출 시 0.0 반환 → 사용 금지)
반환값: float (예: 23.5)
```

**RotatingFileHandler**
```
maxBytes=5MB: 파일이 5MB 초과 시 새 파일 생성
backupCount=3: monitor.log, monitor.log.1, monitor.log.2 최대 3개 보관
→ 로그 파일이 무한정 커지는 것 방지
```

**requests.post(timeout=5)**
```
timeout=5: 5초 안에 응답 없으면 포기
→ Slack 서버 문제 시 프로그램이 무한 대기하는 것 방지
```

---

## 6. log_analyzer.py — 로그 분석 + 리포트 생성

### 전체 코드 + 한 줄 주석

```python
# ============================================================
# log_analyzer.py
# 목적: monitor.log를 실시간 감지하고 자동 분석·리포트 생성
# 실행: python3 log_analyzer.py
# ============================================================

import re           # 정규식 - 로그에서 숫자 패턴 추출
import os           # 파일 존재 확인, 수정 시간 체크
import time         # time.sleep()으로 주기적 실행
from datetime import datetime
from collections import Counter  # 빈도 계산 (확장 여지)

LOG_FILE       = 'monitor.log'   # 분석할 로그 파일
REPORT_FILE    = 'report.txt'    # 결과 저장 파일
CHECK_INTERVAL = 10              # 10초마다 파일 변경 확인


def read_log(filepath):
    """로그 파일 읽어서 줄 단위 리스트 반환"""
    if not os.path.exists(filepath):       # 파일 없으면
        print(f"❌ 로그 파일 없음: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [l.strip() for l in lines if l.strip()]  # 빈 줄 제거


def classify_logs(lines):
    """INFO·WARNING·ERROR로 분류"""
    info     = [l for l in lines if '[INFO]'    in l]  # 정상 로그
    warnings = [l for l in lines if '[WARNING]' in l]  # 경고 로그
    errors   = [l for l in lines if '[ERROR]'   in l]  # 에러 로그
    return info, warnings, errors


def analyze_warnings(warnings):
    """어떤 지표가 몇 번 초과됐는지 카운트"""
    cpu_count  = sum(1 for w in warnings if 'CPU'    in w)
    mem_count  = sum(1 for w in warnings if '메모리' in w)
    disk_count = sum(1 for w in warnings if '디스크' in w)
    return {'CPU': cpu_count, '메모리': mem_count, '디스크': disk_count}


def extract_metrics(info_lines):
    """INFO 로그에서 CPU·메모리·디스크 수치 추출"""
    cpu_vals, mem_vals, disk_vals = [], [], []
    for line in info_lines:
        if '정상' in line and 'CPU' in line:
            try:
                # r'CPU: ([\d.]+)%' = 정규식 패턴
                # [\d.]+  = 숫자와 점으로 된 문자 1개 이상
                # ()      = 이 부분만 캡처
                # .group(1) = 캡처된 숫자 부분만 추출
                cpu  = float(re.search(r'CPU: ([\d.]+)%',   line).group(1))
                mem  = float(re.search(r'메모리: ([\d.]+)%', line).group(1))
                disk = float(re.search(r'디스크: ([\d.]+)%', line).group(1))
                cpu_vals.append(cpu)
                mem_vals.append(mem)
                disk_vals.append(disk)
            except (AttributeError, ValueError):
                continue  # 파싱 실패 시 건너뜀
    return cpu_vals, mem_vals, disk_vals


def generate_report(lines, info, warnings, errors, pattern, cpu_vals, mem_vals, disk_vals):
    """모든 분석 결과를 리포트 문자열로 조합"""
    now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    avg_cpu  = sum(cpu_vals)  / len(cpu_vals)  if cpu_vals  else 0  # 빈 리스트면 0
    avg_mem  = sum(mem_vals)  / len(mem_vals)  if mem_vals  else 0
    avg_disk = sum(disk_vals) / len(disk_vals) if disk_vals else 0

    report = f"""
========================================
  서버 모니터링 로그 분석 리포트
  생성일시: {now}
========================================

[ 전체 통계 ]
  총 로그 라인: {len(lines)}줄
  정상 (INFO):  {len(info)}건
  경고 (WARN):  {len(warnings)}건
  에러 (ERROR): {len(errors)}건

[ 평균 수치 ]
  CPU 평균:    {avg_cpu:.1f}%
  메모리 평균: {avg_mem:.1f}%
  디스크 평균: {avg_disk:.1f}%

[ 경고 패턴 분석 ]
  CPU 초과:    {pattern['CPU']}회
  메모리 초과: {pattern['메모리']}회
  디스크 초과: {pattern['디스크']}회
"""
    if warnings:
        report += "\n[ 최근 경고 내역 ]\n"
        for w in warnings[-3:]:  # 마지막 3건만
            report += f"  {w}\n"
    else:
        report += "\n[ 최근 경고 내역 ]\n  없음\n"

    if errors:
        report += "\n[ 최근 에러 내역 ]\n"
        for e in errors[-3:]:
            report += f"  {e}\n"
    else:
        report += "\n[ 최근 에러 내역 ]\n  없음\n"

    report += "\n========================================"
    return report


def analyze_once():
    """한 번 분석 실행"""
    lines = read_log(LOG_FILE)
    if not lines:
        return

    info, warnings, errors        = classify_logs(lines)
    pattern                       = analyze_warnings(warnings)
    cpu_vals, mem_vals, disk_vals = extract_metrics(info)
    report = generate_report(
        lines, info, warnings, errors,
        pattern, cpu_vals, mem_vals, disk_vals
    )

    print(report)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:  # 'w' = 덮어쓰기
        f.write(report)
    print(f"✅ 리포트 업데이트: {REPORT_FILE}")


def main():
    """파일 변경 감지 → 자동 재분석 루프"""
    print("📊 로그 분석기 시작")
    print(f"   확인 주기: {CHECK_INTERVAL}초 | Ctrl+C 로 종료\n")

    last_modified = 0  # 마지막 확인 수정 시간 (처음엔 0 → 무조건 첫 분석)

    while True:
        try:
            if os.path.exists(LOG_FILE):
                current_modified = os.path.getmtime(LOG_FILE)
                # os.path.getmtime(): 파일 마지막 수정 시간 (타임스탬프)

                if current_modified != last_modified:
                    # 수정 시간이 달라졌으면 = 파일이 변경됨
                    print(f"\n🔄 로그 변경 감지 → 재분석 중...")
                    analyze_once()
                    last_modified = current_modified
                else:
                    now = datetime.now().strftime("%H:%M:%S")
                    print(f"[{now}] 변경 없음 — {CHECK_INTERVAL}초 후 재확인", end='\r')
                    # end='\r': 같은 줄을 계속 덮어씀 (깔끔한 대기 표시)
            else:
                print(f"⏳ {LOG_FILE} 대기 중...", end='\r')

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            # Ctrl+C 누르면 여기서 처리
            print("\n\n🛑 로그 분석기 종료")
            break


if __name__ == "__main__":
    main()
```

---

## 7. monitor.sh — Bash 서버 상태 점검

### 전체 코드 + 한 줄 주석

```bash
#!/bin/bash
# ============================================================
# monitor.sh
# 목적: Bash로 서버 CPU·메모리·디스크 수집·출력·기록
# 실행: ./monitor.sh
# ============================================================

# ── 설정 ─────────────────────────────────────────────────────
CPU_THRESHOLD=80      # CPU 경고 임계값
MEM_THRESHOLD=85      # 메모리 경고 임계값
DISK_THRESHOLD=80     # 디스크 경고 임계값
LOG_FILE="monitor_bash.log"  # Python 로그와 구분하기 위해 별도 파일

# ── 현재 시각 ─────────────────────────────────────────────────
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
# $(): 명령어 실행 결과를 변수에 저장
# date "+형식": 날짜를 원하는 형식으로 출력

# ── CPU 사용률 수집 ───────────────────────────────────────────
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
# top -bn1   : 1회만 실행 (-b 배치모드, -n1 1번 실행)
# grep Cpu(s): "Cpu(s):" 포함된 줄만 추출
# awk '{print $2}': 공백 기준 2번째 컬럼 (사용률)
# cut -d. -f1: 점(.) 기준으로 나눠서 첫 번째 부분 (정수만)

# ── 메모리 사용률 수집 ────────────────────────────────────────
MEM=$(free | grep Mem | awk '{printf("%.0f", $3/$2*100)}')
# free      : 메모리 전체 정보 출력
# grep Mem  : Mem 줄만 추출 (Mem, Swap 중)
# $3/$2*100 : 사용량($3) / 전체($2) × 100 = 사용률(%)
# %.0f      : 소수점 없이 정수로 출력

# ── 디스크 사용률 수집 ────────────────────────────────────────
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
# df /      : 루트(/) 디렉토리의 디스크 정보
# tail -1   : 마지막 줄 (헤더 제외, 실제 데이터)
# $5        : 5번째 컬럼 = 사용률 (예: "45%")
# tr -d '%' : '%' 문자 제거 → 숫자만 (예: "45")

# ── 로그 기록 함수 ────────────────────────────────────────────
log() {
    echo "[$TIMESTAMP] $1" | tee -a $LOG_FILE
    # $1: 함수에 전달된 첫 번째 인수 (메시지)
    # tee -a: 화면 출력 + 파일 이어쓰기(-a) 동시
}

# ── 상태 출력 ─────────────────────────────────────────────────
echo "================================================"
echo "  서버 상태 점검 ($TIMESTAMP)"
echo "================================================"

log "CPU: ${CPU}% | MEM: ${MEM}% | DISK: ${DISK}%"
# ${변수}: 변수 사용 (중괄호로 경계 명확히)

# ── 임계값 체크 ───────────────────────────────────────────────
ALERTED=false   # 알림 발생 여부 (false로 초기화)

if [ "$CPU" -gt "$CPU_THRESHOLD" ] 2>/dev/null; then
    # [ ]: 조건 검사 (양쪽 공백 필수)
    # -gt: greater than (>)
    # 2>/dev/null: 에러 메시지 숨기기
    log "🔴 CPU 위험: ${CPU}% (임계값: ${CPU_THRESHOLD}%)"
    ALERTED=true
fi

if [ "$MEM" -gt "$MEM_THRESHOLD" ] 2>/dev/null; then
    log "🟡 메모리 위험: ${MEM}% (임계값: ${MEM_THRESHOLD}%)"
    ALERTED=true
fi

if [ "$DISK" -gt "$DISK_THRESHOLD" ] 2>/dev/null; then
    log "⚠️  디스크 위험: ${DISK}% (임계값: ${DISK_THRESHOLD}%)"
    ALERTED=true
fi

# ── 정상일 때 ─────────────────────────────────────────────────
if [ "$ALERTED" = false ]; then
    # = : 문자열 비교 (숫자는 -eq, 문자열은 =)
    log "✅ 모든 지표 정상"
fi

echo "================================================"
echo "  로그 저장: $LOG_FILE"
echo "================================================"
```

---

## 8. cleanup.sh — 오래된 로그 자동 삭제

### 전체 코드 + 한 줄 주석

```bash
#!/bin/bash
# ============================================================
# cleanup.sh
# 목적: 오래된 .log 파일 자동 삭제 (디스크 공간 절약)
# 실행: ./cleanup.sh          (기본 7일)
#       ./cleanup.sh 14       (14일 이상 삭제)
# ============================================================

# ── 설정 ─────────────────────────────────────────────────────
LOG_DIR="."         # 정리할 디렉토리 (현재 폴더)
DAYS=${1:-7}        # 삭제 기준 일수
# ${1:-7}: 첫 번째 인수($1)가 있으면 사용, 없으면 기본값 7

TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# ── 시작 로그 ─────────────────────────────────────────────────
echo "[$TIMESTAMP] 로그 정리 시작 (${DAYS}일 이상 파일 삭제)"

# ── 오래된 파일 찾기 ──────────────────────────────────────────
OLD_FILES=$(find "$LOG_DIR" -name "*.log" -mtime +"$DAYS" 2>/dev/null)
# find              : 파일 탐색 명령어
# "$LOG_DIR"        : 탐색 시작 경로
# -name "*.log"     : 이름이 *.log인 파일만
# -mtime +"$DAYS"   : 수정된 지 $DAYS일 초과한 파일
# 2>/dev/null       : 권한 오류 등 에러 메시지 숨기기

# ── 삭제할 파일 없으면 종료 ───────────────────────────────────
if [ -z "$OLD_FILES" ]; then
    # -z: 문자열 길이가 0이면 (비어있으면) true
    echo "[$TIMESTAMP] 삭제할 파일 없음"
    exit 0   # 종료 코드 0 = 정상 종료
fi

# ── 파일 삭제 ─────────────────────────────────────────────────
COUNT=0

echo "$OLD_FILES" | while read FILE; do
    # while read: 한 줄씩 읽어서 FILE 변수에 저장
    if [ -f "$FILE" ]; then
        # -f: 일반 파일이면 (디렉토리 제외)
        echo "[$TIMESTAMP] 삭제: $FILE"
        rm "$FILE"      # 파일 삭제
        COUNT=$((COUNT + 1))  # 카운터 증가
    fi
done

# ── 완료 ─────────────────────────────────────────────────────
echo "[$TIMESTAMP] 정리 완료"
```

---

## 9. 전체 실행 방법

### 기본 실행 (각각 독립 실행)

```bash
cd ~/devops-portfolio/PortFolio/PF3

# 1. Python 모니터링 (1회 실행)
python3 monitor.py

# 2. 로그 분석기 (실시간 감지 모드)
python3 log_analyzer.py

# 3. Bash 서버 상태 점검 (1회 실행)
./monitor.sh

# 4. 오래된 로그 정리
./cleanup.sh
./cleanup.sh 14   # 14일 이상 삭제
```

### 터미널 2개로 동시 실행

```bash
# 터미널 1: Python 모니터링 (5분마다 자동)
# monitor.py의 while 루프 주석 해제 후 실행
python3 monitor.py

# 터미널 2: 로그 분석기 (변경 감지 시 자동 분석)
python3 log_analyzer.py
```

### 임계값 낮춰서 Slack 테스트

```python
# monitor.py에서 임시로 낮추기
CPU_THRESHOLD    = 1.0
MEMORY_THRESHOLD = 1.0
DISK_THRESHOLD   = 1.0
# 실행 → Slack 알림 오는지 확인
# 확인 후 원래 값(80·85·80)으로 복구
```

### 생성되는 파일 확인

```bash
# 로그 파일 실시간 확인
tail -f monitor.log
tail -f monitor_bash.log

# 리포트 확인
cat report.txt

# 전체 파일 확인
ls -la
```

---

```
"Python의 psutil 라이브러리로 5분마다 CPU·메모리·디스크를
 수집하고, 임계값 초과 시 Slack Webhook으로 즉시 알림을
 보냅니다. log_analyzer가 로그를 실시간으로 분석해서
 패턴을 감지하고 리포트를 자동 생성합니다."
```

###

**Q. psutil을 왜 사용했나?**
```
"Python에서 OS 종속적인 시스템 정보(CPU·메모리·디스크)를
 한 줄로 읽을 수 있게 해주는 라이브러리입니다.
 subprocess로 top·free 명령어를 실행하는 것보다
 파싱이 필요 없고 크로스 플랫폼(Linux·Mac·Windows)에서
 동일하게 동작해서 선택했습니다."
```

**Q. Slack Webhook이 뭔가?**
```
"Slack에서 제공하는 HTTP 기반 알림 API입니다.
 특정 URL로 JSON 형식의 POST 요청을 보내면
 지정된 채널에 메시지가 도착합니다.
 requests.post()로 한 줄에 구현 가능해서 적용했습니다."
```

**Q. RotatingFileHandler를 사용한 이유는?**
```
"24시간 서버를 모니터링하면 로그 파일이 무한히 커집니다.
 RotatingFileHandler는 파일이 5MB를 넘으면
 자동으로 새 파일을 만들고 최대 3개까지 보관합니다.
 이를 통해 디스크 공간을 효율적으로 관리했습니다."
```

**Q. log_analyzer의 실시간 감지 원리는?**
```
"os.path.getmtime()으로 파일의 마지막 수정 시간을
 10초마다 체크합니다. 이전에 기록한 수정 시간과 다르면
 파일이 변경된 것이므로 자동으로 재분석합니다.
 파일 내용을 매번 읽어서 비교하는 것보다 빠릅니다."
```

---

## 11. 트러블슈팅

### 문제 1: Slack 알림이 안 옴

```bash
# Webhook URL 확인
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"테스트"}' \
  https://hooks.slack.com/services/YOUR/URL

# 200 응답이면 URL 정상
# 404·403이면 URL 재발급 필요
```

### 문제 2: CPU 값이 0.0으로 나옴

```python
# 잘못된 방법
cpu = psutil.cpu_percent(interval=0)  # 첫 호출 시 항상 0.0

# 올바른 방법
cpu = psutil.cpu_percent(interval=1)  # 1초 기다린 후 측정
```

### 문제 3: monitor.sh에서 CPU 값이 안 나옴

```bash
# WSL2에서 top 명령어 출력 형식이 다를 수 있음
# 직접 확인
top -bn1 | grep -i "cpu"

# 출력에 맞게 grep·awk 패턴 수정
CPU=$(top -bn1 | grep "%Cpu" | awk '{print $2}' | cut -d. -f1)
```

### 문제 4: cleanup.sh 실행 시 권한 오류

```bash
chmod +x cleanup.sh   # 실행 권한 부여
./cleanup.sh
```

### 문제 5: 한글 깨짐

```python
# 파일 열 때 encoding 명시
with open(filepath, 'r', encoding='utf-8') as f:
    ...
with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    ...
```

---
