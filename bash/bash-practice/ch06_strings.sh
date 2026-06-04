#!/bin/bash

str="Hello, DevOps World"

# 문자열 길이
echo ${#str}          # 19

# 부분 문자열 (substring)
echo ${str:0:5}       # Hello (0번째부터 5개)
echo ${str:7:6}       # DevOps

# 문자열 치환
echo ${str/World/Go}  # Hello, DevOps Go (첫 번째만)
echo ${str//o/0}      # Hell0, Dev0ps W0rld (전부)

# 대소문자
name="devops"
echo ${name^^}        # DEVOPS (전부 대문자)
echo ${name^}         # Devops (첫 글자만 대문자)

# 앞뒤 제거
path="/var/log/app.log"
echo ${path##*/}          # app.log (경로 제거)
echo ${path%.log}         # /var/log/app (확장자 제거)
echo ${path%/*}           # /var/log (파일명 제거)

