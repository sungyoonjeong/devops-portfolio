"""
2. 로그 분석 스크립트

배운 것: 8장 정규표현식 + 5장 예외처리
만들 것: 어제 심화 문제 확장

추가할 것:
- IP별 접속 횟수 카운트
- 날짜별 ERROR 개수 통계
"""

import re
import time

# 샘플 로그
log_data = """
2026-05-19 10:23:11 192.168.0.1 INFO 서버 시작
2026-05-19 10:24:05 192.168.0.2 ERROR 연결 실패
2026-05-19 10:25:33 192.168.0.1 INFO 요청 처리
2026-05-19 10:26:44 192.168.0.3 ERROR 타임아웃 발생
2026-05-19 10:27:01 192.168.0.2 INFO 재연결 성공
"""

# 데코레이터
def log_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} 실행시간: {end-start:.3f}초")
        return result
    return wrapper

@log_time
def analyze_log(log_data):
    # Step 1: IP 추출
    ip_pattern = r'\d+\.\d+\.\d+\.\d+'
    ips = re.findall(ip_pattern, log_data)
    print("=== IP 주소 목록 ===")
    for ip in ips:
        print(ip)

    # Step 2: ERROR 필터링
    print("\n=== ERROR 로그 ===")
    error_lines = [line for line in log_data.strip().split('\n') if 'ERROR' in line]
    for line in error_lines:
        print(line)

    # Step 3: IP별 접속 횟수
    print("\n=== IP별 접속 횟수 ===")
    ip_count = {}
    for ip in ips:
        if ip in ip_count:
            ip_count[ip] += 1
        else:
            ip_count[ip] = 1
    for ip, count in ip_count.items():
        print(f"{ip}: {count}회")

# 함수 호출
analyze_log(log_data)