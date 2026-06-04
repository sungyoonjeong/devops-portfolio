#!/bin/bash

# 숫자 계산: (( )) 사용
a=10
b=3

echo $(( a + b ))   # 13
echo $(( a - b ))   # 7
echo $(( a * b ))   # 30
echo $(( a / b ))   # 3 (정수 나누기)
echo $(( a % b ))   # 1 (나머지)
echo $(( a ** b))   # 1000(거듭제곱)

# 변수에 저장
result=$(( a * b ))
echo "결과: $result"

# 증감
(( a++ ))       # a=11
(( a += 5 ))    # a=16

# 비교 연산 (정수)
# -eq : equal (같다)
# -ne : not equal (다르다)
# -gt : greater than (크다)
# -lt : less than (작다)
# -ge : greater or equal (크거나 같다)
# -le : less or equal (작거나 같다)

cpu=85
if [ $cpu -gt 80 ]; then
    echo "CPU 위험!"
fi

# 문자열 비교
# =     # 같다
# !=    # 다르다
# -z    # 비어있다 (zero length)
# -n    # 비어있지 않다

# 빈 문자열 확인
empty=""
if [ -z "$empty" ]; then
    echo "빈 문자열"
fi

str="hey"
if [ -n "$str" ]; then
    echo "비어있지 않음"
fi

status="running"
if [ "$status" = "running" ]; then
    echo "실행중"
fi