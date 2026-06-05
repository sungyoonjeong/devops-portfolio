#!/bin/bash

# $(명령어) = 명령어 실행 결과를 값으로
today=$(date +%Y-%m-%d)
echo "오늘: $today"

# 현재 디렉토리 파일 수
count=$(ls | wc -l)
echo "파일 수: $count"

# CPU 사용률 (실전)
cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
echo "CPU: $cpu"

# 디스크 사용률
disk=$(df / | tail -1 | awk '{print $5}')
echo "디스크: $disk"

# 백틱도 가능하지만 $() 권장
files=`ls`    # 구식
files=$(ls)   # 권장