# 📊 PF3 — 서버 이상 감지 + Slack 자동 알림 시스템

> **Server Anomaly Detection & Slack Alert Automation**  
> Python + Bash로 구현한 실시간 서버 모니터링 자동화 시스템

---

## 📌 프로젝트 배경

> "사람이 보지 않아도 자동으로 감지하고 즉시 알림을 보내는 시스템이 필요하다"

이 경험을 바탕으로 **서버 이상을 자동 감지하고 Slack으로 즉시 알림을 보내는 시스템**을 구현했다.

---

## ⚙️ 기술 스택

| 도구 | 역할 |
|------|------|
| Python 3 | 메트릭 수집·로그 분석 엔진 |
| psutil | CPU·메모리·디스크 수집 |
| requests | Slack Webhook HTTP 요청 |
| logging | 구조화된 로그 기록 |
| Bash | 서버 상태 점검 스크립트 |
| Slack Webhook | 실시간 알림 수신 |

---

## 🏗️ 시스템 아키텍처

```
┌─────────────────────────────────────────────────────┐
│                    서버 (Linux/WSL2)                  │
│                                                       │
│  ┌─────────────┐      ┌──────────────────────────┐   │
│  │ monitor.sh  │      │      monitor.py           │   │
│  │  (Bash)     │      │      (Python)             │   │
│  │ CPU/MEM/    │      │ psutil → 메트릭 수집      │   │
│  │ DISK 수집   │      │ 5분마다 자동 실행         │   │
│  └──────┬──────┘      └──────────┬───────────────┘   │
│         │                        │                    │
│         ▼                        ▼                    │
│  monitor_bash.log         monitor.log                 │
│                                  │                    │
│                       ┌──────────▼───────────────┐   │
│                       │    log_analyzer.py        │   │
│                       │  변경 감지 → 자동 분석    │   │
│                       │  report.txt 생성          │   │
│                       └──────────────────────────┘   │
│                                                       │
│  cleanup.sh → 7일 이상 .log 파일 자동 삭제            │
└─────────────────────────────────────────────────────┘
                    │ 임계값 초과 시
                    │ HTTP POST
                    ▼
         ┌──────────────────┐
         │   Slack 채널     │
         │  🔴 CPU 위험!   │
         │  현재: 92.5%    │
         └──────────────────┘
```

---

## 📁 파일 구조

```
PF3/
├── monitor.py          # Python 메트릭 수집 + Slack 알림
├── log_analyzer.py     # 로그 실시간 분석 + 리포트 생성
├── monitor.sh          # Bash 서버 상태 점검
├── cleanup.sh          # 오래된 로그 자동 삭제
├── monitor.log         # Python 로그 (자동 생성)
├── monitor_bash.log    # Bash 로그 (자동 생성)
└── report.txt          # 분석 리포트 (자동 생성)
```

---

## 🚀 실행 방법

### 1. 패키지 설치

```bash
pip install psutil requests
```

### 2. Slack Webhook 설정

```
api.slack.com/apps → Create New App
→ Incoming Webhooks → ON
→ Add New Webhook → 채널 선택
→ URL 복사
```

`monitor.py` 상단에 URL 입력:

```python
SLACK_WEBHOOK = "https://hooks.slack.com/services/YOUR/URL"
```

### 3. 실행 권한 부여

```bash
chmod +x monitor.sh cleanup.sh
```

### 4. 실행

```bash
# Python 모니터링 (1회 실행)
python3 monitor.py

# 로그 실시간 분석
python3 log_analyzer.py

# Bash 서버 점검
./monitor.sh

# 오래된 로그 정리
./cleanup.sh
```

---

## 📋 핵심 기능 4가지

### ① Python 메트릭 수집 + Slack 알림 (`monitor.py`)

```python
CPU_THRESHOLD    = 80.0  # CPU 80% 초과 시 알림
MEMORY_THRESHOLD = 85.0  # 메모리 85% 초과 시 알림
DISK_THRESHOLD   = 80.0  # 디스크 80% 초과 시 알림
CHECK_INTERVAL   = 300   # 5분마다 자동 실행
```

- `psutil`로 CPU·메모리·디스크 수치 수집
- 임계값 초과 시 Slack Webhook으로 즉시 알림
- `RotatingFileHandler`로 로그 파일 크기 자동 관리 (최대 5MB × 3개)

**실행 결과:**

```
2026-06-06 10:20:35 [INFO] 서버 모니터링 시작
2026-06-06 10:20:36 [INFO] 정상 | CPU: 3.0% | 메모리: 26.0% | 디스크: 1.0%
```

---

### ② 로그 실시간 분석 + 리포트 (`log_analyzer.py`)

- `os.path.getmtime()`으로 10초마다 로그 파일 변경 감지
- 변경 감지 시 자동으로 로그 파싱·분석·리포트 생성
- `report.txt`에 통계·경고패턴·평균 수치 자동 저장

**report.txt 예시:**

```
========================================
  서버 모니터링 로그 분석 리포트
  생성일시: 2026-06-06 10:25:00
========================================

[ 전체 통계 ]
  총 로그 라인: 12줄
  정상 (INFO):  10건
  경고 (WARN):  2건
  에러 (ERROR): 0건

[ 경고 패턴 분석 ]
  CPU 초과:    2회
  메모리 초과: 0회
  디스크 초과: 0회
========================================
```

---

### ③ Bash 서버 상태 점검 (`monitor.sh`)

- `top·free·df` 명령어로 서버 메트릭 수집
- 임계값 초과 시 로그 기록
- `tee -a`로 화면 출력 + 파일 기록 동시

**실행 결과:**

```
================================================
  서버 상태 점검 (2026-06-06 10:20:35)
================================================
[2026-06-06 10:20:35] CPU: 3% | MEM: 26% | DISK: 1%
[2026-06-06 10:20:35] ✅ 모든 지표 정상
================================================
```

---

### ④ 오래된 로그 자동 삭제 (`cleanup.sh`)

```bash
./cleanup.sh       # 7일 이상 된 .log 삭제 (기본값)
./cleanup.sh 14    # 14일 이상 된 .log 삭제
```

- `find -mtime`으로 오래된 로그 파일 탐색
- 자동 삭제로 디스크 공간 관리

---

## 💡 구현하면서 배운 것

```
1. psutil vs subprocess
   → psutil이 파싱 필요 없고 크로스 플랫폼 지원으로 선택

2. RotatingFileHandler 필요성
   → 24시간 실행 시 로그 무한 증가 문제 해결

3. os.path.getmtime() 변경 감지
   → 파일 내용 비교보다 수정 시간 비교가 훨씬 빠름

4. try/except로 Slack 오류 처리
   → 네트워크 오류 시 프로그램 중단 방지
```

---

## 🔧 임계값 설정

`monitor.py` 상단에서 조정:

```python
CPU_THRESHOLD    = 80.0  # CPU 임계값 (%)
MEMORY_THRESHOLD = 85.0  # 메모리 임계값 (%)
DISK_THRESHOLD   = 80.0  # 디스크 임계값 (%)
CHECK_INTERVAL   = 300   # 점검 주기 (초)
```

---

## 📌 개발 환경

```
OS:      Ubuntu 22.04 (WSL2)
Python:  3.10+
Shell:   Bash
IDE:     VSCode (Remote WSL)
```

---