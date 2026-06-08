"""
학생들의 번호 : 체격 순
바로 앞번호의 학생이나 바로 뒷번호의 학생에게만 체육복 빌려줄 수 있음.

n : 전체 학생수
lost : 체육복을 도난당한 학생들의 번호가 담긴 배열
reserve : 여벌의 체육복을 가져온 학생들의 번호가 담긴 배열
return : 체육 수업을 들을 수 있는 학생의 최댓값

<알고리즘>
1) 중복 유저 제거 : 여벌이 있지만 도난당한 학생은 여벌도 없고 도난도 안 당한 일반학생과 같음
    - 빌려줄 수 있는 사람 목록(reserve)과 빌려야하는 사람목록(lost)에서 이들을 제외
    - set의 차집합 연산을 사용하면 처리 가능
2) 정렬 : 앞번호부터 순서대로 확인하며 빌려주는 것이 greedy 관점에서 유리.
    - 남은 lost와 reserve리스트를 정렬
3) 체육복 빌려주기 : lost 유저를 하나씩 확인 후, 해당 유저의 앞번호(student-1)가 reserve에 있다면 빌림. 없다면 뒷번호(student+1)가 reserve에 있는지 확인하고 빌림
빌려준 번호는 reserve에서 지움
4) 수업들을수있는 학생 계산 : 전체 학생 수 (n) - 끝까지 빌리지 못한 학생 수(lost에 남은 인원) 반환
"""
def solution(n, lost, reserve):
    answer = 0
    
    # 여벌이 있으면서 도난당한 학생을 두 리스트에서 완전히 제외하여 진짜 여벌이 있는 사람과 진짜 잃어버린 사람을 거릅니다.
    actual_reserve = sorted(list(set(reserve) - set(lost)))
    actual_lost = sorted(list(set(lost) - set(reserve)))
    
    # 체육복을 잃어버린 학생들을 앞번호부터 차례대로 확인합니다.
    for student in actual_lost:
        # 내 바로 앞번호(student - 1) 학생이 여벌 체육복을 가지고 있는지 확인합니다.
        if student - 1 in actual_reserve:
            actual_reserve.remove(student - 1) # 빌렸으므로 여벌 리스트에서 앞번호 학생을 제외합니다.
        # 앞번호는 없지만 내 바로 뒷번호(student + 1) 학생이 여벌 체육복을 가지고 있는지 확인합니다.
        elif student + 1 in actual_reserve:
            actual_reserve.remove(student + 1) # 빌렸으므로 여벌 리스트에서 뒷번호 학생을 제외합니다.
        # 둘 다 없다면 체육복을 빌리지 못하고 다음 학생으로 넘어갑니다.
        else:
            n -= 1 # 빌리지 못한 학생은 수업을 들을 수 없으므로 전체 수업 가능 인원(n)에서 1명을 뺍니다.
            
    answer = n # 체육수업을 들을 수 있는 최종 학생 수를 반환합니다.

    return answer


def test_solution():
    print("탐욕법(Greedy) [체육복] 예제 검증 시작...\n")
    
    # 입출력 예 #1
    n1, lost1, reserve1 = 5, [2, 4], [1, 3, 5]
    expected1 = 5
    res1 = solution(n1, lost1, reserve1)
    print(f"테스트 1 결과: {'통과(PASS)' if res1 == expected1 else '실패(FAIL)'} (실제: {res1})")
    
    # 입출력 예 #2
    n2, lost2, reserve2 = 5, [2, 4], [3]
    expected2 = 4
    res2 = solution(n2, lost2, reserve2)
    print(f"테스트 2 결과: {'통과(PASS)' if res2 == expected2 else '실패(FAIL)'} (실제: {res2})")
    
    # 입출력 예 #3
    n3, lost3, reserve3 = 3, [3], [1]
    expected3 = 2
    res3 = solution(n3, lost3, reserve3)
    print(f"테스트 3 결과: {'통과(PASS)' if res3 == expected3 else '실패(FAIL)'} (실제: {res3})")

# 테스트 실행
test_solution()