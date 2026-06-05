#!/bin/bash

# $? = 직전 명령의 종료 코드
# 0 = 성공, 0이 아니면 = 실패

ls /home
echo $?        # 0 (성공)

ls /없는경로 2>/dev/null
echo $?        # 2 (실패)

# 스크립트 종료 코드 지정
check() {
    if [ -f "config.yml" ]; then
        exit 0    # 정상 종료
    else
        echo "설정 파일 없음"
        exit 1    # 오류 종료
    fi
}

# 명령 연쇄
command1 && command2   # command1 성공하면 command2 실행
command1 || command2   # command1 실패하면 command2 실행

# 예시
mkdir backup && echo "생성 성공"
cd /없는경로 || echo "이동 실패"