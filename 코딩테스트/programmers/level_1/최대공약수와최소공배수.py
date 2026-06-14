"""
두 수를 입력받아 두 수의 최대공약수와 최소공배수를 반환하는 함수

return : 배열의 맨 앞에 최대공약수, 그다음 최소공배수를 넣어 반환
"""
# <math함수 사용했을때 방법>

# import math

# def solution(n, m):
#     answer = []
    
#     gcd = math.gcd(n,m)
    
#     lcm = (n*m)//gcd
    
#     answer = [gcd,lcm]
    
#     return answer

# <math함수 사용하지 않고 작성하는법>
def solution(n, m):
    # 원래 값을 보존하기 위해 변수에 복사(최소공배수 계산용)
    original_n, original_m = n, m
    
    # 1. 유클리드 호제법으로 최대공약수 구하기
    while m != 0:
        n, m = m, n % m
    gcd = n # while문이 끝나면 n에 최대공약수가 남음
    
    # 2. 공식으로 최소공배수 구하기
    # [수학 공식]
    # 두 자연수의 곱 = 최대공약수(GCD) * 최소공배수(LCM)
    # 따라서, 최소공배수(LCM) = (두 수의 곱) // 최대공약수(GCD)
    lcm = (original_n * original_m) // gcd
    
    answer = [gcd, lcm]
    return answer


# 3. 로컬 환경 검증용 테스트 코드
if __name__ == "__main__":
    # 프로그래머스 입출력 예시 및 추가 테스트 케이스
    test_cases = [
        {"n": 3, "m": 12, "expected": [3, 12]},
        {"n": 2, "m": 5,  "expected": [1, 10]},
        {"n": 1, "m": 10, "expected": [1, 10]},   # 한 숫자가 1인 경우
        {"n": 7, "m": 7,  "expected": [7, 7]}     # 두 숫자가 같은 경우
    ]
    
    print("=== '최대공약수와 최소공배수' 테스트 시작 ===")
    all_passed = True
    
    for idx, case in enumerate(test_cases, 1):
        n_val = case["n"]
        m_val = case["m"]
        expected = case["expected"]
        result = solution(n_val, m_val)
        
        if result == expected:
            print(f"테스트 {idx}: 성공 (입력값: {n_val}, {m_val} -> 결과: {result})")
        else:
            print(f"테스트 {idx}: 실패 ❌ (입력값: {n_val}, {m_val} | 기댓값: {expected} | 결과: {result})")
            all_passed = False
            
    print("---------------------------------------------")
    if all_passed:
        print("🎉 모든 테스트 케이스를 완벽하게 통과했습니다! 제출하셔도 좋습니다.")
    else:
        print("⚠️ 실패한 케이스가 있습니다. 코드를 다시 확인해 보세요.")