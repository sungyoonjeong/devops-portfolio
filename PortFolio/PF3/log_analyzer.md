# 📖 log_analyzer.py 개념 완전 정리
> 코드에서 사용된 Python 개념을 처음부터 설명

---

## 목차
1. [정규식 (re 모듈)](#1-정규식-re-모듈)
2. [os 모듈 — 파일 시스템 다루기](#2-os-모듈--파일-시스템-다루기)
3. [파일 읽기·쓰기](#3-파일-읽기쓰기)
4. [리스트 컴프리헨션](#4-리스트-컴프리헨션)
5. [sum() + 조건식](#5-sum--조건식)
6. [슬라이싱 [-3:]](#6-슬라이싱--3)
7. [문자열 += 이어붙이기](#7-문자열--이어붙이기)
8. [파일 수정 시간으로 변경 감지](#8-파일-수정-시간으로-변경-감지)
9. [end='\r' 같은 줄 덮어쓰기](#9-endr-같은-줄-덮어쓰기)
10. [try / except / KeyboardInterrupt](#10-try--except--keyboardinterrupt)
11. [if __name__ == "__main__"](#11-if-__name__--__main__)

---

## 1. 정규식 (re 모듈)

### 정규식이란?
문자열에서 **특정 패턴**을 찾는 강력한 도구입니다.

예를 들어 이런 로그 문자열에서 숫자만 뽑고 싶을 때:
```
"2026-06-03 10:20:35 [INFO] 정상 | CPU: 12.3% | 메모리: 26.3% | 디스크: 0.6%"
```

단순하게 하면 매우 복잡합니다:
```python
# 방법 1: split() 여러 번 사용 → 복잡하고 깨지기 쉬움
parts = line.split('CPU: ')[1]
cpu = parts.split('%')[0]
```

정규식을 쓰면 한 줄로:
```python
# 방법 2: 정규식 → 간단하고 안정적
cpu = float(re.search(r'CPU: ([\d.]+)%', line).group(1))
```

---

### re.search() 사용법

```python
import re

result = re.search(패턴, 문자열)
```

패턴을 문자열에서 찾아서 결과 객체 반환.
못 찾으면 `None` 반환.

---

### 패턴 문법 핵심

| 패턴 | 의미 | 예시 |
|------|------|------|
| `\d` | 숫자 하나 (0~9) | `\d` → "3" |
| `\d+` | 숫자 하나 이상 | `\d+` → "123" |
| `.` | 점(.) 문자 자체 | `\.` → "." |
| `[\d.]+` | 숫자나 점이 하나 이상 | `[\d.]+` → "12.3" |
| `(패턴)` | 캡처 그룹 (이 부분만 추출) | `([\d.]+)` |

---

### 실제 코드 분석

```python
re.search(r'CPU: ([\d.]+)%', line)
```

```
r'CPU: ([\d.]+)%'  ← 패턴 (r = raw string, 역슬래시 그대로)

CPU:       → 'CPU: ' 문자 그대로 찾기
([\d.]+)   → 숫자(0-9)와 점(.)으로 된 문자 1개 이상 → 캡처
%          → '%' 문자 그대로 찾기
```

문자열에서 찾으면:
```
"CPU: 12.3%"
       ^^^^
       ([\d.]+) 가 "12.3" 캡처
```

---

### .group() 이란?

```python
result = re.search(r'CPU: ([\d.]+)%', "CPU: 12.3%")

result.group(0)  # "CPU: 12.3%" → 전체 매칭 문자열
result.group(1)  # "12.3"       → 첫 번째 () 안의 내용만
```

```python
# 최종 코드
cpu = float(re.search(r'CPU: ([\d.]+)%', line).group(1))
#     ↑         ↑                                  ↑
#  실수변환   패턴으로 찾기                     숫자 부분만 추출
# "12.3" → 12.3
```

---

### 자주 하는 실수: None 체크

```python
result = re.search(r'CPU: ([\d.]+)%', "메모리: 26.3%")
# CPU 패턴이 없으므로 result = None

result.group(1)  # AttributeError! None에는 .group() 없음
```

그래서 코드에서 try/except로 감쌌습니다:
```python
try:
    cpu = float(re.search(r'CPU: ([\d.]+)%', line).group(1))
except AttributeError:
    continue  # None이면 건너뜀
```

---

## 2. os 모듈 — 파일 시스템 다루기

### os.path.exists() — 파일 존재 확인

```python
import os

os.path.exists('monitor.log')  # True (파일 있음)
os.path.exists('없는파일.log')  # False (파일 없음)
```

```python
# 실제 사용
if not os.path.exists(filepath):
    print("파일 없음")
    return []
```

---

### os.path.getmtime() — 파일 수정 시간

```python
mtime = os.path.getmtime('monitor.log')
# 반환값: 타임스탬프 (Unix 시간)
# 예: 1748920235.123
# = 1970년 1월 1일 00:00:00 UTC부터 경과한 초

# 파일이 수정되면 이 숫자가 바뀜
# → 두 번 비교해서 달라졌으면 파일이 변경된 것
```

**왜 이 방식을 쓰나?**
```
파일 내용을 매번 읽어서 비교하면 느림
수정 시간 숫자만 비교하면 매우 빠름
→ 10초마다 확인해도 부담 없음
```

---

## 3. 파일 읽기·쓰기

### 파일 읽기

```python
with open('monitor.log', 'r', encoding='utf-8') as f:
    lines = f.readlines()
```

```
open(파일명, 모드, 인코딩)
  'r' = 읽기 (read)
  'w' = 쓰기 (write) → 기존 내용 삭제 후 새로 씀
  'a' = 추가 (append) → 기존 내용 뒤에 이어씀
  encoding='utf-8' → 한글 깨짐 방지

with 구문:
  블록이 끝나면 자동으로 f.close() 호출
  → 직접 닫는 것 잊어도 안전
```

```python
f.readlines()
# 파일 전체를 읽어서 줄 단위 리스트로 반환
# ["줄1\n", "줄2\n", "줄3\n"]

f.read()
# 파일 전체를 하나의 문자열로 반환

f.readline()
# 한 줄씩 읽기
```

### 파일 쓰기

```python
with open('report.txt', 'w', encoding='utf-8') as f:
    f.write(report)
# 'w' 모드: 파일 없으면 새로 생성, 있으면 덮어씀
# → 매번 최신 리포트로 갱신되는 이유
```

---

## 4. 리스트 컴프리헨션

### 기본 문법

```python
[표현식 for 변수 in 반복가능객체 if 조건]
```

### 기존 방식 vs 컴프리헨션 비교

```python
# 기존 방식
lines = []
for l in all_lines:
    if l.strip():              # 빈 줄 아닌 것만
        lines.append(l.strip()) # 공백 제거 후 추가

# 리스트 컴프리헨션 (한 줄로)
lines = [l.strip() for l in all_lines if l.strip()]
```

### 실제 코드 3가지

```python
# INFO 로그만 추출
info = [l for l in lines if '[INFO]' in l]

# WARNING 로그만 추출
warnings = [l for l in lines if '[WARNING]' in l]

# 빈 줄 제거
lines = [l.strip() for l in lines if l.strip()]
```

### Python 비교

```python
# 필터링 (if 조건만)
[x for x in lst if x > 0]         # 양수만

# 변환 (표현식만)
[x * 2 for x in lst]               # 전부 2배

# 변환 + 필터링
[x * 2 for x in lst if x > 0]     # 양수만 2배
```

---

## 5. sum() + 조건식

### sum(1 for ... if 조건) 패턴

```python
cpu_count = sum(1 for w in warnings if 'CPU' in w)
```

이것을 풀어쓰면:
```python
cpu_count = 0
for w in warnings:
    if 'CPU' in w:
        cpu_count += 1
```

**왜 sum(1 for ...)을 쓰나?**
```
한 줄로 간결하게 표현 가능
len([x for x in ...]) 보다 메모리 효율적
    (리스트를 만들지 않고 바로 카운트)
```

---

### 조건부 평균 계산

```python
avg_cpu = sum(cpu_vals) / len(cpu_vals) if cpu_vals else 0
```

이것을 풀어쓰면:
```python
if cpu_vals:           # 리스트가 비어있지 않으면
    avg_cpu = sum(cpu_vals) / len(cpu_vals)
else:                  # 비어있으면
    avg_cpu = 0        # ZeroDivisionError 방지
```

**왜 필요한가?**
```python
sum([]) / len([])  # len([]) = 0 → ZeroDivisionError!
# 경고가 한 번도 없으면 리스트가 비어있음 → 0으로 안전 처리
```

---

## 6. 슬라이싱 [-3:]

### 리스트 슬라이싱 복습

```python
lst = [1, 2, 3, 4, 5]

lst[0:3]   # [1, 2, 3]  → 처음 3개
lst[-3:]   # [3, 4, 5]  → 마지막 3개  ← 이것 사용
lst[:]     # [1, 2, 3, 4, 5] → 전체
```

### 음수 인덱스

```python
lst = ['a', 'b', 'c', 'd', 'e']
#      -5   -4   -3   -2   -1   ← 음수 인덱스
#       0    1    2    3    4   ← 양수 인덱스

lst[-1]    # 'e'  마지막 하나
lst[-3:]   # ['c', 'd', 'e']  마지막 3개
```

### 실제 코드

```python
for w in warnings[-3:]:
    report += f"  {w}\n"
# warnings 전체가 100줄이어도
# 마지막 3건(최근 경고)만 출력
```

---

## 7. 문자열 += 이어붙이기

```python
report = "시작"
report += "\n중간"    # report = "시작\n중간"
report += "\n끝"      # report = "시작\n중간\n끝"
```

**+=는 이것과 동일:**
```python
report = report + "\n중간"
```

### 실제 코드 흐름

```python
# 1. 기본 리포트 생성
report = f"""
========================================
  리포트 시작
...
"""

# 2. 경고 내역 조건부 추가
if warnings:
    report += "\n[ 경고 내역 ]\n"    # 이어붙이기
    for w in warnings[-3:]:
        report += f"  {w}\n"         # 각 줄 이어붙이기

# 3. 마무리 구분선 추가
report += "\n========================================"
```

---

## 8. 파일 수정 시간으로 변경 감지

### 핵심 원리

```
파일이 바뀌면 → 수정 시간이 바뀜
수정 시간이 바뀌면 → 재분석

파일 내용을 매번 읽어서 비교 (❌ 느림)
수정 시간 숫자만 비교 (✅ 빠름)
```

### 코드 흐름

```python
last_modified = 0   # 이전 수정 시간 (처음엔 0)

while True:
    current_modified = os.path.getmtime(LOG_FILE)
    # 현재 수정 시간 확인

    if current_modified != last_modified:
        # 수정 시간이 달라졌으면 → 파일이 변경됨
        analyze_once()                    # 재분석
        last_modified = current_modified  # 시간 업데이트

    time.sleep(10)  # 10초 대기 후 다시 확인
```

### 실행 시나리오

```
[00초] last_modified = 0
       current = 1748920000 → 다름 → 분석 실행
       last_modified = 1748920000

[10초] current = 1748920000 → 같음 → 대기

[20초] current = 1748920000 → 같음 → 대기

[300초] monitor.py가 로그 추가 → 수정 시간 바뀜
        current = 1748920300 → 다름 → 재분석!
        last_modified = 1748920300
```

---

## 9. end='\r' 같은 줄 덮어쓰기

### print()의 end 파라미터

```python
print("hello")          # "hello\n" → 줄바꿈 포함
print("hello", end='')  # "hello"   → 줄바꿈 없음
print("hello", end='\r')# "hello\r" → 커서를 줄 맨 앞으로
```

### \r (carriage return) 이란?

```
\n = 다음 줄로 이동
\r = 현재 줄 맨 앞으로 이동 (줄바꿈 없음)
```

```
터미널 출력:
  print("[10:20:00] 변경 없음", end='\r')
  → [10:20:00] 변경 없음

  (10초 후)
  print("[10:20:10] 변경 없음", end='\r')
  → [10:20:10] 변경 없음  ← 같은 줄에 덮어씀!
```

**왜 쓰나?**
```
10초마다 새 줄이 생기면 터미널이 지저분해짐
같은 줄을 계속 업데이트하면 깔끔한 대기 표시 가능
```

---

## 10. try / except / KeyboardInterrupt

### try / except 복습

```python
try:
    # 실행할 코드
    result = 10 / 0      # ZeroDivisionError 발생!
except ZeroDivisionError:
    print("0으로 나눌 수 없음")  # 에러 처리
```

### KeyboardInterrupt란?

```
사용자가 Ctrl+C를 누르면 발생하는 예외
= "프로그램 강제 종료" 신호

처리 안 하면: 빨간 에러 메시지와 함께 종료 (지저분)
처리 하면:    깔끔한 메시지 출력 후 종료 (정리된 종료)
```

```python
while True:
    try:
        # 10초마다 실행할 코드
        time.sleep(10)

    except KeyboardInterrupt:
        # Ctrl+C 누르면 여기로
        print("\n\n🛑 로그 분석기 종료")
        break   # while 루프 탈출
```

**실행 흐름:**
```
프로그램 실행 중...
[10:20:00] 변경 없음
[10:20:10] 변경 없음
^C  ← Ctrl+C 누름

🛑 로그 분석기 종료   ← 깔끔하게 종료
```

---

## 11. if __name__ == "__main__"

### 왜 필요한가?

```python
# 파일을 직접 실행할 때
python3 log_analyzer.py
# → __name__ = "__main__"
# → if 조건 True → main() 실행

# 다른 파일에서 import할 때
import log_analyzer
# → __name__ = "log_analyzer"
# → if 조건 False → main() 자동 실행 안 됨
```

**실용적 예시:**
```python
# utils.py
def analyze_warnings(warnings):
    ...

if __name__ == "__main__":
    main()  # python3 utils.py 로 직접 실행할 때만

# main.py
import utils
utils.analyze_warnings(warnings)  # main() 자동 실행 안 됨 ✅
```

**DevOps에서 왜 중요한가?**
```
여러 스크립트를 모듈로 연결할 때
한 파일이 다른 파일을 import해도
원치 않는 코드가 자동 실행되지 않음
```

---

## 핵심 개념 한줄 요약

| 개념 | 핵심 |
|------|------|
| 정규식 re.search() | 문자열에서 패턴으로 원하는 부분만 추출 |
| .group(1) | 정규식 () 안의 캡처 그룹만 가져오기 |
| os.path.exists() | 파일 존재 여부 확인 |
| os.path.getmtime() | 파일 수정 시간 → 변경 감지에 활용 |
| open('r') | 파일 읽기, with로 자동 닫기 |
| open('w') | 파일 쓰기, 기존 내용 덮어씀 |
| 리스트 컴프리헨션 | [표현식 for 변수 in 리스트 if 조건] 한 줄 필터링 |
| sum(1 for ... if) | 조건에 맞는 항목 개수 세기 |
| [-3:] | 리스트 마지막 3개 (최근 3건) |
| += | 문자열·리스트에 이어붙이기 |
| end='\r' | 같은 줄 덮어쓰기 (깔끔한 대기 표시) |
| KeyboardInterrupt | Ctrl+C 감지 → 깔끔하게 종료 |
| if __name__ == "__main__" | 직접 실행할 때만 main() 호출 |

---

*log_analyzer.py 개념 정리 — 2026.06.03*
