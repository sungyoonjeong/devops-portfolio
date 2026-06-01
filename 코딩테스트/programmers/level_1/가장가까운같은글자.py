"""
문자열 s 주어짐
s의 각 위치마다 자신보다 앞에 나왔으면서, 자신과 가장 가까운 곳에 있는 같은 글자가 어딨는지 파악
ex) s="banana", 각 글자들을 왼쪽부터 오른쪽으로 읽어나가면서 아래 순서로 진행
    1) b는 처음 나왔기 때문에 자신의 앞에 같은 글자 없음. => -1
    2) a는 처음 나왔기 때문에 => -1
    3) n은 처음 나왔기 때문에 => -1
    4) a는 자신보다 두 칸 앞에 a가 있음. => 2
    5) n은 자신보다 두 칸 앞에 n 있음. => 2
    6) a는 자신보다 두칸, 네칸 앞에 a가 있음. 이 중 가까운것은 두칸앞
    따라서 최종 결과물 = [-1,-1,-1,2,2,2]
"""

"""
딕셔너리 사용!!!
Step1) 문자를 key로, 문자의 가장 최근 인덱스 위치를 Value로 하는 last_position 딕셔너리 
Step2) 문자열을 처음부터 끝까지 한글자씩 추적
    - 처음 본 문자 : 결과 리스트에 -1 넣고, 딕셔너리에 현재 인덱스 저장
    - 이전에 본 문자 : (현재 인덱스 - 딕셔너리에 저장된 이전 인덱스)를 결과리스트에 넣고, 딕셔너리의 인덱스 업데이트
"""
def solution(s):
    answer = []
    # 각 문자의 최신 위치(인덱스)를 기록할 딕셔너리
    last_position={}
    
    # 인덱스(i)와 문자(char)를 동시에 가져옵니다.
    for i, char in enumerate(s):
        # 문자가 이미 딕셔너리에 있다면 (이전에 나온 적이 있다면)
        if char in last_position:
            # 현재 위치와 직전 위치의 차이를 정답에 추가
            answer.append(i-last_position[char])
        else:
            # 처음 나온 문자라면 -1을 추가
            answer.append(-1)
    
        # 현재 문자의 위치를 가장 최신 인덱스(i)로 업데이트/저장
        last_position[char] = i
    
    return answer

# 1. 딕셔너리에 저장할 때 (last_position[char] = i)반복문이 돌면서 last_position[char] = i를 만나면, 딕셔너리에 {문자: 현재 인덱스} 형태로 데이터를 저장하거나 업데이트합니다.
# 예를 들어, i = 1일 때 문자 char가 'a'였다면 $\rightarrow$ last_position['a'] = 1이 되어 딕셔너리에 {'a': 1}이 저장됩니다.

# 2. 값을 꺼내서 쓸 때 (last_position[char])이후에 똑같은 글자가 다시 나오면, last_position[char]는 방금 딕셔너리에 저장해 뒀던 그 인덱스 숫자로 변신합니다.
# s = "banana"에서 4번째 인덱스(i = 3)에 있는 두 번째 'a'를 만났다고 가정해 볼게요.
# 이때 char는 'a'입니다.last_position['a']를 호출하면, 아까 1번 인덱스에서 저장해 둔 숫자 1을 쏙 꺼내옵니다.
# 따라서 i - last_position[char] 문장은 최종적으로 3 - 1이 되어 거리인 2를 계산할 수 있게 되는 것입니다.

# --- 복사해서 바로 실행하는 테스트 코드 ---
if __name__ == "__main__":
    # 프로그래머스 예시 및 추가 테스트케이스
    test_cases = [
        {"s": "banana", "expected": [-1, -1, -1, 2, 2, 2]},
        {"s": "foobar", "expected": [-1, -1, 1, -1, -1, -1]},
        {"s": "aaaaa", "expected": [-1, 1, 1, 1, 1]}  # 똑같은 글자만 연속될 때
    ]
    
    print("=== 테스트 케이스 실행 시작 ===")
    for idx, case in enumerate(test_cases, 1):
        s_val = case["s"]
        expected_val = case["expected"]
        
        result = solution(s_val)
        
        if result == expected_val:
            print(f"테스트 {idx}번 결과: 성공 (결과: {result})")
        else:
            print(f"테스트 {idx}번 결과: 실패 (결과: {result} / 기대값: {expected_val})")
            
    print("=== 테스트 완료 ===")