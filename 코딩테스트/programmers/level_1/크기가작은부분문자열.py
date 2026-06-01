"""
t,p : 숫자로 이루어진 문자열

t에서 p와 길이가 가은 부분 문자열 중에서, 이 부분 문자열이 나타내는 수가 p가 나타내는 수보다 작거나 같은 것이 나오는 횟수를 return하는 함수

ex) t="3141592", p="271" 인 경우, t의 길이가 3인 부분 문자열은 314,141,415,159,592 입니다.
이 문자열이 나타내는 수 중에서 271보다 작거나 같은수는 141, 159 2개
"""
"""
Step1) p의 길이를 먼저 확인
Step2) t를 p의 길이 만큼 잘라서 보관
Step3) 보관한 수들과 p를 비교하여 작거나 같으면 answer에 +1
"""
def solution(t, p):
    answer = 0
    
    length = len(p)
    # t에서 p의 길이만큼 잘라낼 수 있는 마지막 시작 인덱스까지만 반복합니다.
    for i in range(len(t)-length+1):
        # i부터 p의 길이(length)만큼 문자열을 슬라이싱합니다.
        box = t[i:i+length]
        # 숫자로 비교하여 작거나 같으면 정답 카운트를 올립니다.
        if int(box)<=int(p):
            answer+=1
            
    return answer


# --- 파이썬에서 직접 돌려볼 수 있는 테스트케이스 실행 코드 ---
if __name__ == "__main__":
    # 프로그래머스 입출력 예시
    test_cases = [
        {"t": "3141592", "p": "271", "expected": 2},
        {"t": "500220839878", "p": "7", "expected": 8},
        {"t": "10203", "p": "15", "expected": 3}
    ]
    
    print("=== 테스트 케이스 실행 시작 ===")
    for idx, case in enumerate(test_cases, 1):
        t_val = case["t"]
        p_val = case["p"]
        expected_val = case["expected"]
        
        # 함수 실행
        result = solution(t_val, p_val)
        
        # 결과 비교 및 출력
        if result == expected_val:
            print(f"테스트 케이스 #{idx}: 성공 (결과: {result} / 기대값: {expected_val})")
        else:
            print(f"테스트 케이스 #{idx}: 실패 (결과: {result} / 기대값: {expected_val})")
            
    print("=== 테스트 완료 ===")