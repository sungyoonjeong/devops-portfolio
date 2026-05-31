"""
아래 규칙으로 카드에 적힌 단어들을 사용해 원하는 순서의 단어배열 만듬
    - 원하는 카드 뭉치에서 카드를 순서대로 한장씩 사용
    - 한 번 사용한 카드는 재사용 안됨
    - 카드를 사용하지 않고 다음 카드로 넘어갈수 없음
    - 기존에 주어진 카드 뭉치의 단어 순서 바꿀 수 없음

card1, card2 : 문자열로 이루어진 배열
goal : 원하는 단어 배열
"""
"""
Step1) card1과 card2를 추적할 인덱스 포인터 idx1=0, idx2=0 선언
Step2) goal리스트를 for문으로 추적하면서 단어를 하나씩 꺼냄
Step3) 단어를 비교할 때, 인덱스가 카드 배열의 길이를 벗어나지 않는지(idx<len(cards)) 먼저 체크해야 에러가 나지않음
Step4) 조건이 맞으면 포인터를 뒤로 옮기고, 어떤 카드 뭉치에서도 단어를 찾을 수 없으면 실패 처리
"""

def solution(cards1, cards2, goal):
    # answer 변수를 빈 문자열로 초기화합니다.
    answer = ''
    
    idx1 = 0
    idx2 = 0
    
    for word in goal:
        if idx1 < len(cards1) and cards1[idx1] == word:
            idx1 += 1
        elif idx2 < len(cards2) and cards2[idx2] == word:
            idx2 += 1
        else:
            # 카드를 만들 수 없다면 answer에 "No"를 저장하고
            answer = "No"
            # 더 이상 검사할 필요가 없으므로 반복문(for문)을 빠져나갑니다.
            break
            
    # 만약 반복문을 무사히 마쳤는데도 answer가 비어있다면, 성공적으로 다 만든 것이므로 "Yes"를 넣습니다.
    if not answer:
        answer = "Yes"
        
    # 기존에 적어두셨던 return answer를 그대로 활용하여 최종 결과를 반환합니다.
    return answer


# --- 테스트케이스 실행 코드 ---

# 문제의 입출력 예시 데이터 리스트
test_cases = [
    {
        "cards1": ["i", "drink", "water"],
        "cards2": ["want", "to"],
        "goal": ["i", "want", "to", "drink", "water"],
        "expected": "Yes"
    },
    {
        "cards1": ["i", "water", "drink"],
        "cards2": ["want", "to"],
        "goal": ["i", "want", "to", "drink", "water"],
        "expected": "No"
    }
]

# 각 테스트케이스를 순회하며 검증
for i, case in enumerate(test_cases, 1):
    result = solution(case["cards1"], case["cards2"], case["goal"])
    is_success = result == case["expected"]
    
    print(f"== 테스트 케이스 {i} ==")
    print(f"입력값(cards1)  : {case['cards1']}")
    print(f"입력값(cards2)  : {case['cards2']}")
    print(f"입력값(goal)    : {case['goal']}")
    print(f"기댓값(expected): '{case['expected']}'")
    print(f"실행결과(result): '{result}'")
    print(f"결과: {'정답 (Pass)' if is_success else '오답 (Fail)'}")
    print("-" * 30)