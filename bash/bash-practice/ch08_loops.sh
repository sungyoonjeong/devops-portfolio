#!/bin/bash

# for 루프 — 리스트
for server in web-01 web-02 db-01; do
    echo "체크: $server"
done

# for 루프 — 범위
for i in {1..5}; do
    echo "번호: $i"
done

# 범위 + 증가 (2씩)
for i in {0..10..2}; do
    echo $i    # 0 2 4 6 8 10
done

# for 루프 — C스타일
for (( i=0; i<5; i++ )); do
    echo "i = $i"
done

# while 루프
count=0
while [ $count -lt 3 ]; do
    echo "카운트: $count"
    (( count++ ))
done

# 무한 루프 (모니터링)
while true; do
    echo "서버 체크 중..."
    sleep 60    # 60초 대기
done

# 파일 한 줄씩 읽기
while read line; do
    echo "줄: $line"
done < input.txt

# 파일 목록 순회
for file in /var/log/*.log; do
    echo "로그 파일: $file"
done

# break와 continue
for i in {1..10}; do
    if [ $i -eq 5 ]; then
        continue   # 5 건너뜀
    fi
    if [ $i -eq 8 ]; then
        break      # 8에서 종료
    fi
    echo $i   # 1 2 3 4 6 7
done