# ⚡ Bash 가이드
---

## 목차
### 기초 (1~9)
1. [Bash란 무엇인가](#1-bash란-무엇인가)
2. [Hello World — 첫 스크립트](#2-hello-world--첫-스크립트)
3. [변수 (Variables)](#3-변수-variables)
4. [인수 전달 (Arguments)](#4-인수-전달-arguments)
5. [배열 (Arrays)](#5-배열-arrays)
6. [연산자 (Operators)](#6-연산자-operators)
7. [문자열 (String Operations)](#7-문자열-string-operations)
8. [조건문 (if)](#8-조건문-if)
9. [반복문 (Loops)](#9-반복문-loops)
### 심화 (10~18)
10. [함수 (Functions)](#10-함수-functions)
11. [명령어 치환 (Command Substitution)](#11-명령어-치환)
12. [입력 받기 (read)](#12-입력-받기-read)
13. [파일 다루기](#13-파일-다루기)
14. [exit code와 종료 상태](#14-exit-code와-종료-상태)
15. [파이프와 리다이렉션](#15-파이프와-리다이렉션)
16. [자주 쓰는 명령어 (grep·awk·sed)](#16-자주-쓰는-명령어)
17. [cron 자동 실행](#17-cron-자동-실행)
18. [실전 DevOps 스크립트](#18-실전-devops-스크립트)
- [자주 하는 실수](#자주-하는-실수)
- [핵심 치트시트](#핵심-치트시트)

---

## 1. Bash란 무엇인가

```
Bash = Bourne Again Shell
리눅스/맥 터미널에서 명령어를 실행하는 프로그램이자 언어

쉘 스크립트(.sh):
  여러 명령어를 파일에 모아두고 한 번에 실행
  → 반복 작업 자동화

DevOps에서 왜 필수인가:
  서버는 대부분 리눅스
  GUI 없이 터미널로만 관리
  배포·모니터링·백업 전부 쉘 스크립트로 자동화
```

### 실습 환경 준비

```bash
# WSL2 터미널에서
mkdir -p ~/bash-practice
cd ~/bash-practice
```

### 스크립트 실행 방법 3가지

```bash
# 방법 1: bash 명령으로 실행
bash script.sh

# 방법 2: 실행 권한 주고 직접 실행
chmod +x script.sh   # 실행 권한 부여 (최초 1회)
./script.sh

# 방법 3: source로 실행 (현재 쉘에서)
source script.sh
```

---

## 2. Hello World — 첫 스크립트

```bash
#!/bin/bash
# 위 줄 = 샤뱅(Shebang): "이 파일은 bash로 실행해라"
# 모든 .sh 파일 첫 줄에 필수

# echo = 화면에 출력 (Python의 print)
echo "Hello, World!"
echo "DevOps 시작!"

# 주석은 # 으로 시작
# 이 줄은 실행 안 됨
```

**실행 결과:**
```
Hello, World!
DevOps 시작!
```

### echo 옵션

```bash
echo "줄바꿈 포함"          # 기본: 끝에 줄바꿈
echo -n "줄바꿈 없음"        # -n: 줄바꿈 안 함
echo -e "탭\t줄바꿈\n적용"   # -e: 특수문자(\t \n) 해석
```

---

## 3. 변수 (Variables)

### 변수 선언과 사용

```bash
#!/bin/bash

# 선언: = 양쪽에 공백 절대 금지!
name="성윤"
age=31
server="web-01"

# 사용: $ 붙이기
echo $name           # 성윤
echo "이름: $name"    # 이름: 성윤
echo "나이: ${age}세"  # 나이: 31세  ← {} 권장
```

### ★ 가장 흔한 실수

```bash
name = "성윤"    # ❌ 에러! = 양쪽 공백
name="성윤"      # ✅ 올바름

# 큰따옴표 vs 작은따옴표
echo "$name"     # 성윤 (변수 해석됨)
echo '$name'     # $name (그대로 출력)
```

### 변수 종류

```bash
# 일반 변수
city="서울"

# 읽기 전용 (상수)
readonly PI=3.14
# PI=3.15  # 에러! 변경 불가

# 변수 삭제
unset city

# 환경 변수 (대문자 관례)
export PATH="$PATH:/new/path"
echo $HOME    # /home/jsy
echo $USER    # jsy
echo $PWD     # 현재 디렉토리
```

---

## 4. 인수 전달 (Arguments)

### 스크립트에 값 넘기기

```bash
#!/bin/bash
# 실행: ./script.sh web-01 80

echo "스크립트명: $0"   # ./script.sh
echo "첫째 인수: $1"    # web-01
echo "둘째 인수: $2"    # 80
echo "인수 개수: $#"    # 2
echo "전체 인수: $@"    # web-01 80
```

**실행:**
```bash
./script.sh web-01 80
# 스크립트명: ./script.sh
# 첫째 인수: web-01
# 둘째 인수: 80
# 인수 개수: 2
# 전체 인수: web-01 80
```

### 실전 활용

```bash
#!/bin/bash
# 서버명과 임계값을 인수로 받기

SERVER=$1
THRESHOLD=$2

# 인수 없으면 기본값 사용
SERVER=${1:-"localhost"}    # $1 없으면 localhost
THRESHOLD=${2:-80}          # $2 없으면 80

echo "$SERVER 서버 임계값 $THRESHOLD% 로 체크"
```

---

## 5. 배열 (Arrays)

```bash
#!/bin/bash

# 배열 선언
servers=("web-01" "web-02" "db-01" "cache-01")

# 접근 (0부터)
echo ${servers[0]}    # web-01
echo ${servers[2]}    # db-01
echo ${servers[-1]}   # cache-01 (마지막)

# 전체 요소
echo ${servers[@]}    # web-01 web-02 db-01 cache-01

# 배열 길이
echo ${#servers[@]}   # 4

# 요소 추가
servers+=("api-01")
echo ${#servers[@]}   # 5

# 순회
for s in "${servers[@]}"; do
    echo "서버: $s"
done
```

---

## 6. 연산자 (Operators)

### 산술 연산

```bash
#!/bin/bash
a=10
b=3

# 방법 1: $(( )) — 가장 많이 씀
echo $(( a + b ))    # 13
echo $(( a - b ))    # 7
echo $(( a * b ))    # 30
echo $(( a / b ))    # 3 (정수)
echo $(( a % b ))    # 1 (나머지)
echo $(( a ** b ))   # 1000 (거듭제곱)

# 변수에 저장
result=$(( a * b + 5 ))
echo $result         # 35

# 증감
(( a++ ))            # a = 11
(( a += 5 ))         # a = 16
```

### 비교 연산자 (★ 정수는 영문 약자)

```bash
# 정수 비교
-eq   # equal (==)
-ne   # not equal (!=)
-gt   # greater than (>)
-lt   # less than (<)
-ge   # greater or equal (>=)
-le   # less or equal (<=)

# 사용 예
cpu=85
if [ $cpu -gt 80 ]; then
    echo "위험"
fi
```

### 문자열 비교 (기호 사용)

```bash
=     # 같다
!=    # 다르다
-z    # 비어있다 (zero length)
-n    # 비어있지 않다

status="running"
if [ "$status" = "running" ]; then
    echo "실행중"
fi
```

---

## 7. 문자열 (String Operations)

```bash
#!/bin/bash
str="Hello DevOps World"

# 길이
echo ${#str}              # 18

# 부분 문자열 (시작:길이)
echo ${str:0:5}           # Hello
echo ${str:6:6}           # DevOps

# 치환
echo ${str/World/Go}      # Hello DevOps Go (첫째만)
echo ${str//o/0}          # Hell0 Dev0ps W0rld (전부)

# 대소문자
text="devops"
echo ${text^^}            # DEVOPS (전부 대문자)
echo ${text^}             # Devops (첫글자만)
lower="HELLO"
echo ${lower,,}           # hello (전부 소문자)

# 앞뒤 제거
path="/var/log/app.log"
echo ${path##*/}          # app.log (경로 제거)
echo ${path%.log}         # /var/log/app (확장자 제거)
echo ${path%/*}           # /var/log (파일명 제거)
```

---

## 8. 조건문 (if)

### 기본 구조

```bash
#!/bin/bash
cpu=87

if [ $cpu -ge 90 ]; then
    echo "🔴 위험"
elif [ $cpu -ge 80 ]; then
    echo "🟡 주의"       # 출력됨
elif [ $cpu -ge 60 ]; then
    echo "🟠 보통"
else
    echo "🟢 정상"
fi
```

### ★ [ ] 안쪽 공백 필수

```bash
if [$cpu -gt 80]; then    # ❌ 에러
if [ $cpu -gt 80 ]; then  # ✅ 공백 필수
```

### 파일·디렉토리 검사 (DevOps 필수)

```bash
# 파일 존재
if [ -f "config.yml" ]; then
    echo "파일 있음"
fi

# 디렉토리 존재
if [ -d "/var/log" ]; then
    echo "디렉토리 있음"
fi

# 검사 옵션
-f   # 파일 존재
-d   # 디렉토리 존재
-e   # 파일이든 디렉토리든 존재
-r   # 읽기 가능
-w   # 쓰기 가능
-x   # 실행 가능
-s   # 파일 크기 0보다 큼
```

### AND / OR

```bash
cpu=85
mem=70

# AND (&&)
if [ $cpu -gt 80 ] && [ $mem -gt 60 ]; then
    echo "둘 다 높음"
fi

# OR (||)
if [ $cpu -gt 90 ] || [ $mem -gt 90 ]; then
    echo "하나라도 위험"
fi
```

---

## 9. 반복문 (Loops)

### for 루프

```bash
#!/bin/bash

# 리스트 순회
for server in web-01 web-02 db-01; do
    echo "체크: $server"
done

# 범위 (1부터 5)
for i in {1..5}; do
    echo $i
done

# 범위 + 증가 (2씩)
for i in {0..10..2}; do
    echo $i    # 0 2 4 6 8 10
done

# C 스타일
for (( i=0; i<5; i++ )); do
    echo $i
done

# 파일 목록
for file in /var/log/*.log; do
    echo "로그: $file"
done
```

### while 루프

```bash
#!/bin/bash

# 기본 while
count=0
while [ $count -lt 5 ]; do
    echo "카운트: $count"
    (( count++ ))
done

# 무한 루프 (모니터링)
while true; do
    echo "서버 체크 중..."
    sleep 60    # 60초 대기
done

# 파일 한 줄씩 읽기
while read line; do
    echo "줄: $line"
done < input.txt
```

### break / continue

```bash
for i in {1..10}; do
    if [ $i -eq 3 ]; then
        continue   # 3 건너뜀
    fi
    if [ $i -eq 7 ]; then
        break      # 7에서 종료
    fi
    echo $i        # 1 2 4 5 6
done
```

---

## 10. 함수 (Functions)

```bash
#!/bin/bash

# 함수 선언
greet() {
    echo "안녕하세요, $1님"
}

# 호출 (인수 전달)
greet "성윤"      # 안녕하세요, 성윤님

# 지역 변수 사용
check_cpu() {
    local server=$1       # local: 함수 내부 전용
    local threshold=$2

    echo "$server CPU 체크 (임계값 $threshold%)"

    # 반환값: return은 0~255 (종료코드)
    if [ $threshold -gt 80 ]; then
        return 1   # 실패
    else
        return 0   # 성공
    fi
}

# 반환값 확인
check_cpu "web-01" 85
if [ $? -eq 0 ]; then     # $? = 직전 명령 종료코드
    echo "정상"
else
    echo "주의 필요"
fi

# 값 반환 (echo 사용)
get_timestamp() {
    echo $(date "+%Y-%m-%d %H:%M:%S")
}

now=$(get_timestamp)      # 함수 결과를 변수에
echo "현재: $now"
```

---

## 11. 명령어 치환 (Command Substitution)

```bash
#!/bin/bash

# $(명령어) = 명령어 실행 결과를 값으로
today=$(date +%Y-%m-%d)
echo "오늘: $today"

# 현재 디렉토리 파일 수
count=$(ls | wc -l)
echo "파일 수: $count"

# CPU 사용률 (실전)
cpu=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
echo "CPU: $cpu"

# 디스크 사용률
disk=$(df / | tail -1 | awk '{print $5}')
echo "디스크: $disk"

# 백틱도 가능하지만 $() 권장
files=`ls`    # 구식
files=$(ls)   # 권장
```

---

## 12. 입력 받기 (read)

```bash
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
```

---

## 13. 파일 다루기

```bash
#!/bin/bash

# 파일에 쓰기
echo "첫 줄" > log.txt        # 덮어쓰기 (>)
echo "둘째 줄" >> log.txt      # 이어쓰기 (>>)

# 파일 읽기
cat log.txt                   # 전체 출력
head -5 log.txt               # 앞 5줄
tail -5 log.txt               # 뒤 5줄
tail -f log.txt               # 실시간 추적

# 한 줄씩 처리
while read line; do
    echo "처리: $line"
done < log.txt

# 파일 존재하면 삭제
if [ -f "old.log" ]; then
    rm old.log
fi

# 오래된 파일 찾기 (7일 이상)
find /var/log -name "*.log" -mtime +7
```

---

## 14. exit code와 종료 상태

```bash
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
```

---

## 15. 파이프와 리다이렉션

```bash
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
```

---

## 16. 자주 쓰는 명령어 (grep·awk·sed)

### grep — 패턴 검색

```bash
grep "ERROR" app.log              # ERROR 포함 줄
grep -i "error" app.log           # 대소문자 무시
grep -c "ERROR" app.log           # 개수만
grep -n "ERROR" app.log           # 줄번호 포함
grep -v "INFO" app.log            # INFO 제외한 줄
grep -r "TODO" ./src              # 디렉토리 재귀 검색
```

### awk — 컬럼 처리

```bash
# 공백 기준으로 나눠서 특정 컬럼 출력
echo "web-01 85 70" | awk '{print $1}'    # web-01
echo "web-01 85 70" | awk '{print $2}'    # 85

# df 결과에서 사용률만
df -h | awk '{print $5}'

# 조건부 출력
ps aux | awk '$3 > 50 {print $11}'        # CPU 50% 초과 프로세스
```

### sed — 텍스트 치환

```bash
# 파일 내용 치환
sed 's/old/new/' file.txt          # 첫째만
sed 's/old/new/g' file.txt         # 전부
sed -i 's/old/new/g' file.txt      # 파일 직접 수정

# 특정 줄 삭제
sed '3d' file.txt                  # 3번째 줄 삭제
sed '/ERROR/d' file.txt            # ERROR 포함 줄 삭제
```

---

## 17. cron 자동 실행

```bash
# cron = 정해진 시간에 자동 실행하는 스케줄러

# crontab 편집
crontab -e

# 형식: 분 시 일 월 요일 명령어
# *     *  *  *  *

# 예시
0 9 * * *     /home/jsy/monitor.sh      # 매일 9시
*/5 * * * *   /home/jsy/check.sh        # 5분마다
0 0 * * 0     /home/jsy/cleanup.sh      # 매주 일요일 0시
0 2 1 * *     /home/jsy/backup.sh       # 매월 1일 2시

# 등록된 cron 확인
crontab -l
```

---

## 18. 실전 DevOps 스크립트

### monitor.sh (PF3용)

```bash
#!/bin/bash
# 서버 상태 자동 점검 스크립트

# 설정
CPU_THRESHOLD=80
MEM_THRESHOLD=85
DISK_THRESHOLD=80
LOG_FILE="monitor.log"

# 시각
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# 메트릭 수집
CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)
MEM=$(free | grep Mem | awk '{printf("%.0f", $3/$2*100)}')
DISK=$(df / | tail -1 | awk '{print $5}' | tr -d '%')

# 로그 함수
log() {
    echo "[$TIMESTAMP] $1" | tee -a $LOG_FILE
}

# 상태 기록
log "CPU: ${CPU}% | MEM: ${MEM}% | DISK: ${DISK}%"

# 임계값 체크
[ $CPU -gt $CPU_THRESHOLD ]   && log "🔴 CPU 위험: ${CPU}%"
[ $MEM -gt $MEM_THRESHOLD ]   && log "🟡 메모리 위험: ${MEM}%"
[ $DISK -gt $DISK_THRESHOLD ] && log "⚠️ 디스크 위험: ${DISK}%"
```

### cleanup.sh (PF3용 — 오래된 로그 삭제)

```bash
#!/bin/bash
# 오래된 로그 파일 자동 삭제

LOG_DIR="./logs"
DAYS=7

echo "[$( date '+%Y-%m-%d %H:%M:%S')] 정리 시작"

# 7일 이상 된 .log 파일 찾기
old_files=$(find $LOG_DIR -name "*.log" -mtime +$DAYS 2>/dev/null)

if [ -z "$old_files" ]; then
    echo "삭제할 파일 없음"
else
    count=$(echo "$old_files" | wc -l)
    echo "$old_files" | while read file; do
        echo "삭제: $file"
        rm "$file"
    done
    echo "총 ${count}개 삭제 완료"
fi
```

---

## 자주 하는 실수

```bash
# 1. = 양쪽 공백
name = "값"      # ❌
name="값"        # ✅

# 2. [ ] 안쪽 공백 없음
if [$x -gt 5]    # ❌
if [ $x -gt 5 ]  # ✅

# 3. $ 빼먹기
echo name        # name (문자 그대로)
echo $name       # 값

# 4. 변수에 공백 있을 때 따옴표 없음
file=$1
rm $file         # 공백 있으면 깨짐
rm "$file"       # ✅ 항상 따옴표

# 5. 정수 비교에 기호 사용
if [ $x > 5 ]    # ❌ (이건 리다이렉션됨)
if [ $x -gt 5 ]  # ✅

# 6. 샤뱅 빠짐
# 첫 줄에 #!/bin/bash 꼭 넣기
```

---

## 핵심 치트시트

| 분류 | 문법 | 의미 |
|------|------|------|
| 출력 | `echo "text"` | 화면 출력 |
| 변수 | `name="값"` | 선언 (공백X) |
| 변수 | `$name` `${name}` | 사용 |
| 인수 | `$1 $2 $#  $@` | 인수·개수·전체 |
| 산술 | `$(( a + b ))` | 계산 |
| 비교 | `-eq -ne -gt -lt -ge -le` | 정수 비교 |
| 문자열 | `= != -z -n` | 문자열 비교 |
| 조건 | `if [ 조건 ]; then` | 조건문 |
| 파일 | `-f -d -e -r -w -x` | 파일 검사 |
| 반복 | `for x in ...; do` | for 루프 |
| 반복 | `while [ 조건 ]; do` | while 루프 |
| 함수 | `name() { ... }` | 함수 선언 |
| 치환 | `$(명령어)` | 명령 결과를 값으로 |
| 종료코드 | `$?` | 직전 명령 결과 (0=성공) |
| 파이프 | `cmd1 \| cmd2` | 결과 전달 |
| 리다이렉션 | `> >> 2>` | 파일로 출력 |
| 검색 | `grep "패턴" 파일` | 패턴 찾기 |
| 컬럼 | `awk '{print $1}'` | 컬럼 추출 |
| 치환 | `sed 's/a/b/g'` | 텍스트 치환 |

---


---

# 📌 [learnshell.org Advanced] Bash Debugging (디버깅)

> learnshell.org의 Advanced 섹션 내용 — 스크립트 오류 찾기

## 디버깅이 필요한 이유

```
스크립트가 길어지면 어디서 틀렸는지 찾기 어려움
Bash는 디버깅 옵션을 내장하고 있음
→ 어떤 명령이 실행됐는지 한 줄씩 추적 가능
```

## 방법 1: -x 옵션 (실행 추적)

```bash
# 실행할 때 -x 붙이기
bash -x script.sh

# 각 명령이 실행되기 전에 + 표시와 함께 출력됨
```

**예시:**
```bash
#!/bin/bash
name="성윤"
echo "안녕 $name"
```

```bash
bash -x script.sh
# + name=성윤
# + echo '안녕 성윤'
# 안녕 성윤
# → 실제 어떤 값으로 실행됐는지 보임
```

## 방법 2: 스크립트 안에서 부분 디버깅

```bash
#!/bin/bash

echo "정상 부분"

set -x           # 여기서부터 디버깅 켜기
name="성윤"
cpu=85
echo "$name $cpu"
set +x           # 여기서 디버깅 끄기

echo "다시 정상"
```

## 방법 3: 샤뱅에 옵션 추가

```bash
#!/bin/bash -x
# 스크립트 전체를 디버깅 모드로 실행
```

## 디버깅 핵심 옵션 4가지

```bash
set -x    # 실행되는 명령 출력 (추적)
set -e    # 에러 발생 시 즉시 종료
set -u    # 선언 안 된 변수 사용 시 에러
set -o pipefail   # 파이프 중간 실패 감지

# 실무에서 스크립트 맨 위에 자주 쓰는 조합
set -euo pipefail
# = 에러나면 멈추고, 미선언 변수 막고, 파이프 실패 감지
```

### 실전 예시

```bash
#!/bin/bash
set -euo pipefail   # 안전한 스크립트의 표준 시작

# 이제 아래에서 에러나면 즉시 멈춤
cp config.yml backup/    # 실패하면 여기서 종료
echo "백업 완료"          # 위가 성공해야 실행
```

## 방법 4: echo로 직접 확인 (가장 기본)

```bash
#!/bin/bash
cpu=85

echo "DEBUG: cpu 값은 $cpu"    # 변수 값 확인용 출력
if [ $cpu -gt 80 ]; then
    echo "DEBUG: if 진입함"     # 흐름 확인용 출력
    echo "위험"
fi
# 디버깅 끝나면 DEBUG 줄 삭제
```

---
