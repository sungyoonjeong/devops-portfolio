"""
콜라츠 추측 : 주어진 수가 1이 될 때까지 다음 작업을 반복하면 모든 수를 1로 만들 수 있다는 추측
1.1) 입력된 수가 짝수라면 2로 나눈다.
1.2) 입력된 수가 홀수라면 3을 곱하고 1을 더한다.
2) 결과로 나온 수에 같은 작업을 1이 될 때까지 반복한다.
"""
def solution(num):
    answer = 0
    count = 0
    
    if num == 1:
        answer = 0
        
    while num != 1:
        if num % 2 == 0:
            num = num // 2
            count += 1
        else:
            num = num * 3 + 1
            count += 1
            
        # 500번 이상 반복되면 바로 -1을 반환하고 함수 종료!
        if count >= 500:
            return -1
    
    # 500번 미만으로 1이 되었다면 정상적으로 count 반환
    answer = count
    return answer

# 2. 테스트를 위한 코드 (아래 내용을 복사해서 붙여넣으세요)
if __name__ == "__main__":
    # 프로그래머스 입출력 예시 및 중요 예외 케이스
    test_cases = [
        {"input": 6, "expected": 8},
        {"input": 16, "expected": 4},
        {"input": 626331, "expected": -1},
        {"input": 1, "expected": 0},       # 숫자가 처음부터 1인 경우 (중요 조건!)
        {"input": 4, "expected": 2}        # 4 -> 2 -> 1 (총 2번)
    ]
    
    print("=== '콜라츠 추측' 테스트 시작 ===")
    all_passed = True
    
    for idx, case in enumerate(test_cases, 1):
        num = case["input"]
        expected = case["expected"]
        result = solution(num)
        
        if result == expected:
            print(f"테스트 {idx}: 성공 (입력값: {num} -> 결과: {result})")
        else:
            print(f"테스트 {idx}: 실패 ❌ (입력값: {num} | 기댓값: {expected} | 결과: {result})")
            all_passed = False
            
    print("---------------------------------")
    if all_passed:
        print("🎉 모든 테스트 케이스를 완벽하게 통과했습니다! 제출하셔도 좋습니다.")
    else:
        print("⚠️ 실패한 케이스가 있습니다. 코드를 다시 확인해 보세요.")