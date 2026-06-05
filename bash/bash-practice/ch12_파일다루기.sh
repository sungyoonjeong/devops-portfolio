#!/bin/bash

# 파일에 쓰기
echo "첫 줄" > log.txt        # 덮어쓰기 (>)
echo "둘째 줄" >> log.txt      # 이어쓰기 (>>)

# 파일 읽기
cat log.txt                   # 전체 출력
head -5 log.txt               # 앞 5줄
tail -5 log.txt               # 뒤 5줄
tail -f log.txt               # 실시간 추적

# 한 줄씩 처리
while read line; do
    echo "처리: $line"
done < log.txt

# 파일 존재하면 삭제
if [ -f "old.log" ]; then
    rm old.log
fi

# 오래된 파일 찾기 (7일 이상)
find /var/log -name "*.log" -mtime +7