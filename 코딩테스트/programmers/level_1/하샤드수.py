"""
양의정수 x가 하샤드 수가 되려면 x의 자릿수의 합으로 x가 나누어져야함

Ex) 18의 자릿수의 합은 1+8=9이고, 18은 9로 나누어 떨어지므로 하샤드 수

자연수 x를 입력받아 x가 하샤드 수인지 아닌지 검사
"""
def solution(x):
    answer = True
    
#     harshad = list(str(x))
#     sum_harshad = 0
    
#     for i in harshad:
#         sum_harshad += int(i)
    
#     if x%sum_harshad == 0:
#         answer = True
#     else:
#         answer = False
    
    sum_harshad = sum(int(i) for i in str(x))
    
    answer = x % sum_harshad == 0
    
    return answer

# 2. 테스트를 위한 코드 (아래 내용을 복사해서 붙여넣으세요)
if __name__ == "__main__":
    # 프로그래머스 입출력 예시 데이터
    test_cases = [
        {"input": 10, "expected": True},
        {"input": 12, "expected": True},
        {"input": 11, "expected": False},
        {"input": 13, "expected": False},
        {"input": 1,  "expected": True},   # 한 자리 수 예시 추가
        {"input": 10000, "expected": True} # 제한 조건 최대치 예시 추가
    ]
    
    print("=== 테스트 시작 ===")
    all_passed = True
    
    for idx, case in enumerate(test_cases, 1):
        x = case["input"]
        expected = case["expected"]
        result = solution(x)
        
        if result == expected:
            print(f"테스트 {idx}: 성공 (입력값: {x} -> 결과: {result})")
        else:
            print(f"테스트 {idx}: 실패 ❌ (입력값: {x} | 기댓값: {expected} | 결과: {result})")
            all_passed = False
            
    print("-------------------")
    if all_passed:
        print("🎉 모든 테스트 케이스를 통과했습니다! 제출하셔도 좋습니다.")
    else:
        print("⚠️ 실패한 케이스가 있습니다. 코드를 다시 확인해 보세요.")