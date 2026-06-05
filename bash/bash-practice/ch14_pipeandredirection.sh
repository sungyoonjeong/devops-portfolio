#!/bin/bash

# 파이프 | : 앞 명령 결과를 뒤 명령 입력으로
ls -l | grep ".log"           # ls 결과에서 .log만
cat access.log | wc -l        # 줄 수 세기
ps aux | grep nginx           # 프로세스 찾기

# 리다이렉션
echo "내용" > file.txt        # 표준출력 → 파일 (덮어쓰기)
echo "추가" >> file.txt       # 표준출력 → 파일 (이어쓰기)
command 2> error.txt          # 표준에러 → 파일
command > out.txt 2>&1        # 출력+에러 모두 파일로
command 2>/dev/null           # 에러 무시 (버리기)

# 실전 예시
df -h | grep "/dev/sda1" | awk '{print $5}'   # 특정 디스크 사용률
ps aux | sort -k3 -r | head -5                # CPU 상위 5개 프로세스