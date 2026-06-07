"""
absolutes : 정수들의 절대값을 차례대로 담은 정수 배열
signs : 정수들의 부호를 차례대로 담은 불리언 배열
return : 실제 정수들의 합
"""
def solution(absolutes, signs):
    answer = 123456789
    sum = 0  # 부호가 반영된 실제 정수들의 총합을 저장할 변수입니다.
    
    # 배열의 길이만큼 반복하며 각 인덱스(i)의 값과 부호를 확인합니다.
    for i in range(len(signs)):
        # 만약 signs[i]가 True라면 양수이므로, absolutes[i] 값을 더해줍니다.
        if signs[i] == True:
            sum += absolutes[i]
        # signs[i]가 False라면 음수이므로, absolutes[i] 값을 빼줍니다.
        else:
            sum -= absolutes[i]
            
    answer = sum  # 계산된 총합을 결과 변수에 저장합니다.
    return answer  # 최종 합을 반환합니다.


# --- 테스트 실행 함수 ---
def run_tests():
    # 입출력 예시 데이터: (absolutes, signs, 기대하는 정답)
    test_cases = [
        ([4, 7, 12], [True, False, True], 9),
        ([1, 2, 3], [False, False, True], 0)
    ]
    
    print("========== 테스트 시작 ==========")
    for idx, (absolutes, signs, expected) in enumerate(test_cases, 1):
        result = solution(absolutes, signs)
        is_success = "통과" if result == expected else "실패"
        print(f"테스트 {idx}: 결과 {result} / 기대값 {expected} -> [{is_success}]")
    print("========== 테스트 종료 ==========")

# 테스트 함수 실행
run_tests()