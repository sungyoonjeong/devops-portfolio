#!/bin/bash

# 스크립트 실행할 때 넘기는 값
# bash script.sh arg1 arg2 arg3

echo "스크립트 이름: $0"    # 스크립트 파일명
echo "첫 번째 인수: $1"     # 첫 번째 값
echo "두 번째 인수: $2"     # 두 번째 값
echo "전체 인수 수: $#"     # 인수 개수
echo "모든 인수: $@"        # 모든 인수

# 실제 사용 예
server=$1
threshold=$2

# 인수 없으면 기본값
server=${1:-"localhost"}
threshold=${2:-80}

echo "$server 의 임계값: $threshold%"