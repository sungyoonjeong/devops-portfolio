#!/bin/bash

# 함수 선언
check_server() {
    local server=$1      # local: 함수 내부에서만 사용
    local threshold=$2

    echo "=== $server 체크 ==="

    # CPU 사용률 가져오기 (실제 명령어)
    cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "CPU: $cpu%"

    if (( $(echo "$cpu > $threshold" | bc -l) )); then
        echo "🔴 임계값 초과!"
        return 1   # 실패 반환
    else
        echo "🟢 정상"
        return 0   # 성공 반환
    fi
}

# 간단한 알림 함수
send_alert() {
    local message=$1
    echo "[알림] $message"
    # 실제로는 curl로 Slack 전송
}

# 함수 호출
check_server "web-01" 80

# 반환값 확인
if check_server "web-01" 80; then
    echo "정상 서버"
else
    send_alert "web-01 CPU 위험"
fi