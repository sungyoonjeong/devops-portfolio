"""
n : 자연수
return : n을 3진법 상에서 앞뒤로 뒤집은 후, 이를 다시 10진법으로 표현한 수

ex) n=45 => 3진법: 1200 => 앞뒤반전 : 0021 => 10진법 : 7

<알고리즘>
1) 3진법 변환 및 뒤집기
    - n을 3으로 나눈 나머지를 문자열에 계속 더해줌
    - 자동으로 뒤집힌 형태의 문자열 만들어짐
    - n이 0이 될때까지 n을 3으로 나눈 몫으로 갱신하며 반복
2) 10진법으로 재변환
    - 뒤집힌 3진법 문자열을 파이썬의 int(문자열,3)함수를 이용해 10진법으로 변환
"""

def solution(n):
    ternary_reversed = ""  # 앞뒤 뒤집힌 3진법 문자를 이어 붙일 빈 문자열을 생성합니다.
    
    # n이 0보다 클 때까지 반복하며 3진법 변환(동시에 뒤집기)을 진행합니다.
    while n > 0:
        # n을 3으로 나눈 나머지를 구합니다. (3진법의 각 자리수)
        remainder = n % 3
        # 나머지를 문자열로 변환하여 뒤에 붙입니다. (순서대로 붙이므로 자동으로 뒤집힙니다.)
        ternary_reversed += str(remainder)
        # n을 3으로 나눈 몫으로 갱신하여 다음 자리수를 구하도록 준비합니다.
        n = n // 3
        
    # int(문자열, 3) 함수를 사용하여 3진법 형태의 문자열을 다시 10진수 정수로 변환합니다.
    answer = int(ternary_reversed, 3)
    return answer


# --- 테스트 실행 함수 ---
def run_tests():
    # 입출력 예시 데이터: (입력값 n, 기대하는 정답)
    test_cases = [
        (45, 7),
        (125, 229)
    ]
    
    print("========== 테스트 시작 ==========")
    for idx, (n, expected) in enumerate(test_cases, 1):
        result = solution(n)
        is_success = "통과" if result == expected else "실패"
        print(f"테스트 {idx}: 입력값 {n} -> 결과 {result} / 기대값 {expected} -> [{is_success}]")
    print("========== 테스트 종료 ==========")

# 테스트 함수 실행
run_tests()