"""
조카는 "aya","ye","woo","ma" 네가지발음과 조합해서 만들수 있는 발음밖에 하지 못함
연속해서 같은 발음을 하는것을 어려워함

babbling : 문자열 배열
return : 조카가 발음할 수 있는 단어의 개수
"""
"""
Step 1) 조카가 발음할 수 있는 네 가지 발음을 리스트(can)에 저장합니다.

Step 2) babbling 배열에 있는 단어들을 하나씩 꺼내어 검사합니다.

Step 3) 네 가지 발음을 하나씩 순회하면서, 같은 발음이 연속으로 연속해서 나오는지(b * 2) 먼저 체크합니다. 연속된 발음이 있다면 그 단어는 발음할 수 없으므로 탈락시킵니다.

Step 4) 연속된 발음이 없다면, 해당 발음을 공백 문자(예: " ")로 치환합니다.

주의: 빈 문자 ""로 치환하면 "yeye"에서 앞의 "ye"를 지웠을 때 뒤의 "ye"가 붙으면서 예기치 못한 연속 발음 처리가 되거나, 다른 문자끼리 결합할 수 있으므로 치환할 때 반드시 공백 공백(" ")을 주어야 합니다.

Step 5) 모든 발음을 치환한 후, 문자열의 공백을 다 제거했을 때(strip()) 빈 문자열("")만 남는다면 조카가 완벽하게 발음할 수 있는 단어이므로 answer를 1 증가시킵니다.
"""
def solution(babbling):
    answer = 0
    # 조카가 발음할 수 있는 4가지 기본 발음을 리스트로 정의합니다.
    can = ["aya", "ye", "woo", "ma"]
    
    # 입력받은 단어 배열(babbling)에서 단어를 하나씩 꺼내어 확인합니다.
    for word in babbling:
        # 4가지 발음을 하나씩 대조해봅니다.
        for b in can:
            # 만약 같은 발음이 연속해서 2번 등장한다면(예: "ayaaya") 조카는 발음할 수 없습니다.
            if b * 2 in word:
                break # 더 이상 확인할 필요가 없으므로 내부 루프를 탈출합니다.
            
            # 연속된 발음이 아니라면, 해당 발음 부분을 공백 하나(" ")로 치환합니다.
            # 빈 문자("")로 바꾸면 "w" + "oo" 처럼 찢어져 있던 문자가 합쳐져 발음 가능한 단어로 변하는 오류가 생깁니다.
            word = word.replace(b, " ")
            
        # 4가지 발음을 다 치환하고 난 뒤, 문자열 양쪽의 공백을 제거했을 때 빈 문자열("")만 남는다면
        # 오직 조카가 발음할 수 있는 단어들로만 이루어졌다는 뜻입니다.
        if word.strip() == "":
            answer += 1 # 발음 가능한 단어 개수를 1 증가시킵니다.
            
    # 최종적으로 발음할 수 있는 단어의 총 개수를 반환합니다.
    return answer

# ==========================================
# 🧪 [옹알이 (2)] 테스트 및 검증 코드
# ==========================================
if __name__ == "__main__":
    print("=== [옹알이 (2)] 테스트 시작 ===")
    
    # 테스트 케이스 1
    babbling1 = ["aya", "yee", "u", "maa"]
    expected1 = 1
    result1 = solution(babbling1)
    print(f"\n[테스트 1]")
    print(f"입력값 〉 babbling = {babbling1}")
    print(f"기댓값 〉 {expected1}")
    print(f"실행결과 〉 {result1}")
    print(f"통과여부 〉 {'성공  (수정됨)' if result1 == expected1 else '실패 ❌'}")
    
    # 테스트 케이스 2
    babbling2 = ["ayaye", "uuu", "yeye", "yemawoo", "ayaayaa"]
    expected2 = 2
    result2 = solution(babbling2)
    print(f"\n[테스트 2]")
    print(f"입력값 〉 babbling = {babbling2}")
    print(f"기댓값 〉 {expected2}")
    print(f"실행결과 〉 {result2}")
    print(f"통과여부 〉 {'성공  (수정됨)' if result2 == expected2 else '실패 ❌'}")

    print("\n==========================================")