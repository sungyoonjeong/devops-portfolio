#!/bin/bash

# 숫자 계산: (( )) 사용
a=10
b=3

echo $(( a + b ))   # 13
echo $(( a - b ))   # 7
echo $(( a * b ))   # 30
echo $(( a / b ))   # 3 (정수 나누기)
echo $(( a % b ))   # 1 (나머지)

# 변수에 저장
result=$(( a * b ))
echo "결과: $result"

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