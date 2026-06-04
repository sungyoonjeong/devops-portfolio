#!/bin/bash
# monitor.sh - PF3: 서버 상태 자동 점검

# 설정
CPU_THRESHOLD=80
MEM_THRESHOLD=85
DISK_THRESHOLD=80
LOG_FILE="monitor.log"

# 현재 시각
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# CPU 사용률
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)

# 메모리 사용률
MEM=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100)}')

# 디스크 사용률
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

# 로그 기록 함수
log() {
    echo "[$TIMESTAMP] $1" | tee -a $LOG_FILE
}

# 상태 체크
log "CPU: ${CPU}% | MEM: ${MEM}% | DISK: ${DISK}%"

if [ $CPU -gt $CPU_THRESHOLD ]; then
    log "🔴 CPU 위험: ${CPU}%"
fi

if [ $MEM -gt $MEM_THRESHOLD ]; then
    log "🟡 메모리 위험: ${MEM}%"
fi

if [ $DISK -gt $DISK_THRESHOLD ]; then
    log "⚠️ 디스크 위험: ${DISK}%"
fi