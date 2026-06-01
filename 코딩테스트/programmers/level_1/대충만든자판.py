"""
휴대폰 자판 : 하나의 키에 여러개의 문자 할당 가능
    - 동일한 키 연속해서 빠르게 누르면 할당된 순서대로 문자 바뀜
    - 1번키에 "A","B","C" 있으면 1번누를때 "A", 2번누를때 "B", 3번 누를때 "C"

이 휴대폰 자판은 키의 개수가 1개부터 최대 100개
특정 키를 눌렀을 때 입력되는 문자들도 무작위로 배열
    - 같은 문자 자판 전체에 여러번 할당된 경우 있음
    - 키 하나에 같은 문자가 여러번 할당된 경우 있음
    - 아예 할당되지 않은 경우 있음

이 휴대폰 자판을 이용해 문자열 작성할때, 키를 최소 몇번 눌러야 그 문자열을 작성할 수 있는지 파악

keymap : 1번 키부터 차례대로 할당된 문자들이 순서대로 담긴 문자열배열
targets : 입력하려는 문자열들이 담긴 문자열 배열

각 문자열을 작성하기 위해 최소 몇 번씩 눌러야 하는지 순서대로 배열에 담아 return
"""
"""
<문제풀이>
Step1) 문제 분석 및 핵심 아이디어 도출
    - 조건 : 하나의 키에 여러문자가 연속으로 배치, 자판 전체에 동일한 문자 등장 가능
    - 목표 : targets에 담긴 문자열을 만들기 위해 필요한 최소 키 누름 횟수의 합
    - 아이디어 
        1) 알파벳 A부터 Z까지 각 문자를 치기 위한 최소 횟수를 저장하는 딕셔너리(해시맵)
        2) keymap을 순회하면서 각 문자가 처음 등장하는 위치(인덱스 + 1)를 확인, 기존에 저장된 값보다 작다면 더 작은 값으로 갱신
        3) 문자열을 만들때 딕셔너리를 조회하여 합산, 만약 자판에 없는 문자가 포함되어있다면 -1 반환

Step2) 알고리즘 설계
    1) 문자별 최소 누름 횟수 딕셔너리 정의
        - keymap을 바탕으로 특정 문자를 입력하기 위한 최소 횟수를 저장할 key_dict를 생성
    2) keymap을 순회하며 최솟값 갱신
        - keymap 안에 있는 각 문자열을 돕니다.
        - 문자열의 각 글자에 대해 {현재 인덱스 +1}(누른 횟수)를 구함
        - key_dict 에 해당 문자가 없거나, 새로 구한 횟수가 기존 횟수보다 작다면 값을 업데이트

    3) targets를 순회하며 결과 계산
        - 목표 문자열(targets)의 각 글자를 확인
        - 모든 글자가 key_dict에 존재하면 횟수를 더해줌
        - 만약 단 하나라도 key_dict에 없다면, 그 문자열은 만들수 없으므로 -1 처리함
"""
def solution(keymap, targets):
    # 정답을 담을 빈 리스트를 준비합니다.
    answer = []
    
    # 각 알파벳 문자를 입력하기 위한 '최소 누름 횟수'를 저장할 빈 딕셔너리를 만듭니다.
    key_dict = {}
    
    # keymap 배열에 있는 자판들을 하나씩 꺼내어 순회합니다.
    for key in keymap:
        # 각 자판 문자열의 인덱스(위치)와 해당 글자(char)를 하나씩 꺼냅니다.
        # enumerate(key) : 리스트나 문자열을 돌면서 현재 몇번째(인덱스)이고, 그 값이 무엇인지 동시에 알려주는 역할
        for index, char in enumerate(key):
            # 사용자가 자판을 눌러야 하는 횟수는 '인덱스 + 1'번 입니다. (0번 인덱스 = 1번 누름)
            press_count = index + 1
            
            # 딕셔너리에 아직 등록되지 않은 문아이거나, 기존에 등록된 횟수보다 현재 횟수가 더 적다면
            if char not in key_dict or press_count < key_dict[char]:
                # 해당 문자를 입력하기 위한 최소 횟수를 현재 횟수로 갱신하거나 새로 등록합니다.
                key_dict[char] = press_count
                
    # 입력하려는 목표 문자열(targets)들을 하나씩 꺼내어 순회합니다.
    for target in targets:
        # 현재 문자열을 만들기 위해 누른 누적 횟수를 저장할 변수를 0으로 초기화합니다.
        total_press = 0
        # 현재 문자열을 자판으로 완전히 만들 수 있는지 여부를 나타내는 플래그입니다.
        is_possible = True
        
        # 목표 문자열의 글자들을 한 글자씩 꺼내어 확인합니다.
        for char in target:
            # 만약 자판 정보가 저장된 딕셔너리에 해당 글자가 존재한다면
            if char in key_dict:
                # 그 글자를 치기 위한 최소 누름 횟수를 누적 합산합니다.
                total_press += key_dict[char]
            # 자판에 없는 글자가 포함되어 있다면 (만들 수 없는 문자열인 경우)
            else:
                # 만들 수 없음을 표시하기 위해 플래그를 False로 바꿉니다.
                is_possible = False
                # 이미 만들 수 없는 문자열이므로 내부 루프를 중단(break)하고 빠져나갑니다.
                break
        
        # 글자들을 모두 확인한 후, 정상적으로 만들 수 있는 문자열이었다면
        if is_possible:
            # 계산된 총 누름 횟수를 정답 리스트에 추가합니다.
            answer.append(total_press)
        # 자판에 없는 글자가 있어서 만들지 못한 문자열이었다면
        else:
            # 문제 조건에 따라 -1을 정답 리스트에 추가합니다.
            answer.append(-1)
            
    # 모든 목표 문자열에 대한 계산이 끝나면 최종 정답 배열을 반환합니다.
    return answer



# --- 테스트케이스 실행 코드 ---

# 문제에 주어진 입출력 예시 데이터 리스트
test_cases = [
    {
        "keymap": ["ABACD", "BCEFD"],
        "targets": ["ABCD", "AABB"],
        "expected": [9, 4]
    },
    {
        "keymap": ["AA"],
        "targets": ["B"],
        "expected": [-1]
    },
    {
        "keymap": ["AGZ", "BSSS"],
        "targets": ["ASA", "BGZ"],
        "expected": [4, 6]
    }
]

# 각 테스트케이스를 순회하며 검증
for i, case in enumerate(test_cases, 1):
    result = solution(case["keymap"], case["targets"])
    is_success = result == case["expected"]
    
    print(f"== 테스트 케이스 {i} ==")
    print(f"입력값(keymap)  : {case['keymap']}")
    print(f"입력값(targets) : {case['targets']}")
    print(f"기댓값(expected): {case['expected']}")
    print(f"실행결과(result): {result}")
    print(f"결과: {'정답 (Pass)' if is_success else '오답 (Fail)'}")
    print("-" * 30)