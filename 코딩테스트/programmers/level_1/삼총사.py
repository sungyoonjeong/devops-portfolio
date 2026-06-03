"""
학생들의 정수 번호가 담긴 배열 number가 주어집니다.

이 중 서로 다른 위치에 있는 학생 3명을 선택합니다.

선택한 3명의 정수 번호를 더했을 때 0이 되는 방법의 수를 구하여 반환해야 합니다.

<알고리즘>
Step 1) 파이썬 내장 라이브러리 itertools의 combinations 모듈을 불러옵니다. (3명을 순서 없이 뽑는 '조합'을 쉽게 구하기 위함)

Step 2) 삼총사를 만들 수 있는 경우의 수를 세어줄 변수 answer를 0으로 초기화합니다.

Step 3) combinations(number, 3)을 사용하여 number 배열에서 3개의 숫자를 뽑는 모든 경우의 수를 하나씩 순회합니다.

Step 4) 뽑힌 3개 숫자의 합(sum)이 0인지 확인합니다.

Step 5) 합이 0이라면 조건에 만족하므로 answer를 1 증가시킵니다.

Step 6) 모든 조합의 검사가 끝나면 최종 누적된 answer를 반환합니다.
"""
# 파이썬 내장 라이브러리에서 조합(Combination)을 구해주는 함수를 가져옵니다.
from itertools import combinations

def solution(number):
    answer = 0  # 삼총사를 만들 수 있는 방법의 수를 저장할 변수입니다.
    
    # number 배열에서 서로 다른 3개의 원소를 뽑는 모든 조합을 구하여 순회합니다.
    # 예: [1, 2, 3, 4]가 있으면 (1,2,3), (1,2,4), (1,3,4), (2,3,4)를 차례대로 꺼냅니다.
    for comb in combinations(number, 3):
        # 뽑힌 3개 숫자(튜플 형태)의 총합이 0인지 확인합니다.
        if sum(comb) == 0:
            answer += 1  # 합이 0이라면 삼총사 조건을 만족하므로 1을 더합니다.
            
    # 삼총사를 만들 수 있는 총 경우의 수를 반환합니다.
    return answer


# ==========================================
# 🧪 [삼총사] 테스트 및 검증 코드
# ==========================================
if __name__ == "__main__":
    print("=== [삼총사] 테스트 시작 ===")
    
    # 테스트 케이스 1 (입출력 예 #1)
    number1 = [-2, 3, 0, 2, -5]
    expected1 = 2
    result1 = solution(number1)
    print(f"\n[테스트 1]")
    print(f"입력값 〉 number = {number1}")
    print(f"기댓값 〉 {expected1}")
    print(f"실행결과 〉 {result1}")
    print(f"통과여부 〉 {'성공  (수정됨)' if result1 == expected1 else '실패 ❌'}")
    
    # 테스트 케이스 2 (입출력 예 #2)
    number2 = [-3, -2, -1, 0, 1, 2, 3]
    expected2 = 5
    result2 = solution(number2)
    print(f"\n[테스트 2]")
    print(f"입력값 〉 number = {number2}")
    print(f"기댓값 〉 {expected2}")
    print(f"실행결과 〉 {result2}")
    print(f"통과여부 〉 {'성공  (수정됨)' if result2 == expected2 else '실패 ❌'}")

    # 테스트 케이스 3 (입출력 예 #3)
    number3 = [-1, 1, -1, 1]
    expected3 = 0
    result3 = solution(number3)
    print(f"\n[테스트 3]")
    print(f"입력값 〉 number = {number3}")
    print(f"기댓값 〉 {expected3}")
    print(f"실행결과 〉 {result3}")
    print(f"통과여부 〉 {'성공  (수정됨)' if result3 == expected3 else '실패 ❌'}")

    print("\n==========================================")