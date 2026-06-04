#!/bin/bash

# 변수 선언 (= 양쪽에 공백 없음!)
name="성윤"
server="web-01"
cpu=85

# 변수 사용: $ 붙이기
echo "이름: $name"
echo "서버: $server"
echo "CPU: $cpu%"

# 변수 안에 변수 사용
message="$server 의 CPU가 $cpu% 입니다"
echo $message

# name = "성윤"   # 에러! = 양쪽에 공백 없어야 함
# name="성윤"     # 올바름