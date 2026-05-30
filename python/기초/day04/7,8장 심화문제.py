#데코레이터 + 정규표현식 활용

#문제 : 로그 분석 프로그램을 만들어라.

# 조건:
# ① 데코레이터 만들기
#    - @log_time 데코레이터
#    - 함수 실행 시간을 측정해서 출력
#    - 예시: "analyze_log 실행시간: 0.002초"

# ② 정규표현식으로 로그 분석 함수 만들기
#    - 아래 로그에서 추출:
#      a. IP 주소 (예: 192.168.0.1)
#      b. 날짜 (예: 2026-05-19)
#      c. ERROR 포함된 라인만 필터링

# ③ 샘플 로그:
# log_data = """
# 2026-05-19 10:23:11 192.168.0.1 INFO 서버 시작
# 2026-05-19 10:24:05 192.168.0.2 ERROR 연결 실패
# 2026-05-19 10:25:33 192.168.0.1 INFO 요청 처리
# 2026-05-19 10:26:44 192.168.0.3 ERROR 타임아웃 발생
# 2026-05-19 10:27:01 192.168.0.2 INFO 재연결 성공
# """

# ④ 실행 결과:
# === IP 주소 목록 ===
# 192.168.0.1
# 192.168.0.2
# 192.168.0.1
# 192.168.0.3
# 192.168.0.2

# === ERROR 로그 ===
# 2026-05-19 10:24:05 192.168.0.2 ERROR 연결 실패
# 2026-05-19 10:26:44 192.168.0.3 ERROR 타임아웃 발생

# analyze_log 실행시간: 0.000초

"""
풀이
1) @log_time데코레이터

import time

def log_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행시간: {end-start:.3f}초")
        return result
    return wrapper

2) IP주소 추출 정규표현식
import re

# IP 패턴 : 숫자.숫자.숫자.숫자
ip_pattern = r'\d+\.\d+\.\d+\.\d+'
ips = re.findall(ip_pattern, log_data)

3) ERROR 라인 필터링
# 각 줄을 순회하면서 ERROR 포함된 줄만 추출
error_lines = [line for line in log_data.strip().split('\n') if 'ERROR' in line]

4) 전체구조

@log_time
def analyze_log(log_data):
    #IP추출
    #ERROR필터링
    #출력
    pass

"""

import re
import time

#샘플로그
log_data = """
2026-05-19 10:23:11 192.168.0.1 INFO 서버 시작
2026-05-19 10:24:05 192.168.0.2 ERROR 연결 실패
2026-05-19 10:25:33 192.168.0.1 INFO 요청 처리
2026-05-19 10:26:44 192.168.0.3 ERROR 타임아웃 발생
2026-05-19 10:27:01 192.168.0.2 INFO 재연결 성공
"""
"""
# Step 1 : IP 추출먼저
ip_pattern = r'\d+\.\d+\.\d+\.\d+'
ips = re.findall(ip_pattern, log_data)
print("=== IP 주소 목록 ===")
for ip in ips:
    print(ip)

# Step 2 : Error 필터링추가
print("\n=== ERROR 로그 ===")
error_lines = [line for line in log_data.strip().split('\n') if 'ERROR' in line]

1. log_data.strip() : 앞뒤 공백, 줄바꿈 제거
2. split('\n') : '\n' 기준으로 잘라서 리스트 만들기
3. for line in ... : 리스트에서 한줄씩 꺼내기
4. if 'ERROR' in line : 꺼낸 줄에 'ERROR'문자열 있으면 포함

[담을것 for 변수 in 리스트 if 조건]



for line in error_lines:
    print(line)

"""

# Strp3 데코레이터 추가
import time

# 데코레이터 먼저 선언 (코드 맨 위에 추가)
def log_time(func):  #데코레이터 함수(함수를 인자로 받음)
    def wrapper(*args, **kwargs): #내부 함수 (위치인자,키워드인자)
        start = time.time() #시작시간 기록
        result = func(*args, **kwargs) #원래 함수 실행
        end = time.time() #끝 시간 기록
        print(f"{func.__name__} 실행시간: {end-start:.3f}초") #시간 출력
        #여기서 func.__name__은 analayze_log
        return result       #원래 함수 결과로 반환
    return wrapper      #wrapper 함수 반환

# 기존 코드를 함수로 감싸기
@log_time
def analyze_log(log_data):
    # Step 1
    ip_pattern = r'\d+\.\d+\.\d+\.\d+'
    ips = re.findall(ip_pattern, log_data)
    print("=== IP 주소 목록 ===")
    for ip in ips:
        print(ip)

    # Step 2
    print("\n=== ERROR 로그 ===")
    error_lines = [line for line in log_data.strip().split('\n') if 'ERROR' in line]
    for line in error_lines:
        print(line)

# 함수 호출
analyze_log(log_data)