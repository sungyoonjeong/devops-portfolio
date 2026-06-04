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

# 요소 추가
servers+=("api-01")
echo ${#servers[@]} # 5

# 배열 순회
for server in "${servers[@]}"; do
    echo "서버: $server"
done


# $0- 현재 스크립트의 파일 이름입니다.
# $n- 스크립트에 전달된 N번째 인수가 호출되었거나 함수가 호출되었습니다.
# $#- 스크립트 또는 함수에 전달되는 인자의 개수.
# $@- 스크립트 또는 함수에 전달되는 모든 인수.
# $*- 스크립트 또는 함수에 전달되는 모든 인수.
# $?- 마지막으로 실행된 명령의 종료 상태입니다.
# $$- 현재 셸의 프로세스 ID입니다. 셸 스크립트의 경우, 이는 스크립트가 실행 중인 프로세스 ID입니다.
# $!- 마지막 백그라운드 명령의 프로세스 번호입니다.