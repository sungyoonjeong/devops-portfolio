#!/bin/bash

# 배열 선언
servers=("web-01" "web-02" "db-01" "cache-01")

# 인덱스로 접근 (0부터)
echo ${servers[0]}   # web-01
echo ${servers[1]}   # web-02
echo ${servers[-1]}  # cache-01 (마지막)

# 배열 전체
echo ${servers[@]}   # web-01 web-02 db-01 cache-01

# 배열 길이
echo ${#servers[@]}  # 4

# 배열 순회
for server in "${servers[@]}"; do
    echo "서버: $server"
done