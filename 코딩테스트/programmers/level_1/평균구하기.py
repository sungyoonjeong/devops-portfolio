"""
arr : 정수를 담고 있는 배열
return : arr의 평균값
"""
def solution(arr):
    answer = 0
    
    sum_arr = sum(arr)
    avg_arr = sum_arr/len(arr)
    
    answer = avg_arr
    return answer

# 2. 테스트를 위한 코드 (아래 내용을 복사해서 붙여넣으세요)
if __name__ == "__main__":
    # 프로그래머스 입출력 예시 및 추가 테스트 케이스
    test_cases = [
        {"input": [1, 2, 3, 4], "expected": 2.5},
        {"input": [5, 5], "expected": 5.0},
        {"input": [10], "expected": 10.0},          # 원소가 1개인 경우
        {"input": [-10, 10, -5, 5], "expected": 0.0}, # 음수가 포함된 경우
        {"input": [1, 3, 5, 7, 9], "expected": 5.0}   # 홀수 개수 배열인 경우
    ]
    
    print("=== '평균 구하기' 테스트 시작 ===")
    all_passed = True
    
    for idx, case in enumerate(test_cases, 1):
        arr = case["input"]
        expected = case["expected"]
        result = solution(arr)
        
        if result == expected:
            print(f"테스트 {idx}: 성공 (입력값: {arr} -> 결과: {result})")
        else:
            print(f"테스트 {idx}: 실패 ❌ (입력값: {arr} | 기댓값: {expected} | 결과: {result})")
            all_passed = False
            
    print("---------------------------------")
    if all_passed:
        print("🎉 모든 테스트 케이스를 완벽하게 통과했습니다!")
    else:
        print("⚠️ 실패한 케이스가 있습니다. 코드를 다시 확인해 보세요.")