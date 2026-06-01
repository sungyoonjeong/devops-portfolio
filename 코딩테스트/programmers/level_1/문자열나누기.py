"""
문자열 s 입력되었을때, 아래규칙대로 여러 문자열로 분해하려고 함
    1) 첫글자 = x
    2) 문자열을 왼쪽에서 오른쪽으로 읽어나가면서 x와 x가 아닌 다른 글자들의 횟수 카운팅
    3) 처음으로 두 횟수가 같아지는 순간 멈추고, 지금까지 읽은 문자열을 분리
    4) s에서 분리한 문자열을 빼고 남은 부분에 대해 위 1~3 과정 반복
    5) 남은 부분이 없다면 종료
    6) 만약 두 횟수가 다른 상태에서 더 이상 읽을 글자가 없다면
        - 지금까지 읽은 문자열 분리 후 종료
"""
"""
Step1) 문자열을 한 글자씩 순회함녀서 첫글자(x)를 정함
Step2) 두 개의 카운터 변수를 둠
        - same_count : 첫글자 x와 같은 글자가 나온 횟수
        - diff_count : 첫글자 x와 다른 글자가 나온 횟수
Step3) 두 카운터의 숫자가 같아지는 순간 문자열을 분리하고(anser+=1)
Step4) 카운터를 초기화 한 뒤 다음 글자를 새로운 x로 잡고 다시 시작
Step5) 끝까지 다 읽었는데 두 카운터가 다르더라도, 남은 조각이 있으면 하나의 문자열로 취급, 분리
"""
def solution(s):
    answer = 0
    
    # 현재 분리 중인 부분 문자열의 첫 글자 (x)
    x = ""
    same_count = 0
    diff_count = 0
    
    for char in s:
        # 첫 글자가 지정되지 않았다면 현재 문자를 첫 글자 x로 지정
        if same_count == 0:
            x = char
            same_count = 1
        else:
            # 첫 글자 x와 비교하여 카운트 증가
            if char == x:
                same_count += 1
            else:
                diff_count += 1
        
        # x의 개수와 x가 아닌 글자의 개수가 같아지면 싹둑 자르기
        if same_count == diff_count:
            answer += 1
            # 다음 턴을 위해 카운트 리셋 (same_count가 0이 되면 다음 루프 때 새로운 x가 잡힙니다)
            same_count = 0
            diff_count = 0
            
    # 루프가 끝났는데 카운트가 남아있다면 (즉, 다 읽었는데 두 횟수가 다른 상태로 끝난 경우)
    # 남은 부분도 하나의 문자열로 분리해야 하므로 1을 더해줍니다.
    if same_count > 0:
        answer += 1
        
    return answer


# --- 복사해서 바로 실행하는 테스트 코드 ---
if __name__ == "__main__":
    test_cases = [
        {"s": "banana", "expected": 3},
        {"s": "abracadabra", "expected": 6},
        {"s": "aaabbaccccabba", "expected": 3}
    ]
    
    print("=== 문자열 나누기 테스트 시작 ===")
    for idx, case in enumerate(test_cases, 1):
        res = solution(case["s"])
        status = "성공" if res == case["expected"] else "실패"
        print(f"테스트 {idx}번 ({case['s']}): {status} (결과: {res})")
    print("=== 테스트 완료 ===")