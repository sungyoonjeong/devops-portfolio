#!/bin/bash
# ============================================================
# monitor.sh
# 목적: 서버 CPU·메모리·디스크 상태를 Bash로 수집·출력·기록
# 실행: ./monitor.sh
# PF3: Python monitor.py와 함께 사용
# ============================================================

# ── 설정 ─────────────────────────────────────────────────────
CPU_THRESHOLD=80      # CPU 경고 임계값 (%)
MEM_THRESHOLD=85      # 메모리 경고 임계값 (%)
DISK_THRESHOLD=80     # 디스크 경고 임계값 (%)
LOG_FILE="monitor_bash.log"  # 로그 파일 (Python과 구분)

# ── 현재 시각 ─────────────────────────────────────────────────
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
# date: 현재 날짜·시간 출력 명령어
# "+%Y-%m-%d %H:%M:%S": 형식 지정 → 2026-06-06 10:20:35

# ── 메트릭 수집 ───────────────────────────────────────────────

# CPU 사용률
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
# top -bn1   : 1회만 실행 (-b 배치모드, -n1 1번)
# grep Cpu(s): CPU 정보 줄만 추출
# awk {print $2}: 두 번째 컬럼 (사용률 숫자) 추출
# cut -d. -f1: 소수점 앞 정수만 (예: 23.5 → 23)

# 메모리 사용률
MEM=$(free | grep Mem | awk '{printf("%.0f", $3/$2*100)}')
# free      : 메모리 정보 출력
# grep Mem  : Mem 줄만 추출
# $3/$2*100 : 사용량/전체*100 = 사용률(%)
# %.0f      : 소수점 없이 정수로

# 디스크 사용률 (루트 기준)
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
# df /      : 루트 디렉토리 디스크 정보
# tail -1   : 마지막 줄 (실제 데이터)
# $5        : 5번째 컬럼 (사용률)
# tr -d '%' : % 문자 제거 → 숫자만

# ── 로그 기록 함수 ────────────────────────────────────────────
log() {
    echo "[$TIMESTAMP] $1" | tee -a $LOG_FILE
    # echo: 화면 출력
    # tee -a: 화면 출력 + 파일에 이어쓰기 동시
}

# ── 상태 출력 ─────────────────────────────────────────────────
echo "================================================"
echo "  서버 상태 점검 ($TIMESTAMP)"
echo "================================================"

log "CPU: ${CPU}% | MEM: ${MEM}% | DISK: ${DISK}%"

# ── 임계값 체크 ───────────────────────────────────────────────
ALERTED=false   # 알림 발생 여부 추적

if [ "$CPU" -gt "$CPU_THRESHOLD" ] 2>/dev/null; then
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

# 정상일 때
if [ "$ALERTED" = false ]; then
    log "✅ 모든 지표 정상"
fi

echo "================================================"
echo "  로그 저장: $LOG_FILE"
echo "================================================"