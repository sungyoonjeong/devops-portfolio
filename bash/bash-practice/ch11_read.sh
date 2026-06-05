#!/bin/bash

# 사용자 입력 받기
echo "서버 이름을 입력하세요:"
read server
echo "입력한 서버: $server"

# 한 줄로 (프롬프트 포함)
read -p "임계값 입력: " threshold
echo "임계값: $threshold"

# 비밀번호 (화면에 안 보이게)
read -sp "비밀번호: " password
echo ""
echo "입력 완료"

# 여러 값 한 번에
read -p "이름 나이: " name age
echo "$name / $age"