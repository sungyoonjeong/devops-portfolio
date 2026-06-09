"""
배열 array의 i번째~j번째 숫자까지 자르고 정렬
k번째 있는 수를 구하여라

ex) array=[1,5,2,6,3,7,4], i=2, j=5, k=3 이라면
    - array 의 2번째부터 5번째까지 자르면 [5,2,6,3]
    - 정렬하면 [2,3,5,6]
    - k=3번째 숫자는 5
    
commands : [i,j,k]를 원소로 가진 2차원 배열
return : commands의 모든 원소에 대한 결과를 담은 배열

<알고리즘>
1) commands의 각 원소를 빼서 i,j,k값을 빼낸다.
2) array의 [i-1:j]을 새로운 리스트로 저장 후 sorted(array)
3) 그 리스트의 k-1 인덱스의 숫자를 return에 append
"""
def solution(array, commands):
    answer = [] # 결과를 순서대로 담아서 반환할 빈 리스트 선언
    
    # 1) commands 리스트에서 하나의 명령(예: [2, 5, 3])을 하나씩 꺼내어 command 변수에 담음
    for command in commands:
        
        # 2) 꺼내온 command 리스트의 0번, 1번, 2번 인덱스에서 각각 i, j, k 값을 추출
        i = command[0] # 시작 위치 (예: 2)
        j = command[1] # 끝 위치 (예: 5)
        k = command[2] # 찾을 원소의 순서 (예: 3)
        
        # 3) array 배열을 i번째부터 j번째까지 자름 
        # 파이썬 슬라이싱 [시작:끝]은 '시작'은 포함하고 '끝'은 포함하지 않음
        # 또한 사람은 1번째부터 세지만 컴퓨터는 0번째부터 세므로, 시작 인덱스는 i-1을 해줌
        new_array = array[i-1:j]
        
        # 4) 잘라낸 새로운 배열(new_array)을 sorted() 함수를 사용해 오름차순으로 정렬
        sorted_array = sorted(new_array)
        
        # 5) 정렬된 배열에서 k번째에 있는 숫자를 꺼내 answer 리스트에 추가
        # 이 역시 컴퓨터 인덱스 규칙에 맞추기 위해 k-1 번 인터페이스의 값을 가져옴
        answer.append(sorted_array[k-1])
        
    return answer # 모든 명령을 처리한 후 최종 정답 리스트 반환


# ========================================================
# 🔍 실행 확인용 실시간 테스트 코드 (바로 실행 가능)
# ========================================================

print("=== [K번째수] 알고리즘 테스트 시작 ===")

# 프로그래머스 기본 예제 케이스 테스트
test_array = [1, 5, 2, 6, 3, 7, 4]
test_commands = [[2, 5, 3], [4, 4, 1], [1, 7, 3]]

# 함수 실행
result = solution(test_array, test_commands)
expected = [5, 6, 3]

# 결과 검증 출력
print(f"실행 결과: {result}")
print(f"예상 정답: {expected}")
print(f"테스트 판정: {'✅ 통과' if result == expected else '❌ 실패'}")

print("=== 테스트 종료 ===")