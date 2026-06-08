"""
numbers : 정수 배열
numbers에서 서로 다른 인덱스에 있는 두 개의 수를 뽑아 더해서 만들 수 있는 모든수를 배열에 오름차순으로 담아 return

<알고리즘>
1) 모든 조합 찾기 : 배열에서 서로 다른 인덱스에 있는 두 수를 뽑아야 하므로, 이중 반복문을 사용해 가능한 모든 두 수의 합을 구함
2) 중복제거 : 같은 합이 여러번 나올 수 있으므로 중복을 허용하지 않는 자료구조인 set에 합을 집어넣음
3) 정렬 및 반환 : 세트를 다시 리스트로 변환한 뒤 정렬하여 반환
"""

def solution(numbers):
    answer = set() # 중복된 합을 자동으로 제거하기 위해 빈 세트(set)를 생성합니다.
    
    # 서로 다른 인덱스의 두 수를 뽑기 위한 이중 반복문을 시작합니다.
    for i in range(len(numbers)): # 첫 번째 수를 가리키는 인덱스 i
        for j in range(i + 1, len(numbers)): # i 이후의 인덱스 j를 선택하여 자기 자신과의 더하기 및 중복 조합을 방지합니다.
            answer.add(numbers[i] + numbers[j]) # 두 수의 합을 세트에 추가합니다. (중복은 자동으로 제거됨)
            
    return sorted(list(answer)) # 세트를 리스트로 변환한 뒤, 오름차순으로 정렬하여 반환합니다.


# 테스트를 위한 함수
def test_solution():
    print("코딩테스트 예제 검증 시작...\n")
    
    # 입출력 예 #1
    ex1_input = [2, 1, 3, 4, 1]
    ex1_expected = [2, 3, 4, 5, 6, 7]
    ex1_result = solution(ex1_input)
    print(f"테스트 1 입력: {ex1_input}")
    print(f"기대 결과: {ex1_expected} | 실제 결과: {ex1_result}")
    print(f"결과: {'통과(PASS)' if ex1_result == ex1_expected else '실패(FAIL)'}\n")
    
    # 입출력 예 #2
    ex2_input = [5, 0, 2, 7]
    ex2_expected = [2, 5, 7, 9, 12]
    ex2_result = solution(ex2_input)
    print(f"테스트 2 입력: {ex2_input}")
    print(f"기대 결과: {ex2_expected} | 실제 결과: {ex2_result}")
    print(f"결과: {'통과(PASS)' if ex2_result == ex2_expected else '실패(FAIL)'}\n")

# 테스트 실행
test_solution()