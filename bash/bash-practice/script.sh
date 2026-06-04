#!/bin/bash
# 실행: ./script.sh web-01 80

echo "스크립트명: $0"   # ./script.sh
echo "첫째 인수: $1"    # web-01
echo "둘째 인수: $2"    # 80
echo "인수 개수: $#"    # 2
echo "전체 인수: $@"    # web-01 80

SERVER=$1
THRESHOLD=$2

echo "$SERVER 서버 임계값 $THRESHOLD% 로 체크"