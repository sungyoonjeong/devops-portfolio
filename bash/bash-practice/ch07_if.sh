#!/bin/bash

cpu=87

# 기본 if-elif-else
if [ $cpu -ge 90 ]; then
    echo "🔴 CPU 위험"
elif [ $cpu -ge 80 ]; then
    echo "🟡 CPU 주의"    # 출력됨
elif [ $cpu -ge 60 ]; then
    echo "🟠 CPU 보통"
else
    echo "🟢 CPU 정상"
fi

# 파일 존재 확인
if [ -f "monitor.log" ]; then
    echo "로그 파일 있음"
else
    echo "로그 파일 없음"
fi

# 디렉토리 확인
if [ -d "/var/log" ]; then
    echo "/var/log 디렉토리 있음"
fi

# 검사 옵션
# -f   # 파일 존재
# -d   # 디렉토리 존재
# -e   # 파일이든 디렉토리든 존재
# -r   # 읽기 가능
# -w   # 쓰기 가능
# -x   # 실행 가능
# -s   # 파일 크기 0보다 큼

# 문자열 비교
status="running"
if [ "$status" = "running" ]; then
    echo "서버 실행 중"
fi

# AND(&&), OR(||)
if [ $cpu -gt 80 ] && [ $cpu -lt 100 ]; then
    echo "CPU 위험 범위"
fi

if [ $cpu -gt 90 ] || [ $mem -gt 90 ]; then
    echo "하나라도 위험"
fi

# if [$cpu -gt 80]; then   # 에러!
# if [ $cpu -gt 80 ]; then # 올바름 (공백 필수)

