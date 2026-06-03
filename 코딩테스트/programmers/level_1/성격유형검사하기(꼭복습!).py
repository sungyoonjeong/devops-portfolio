"""
성격 유형은 총 4가지 지표, 8가지 유형(R, T, C, F, J, M, A, N)이 있습니다.

각 질문마다 선택지(choices)는 1~7번까지 있으며, 4번(모르겠음)을 기준으로 점수가 나뉩니다.

1~3번(비동의 관련): survey[i]의 첫 번째 글자에 각각 3, 2, 1점이 부여됩니다.

5~7번(동의 관련): survey[i]의 두 번째 글자에 각각 1, 2, 3점이 부여됩니다.

모든 질문을 계산한 후, 지표별로 점수가 더 높은 유형을 고릅니다. 단, 점수가 같으면 사전 순으로 빠른 유형을 선택하여 4글자의 성격 유형 문자열을 만듭니다.

<알고리즘>
Step 1) 8가지 성격 유형의 점수를 저장할 딕셔너리(scores)를 만들고 모든 초기 점수를 0으로 설정합니다.

Step 2) survey와 choices 배열을 동시에 하나씩 순회합니다.

Step 3) 선택한 값(choice)에 따라 점수와 점수를 받을 성격 유형을 계산합니다:
    - choice < 4 이면: 점수는 4 - choice 이고, 대상은 survey[i][0] (비동의)
    - choice > 4 이면: 점수는 choice - 4 이고, 대상은 survey[i][1] (동의)
    - choice == 4 이면: 점수를 얻지 않으므로 건너뜁니다.

Step 4) 계산된 점수를 딕셔너리의 해당 성격 유형에 누적합니다.

Step 5) 1번 지표(R vs T), 2번 지표(C vs F), 3번 지표(J vs M), 4번 지표(A vs N)를 각각 비교하여 점수가 더 크거나 같은 쪽의 유형을 정답 문자열에 더합니다. (사전 순으로 이미 정렬해서 비교하므로 같을 때는 앞의 문자가 선택되게 만듭니다.)
"""
def solution(survey, choices):
    answer = ''
    
    # 8가지 성격 유형의 점수를 기록할 딕셔너리를 0점으로 초기화합니다.
    scores = {'R': 0, 'T': 0, 'C': 0, 'F': 0, 'J': 0, 'M': 0, 'A': 0, 'N': 0}
    
    # zip 함수를 사용해 질문(survey)과 선택지(choices)를 하나씩 매칭하며 순회합니다.
    for sur, choice in zip(survey, choices):
        # 1~3번 선택지는 비동의 영역으로, 첫 번째 성격 유형(sur[0])이 점수를 얻습니다.
        if choice < 4:
            scores[sur[0]] += (4 - choice)  # 1번은 3점, 2번은 2점, 3번은 1점 계산
        # 5~7번 선택지는 동의 영역으로, 두 번째 성격 유형(sur[1])이 점수를 얻습니다.
        elif choice > 4:
            scores[sur[1]] += (choice - 4)  # 5번은 1점, 6번은 2점, 7번은 3점 계산
            
    # 4개의 지표 순서대로 두 유형의 점수를 비교하여 최종 성격 유형을 결정합니다.
    # 두 유형의 점수가 같을 때는 사전 순으로 빠른 앞의 글자가 선택되도록 '>=' 연산자를 사용합니다.
    answer += 'R' if scores['R'] >= scores['T'] else 'T'  # 1번 지표
    answer += 'C' if scores['C'] >= scores['F'] else 'F'  # 2번 지표
    answer += 'J' if scores['J'] >= scores['M'] else 'M'  # 3번 지표
    answer += 'A' if scores['A'] >= scores['N'] else 'N'  # 4번 지표
    
    return answer


# ==========================================
# 🧪 [성격 유형 검사하기] 테스트 및 검증 코드
# ==========================================
if __name__ == "__main__":
    print("=== [성격 유형 검사하기] 테스트 시작 ===")
    
    # 테스트 케이스 1 (입출력 예 #1)
    survey1 = ["AN", "CF", "MJ", "RT", "NA"]
    choices1 = [5, 3, 2, 7, 5]
    expected1 = "TCMA"
    result1 = solution(survey1, choices1)
    print(f"\n[테스트 1]")
    print(f"실행결과 〉 \"{result1}\"")
    print(f"통과여부 〉 {'성공  (수정됨)' if result1 == expected1 else '실패 ❌'}")
    
    # 테스트 케이스 2 (입출력 예 #2 - 모두 0점일 때 사전순 정렬 확인)
    survey2 = ["TR", "RT", "TR"]
    choices2 = [7, 1, 3]
    expected2 = "RCJA"
    result2 = solution(survey2, choices2)
    print(f"\n[테스트 2]")
    print(f"실행결과 〉 \"{result2}\"")
    print(f"통과여부 〉 {'성공  (수정됨)' if result2 == expected2 else '실패 ❌'}")

    print("\n==========================================")