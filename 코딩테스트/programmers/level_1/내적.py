"""
a,b : 길이가 같은 1차원 정수 배열
return : a,b의 내적
내적: a[0]*b[0] + a[1]*b[1] + ... + a[n-1]*b[n-1]
n=a,b의 길이
"""
def solution(a, b):
    answer = 1234567890
    result = 0
    
    for i in range(len(a)):
        result += a[i] * b[i]
        answer = result
    return answer

# --- 테스트 실행 함수 ---
def run_tests():
    # 프로그래머스 공식 입출력 예시 데이터
    # 구조: (배열 a, 배열 b, 기대하는 정답)
    test_cases = [
        ([1, 2, 3, 4], [-3, -1, 0, 2], 3),
        ([-1, 0, 1], [1, 0, -1], -2)
    ]
    
    print("========== 테스트 시작 ==========")
    for idx, (a, b, expected) in enumerate(test_cases, 1):
        result = solution(a, b)
        is_success = "통과" if result == expected else "실패"
        print(f"테스트 {idx}: 결과 {result} / 기대값 {expected} -> [{is_success}]")
    print("========== 테스트 종료 ==========")

# 테스트 함수 호출
run_tests()