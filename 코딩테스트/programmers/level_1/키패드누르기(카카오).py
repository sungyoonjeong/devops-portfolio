"""
왼손 엄지는 *, 오른손 엄지는 # 위치에서 시작
<규칙>
1) 엄지는 상하좌우 4가지 방향으로만 이동 가능하며 키패드 한칸은 거리로 1에 해당
2) 왼쪽 열의 3개의 숫자 1,4,7을 입력할때는 왼손 엄지 사용
3) 오른쪽 열의 3,6,9를 입력할때는 오른손 엄지 사용
4) 가운데 열의 2,5,8,0을 입력할 때는 두 엄지손가락의 현재 키패드의 위치에서 더 가까운 엄지를 사용

numbers : 순서대로 누를 번호가 담긴 배열
hand : 왼손잡이인지 오른손잡이인지 나타내는 문자열
return : 각 번호를 누른 엄지가 왼손인지 오른손인지 나타내는 문자열 

<알고리즘>
1) 키패드 위치를 좌표로 전환
    - 1(0,0), 5(1,1) 0(3,1) 등으로
    - 이를 딕셔너리 형태로 미리 정의해둠
2) 시작 위치 설정
    - 왼손 엄지는 *자리(3,0), 오른쪽 엄지는 #자리(3,2)에서 출발
3) 숫자별 이동 규칙 적용
    - 1,4,7 : 왼손
    - 3,6,9 : 오른손
    - 2,5,8,0 : 거리 계산
        - |x1-x2| + |y1-y2|
        - 거리가 가까운 손을 움직임
        - 거리가 같다면 hand에 따라 움직임
"""
def solution(numbers, hand):
    answer = ''
    # 키패드의 숫자들을 (행, 열) 형태의 2차원 좌표로 매핑합니다.
    keypad = {
        1: (0, 0), 2: (0, 1), 3: (0, 2),
        4: (1, 0), 5: (1, 1), 6: (1, 2),
        7: (2, 0), 8: (2, 1), 9: (2, 2),
        '*': (3, 0), 0: (3, 1), '#': (3, 2)
    }
    
    # 왼손 엄지와 오른손 엄지의 초기 위치(*, #)를 설정합니다.
    left_pos = keypad['*']
    right_pos = keypad['#']
    
    # 입력받은 번호들을 순서대로 확인합니다.
    for num in numbers:
        if num in [1, 4, 7]: # 1, 4, 7은 왼손을 사용합니다.
            answer += 'L'
            left_pos = keypad[num] # 왼손 위치를 해당 숫자의 좌표로 갱신합니다.
        elif num in [3, 6, 9]: # 3, 6, 9는 오른손을 사용합니다.
            answer += 'R'
            right_pos = keypad[num] # 오른손 위치를 해당 숫자의 좌표로 갱신합니다.
        else: # 2, 5, 8, 0인 경우 거리를 비교합니다.
            target_pos = keypad[num] # 목표 숫자의 좌표를 가져옵니다.
            # 왼손과 목표 위치 사이의 맨해튼 거리를 계산합니다.
            left_dist = abs(left_pos[0] - target_pos[0]) + abs(left_pos[1] - target_pos[1])
            # 오른손과 목표 위치 사이의 맨해튼 거리를 계산합니다.
            # abs(): 절대값 함수, 거리는 항상 양수이므로
            right_dist = abs(right_pos[0] - target_pos[0]) + abs(right_pos[1] - target_pos[1])
            
            if left_dist < right_dist: # 왼손이 더 가까우면 왼손 이동
                answer += 'L'
                left_pos = target_pos
            elif right_dist < left_dist: # 오른손이 더 가까우면 오른손 이동
                answer += 'R'
                right_pos = target_pos
            else: # 거리가 같은 경우 주손(hand)에 따라 결정합니다.
                if hand == 'left':
                    answer += 'L'
                    left_pos = target_pos
                else:
                    answer += 'R'
                    right_pos = target_pos
                    
    return answer # 최종 누른 손의 순서 기록을 반환합니다.



def test_solution():
    print("카카오 인턴십 [키패드 누르기] 예제 검증 시작...\n")
    
    # 테스트 케이스 1
    nums1 = [1, 3, 4, 5, 8, 2, 1, 4, 5, 9, 5]
    hand1 = "right"
    expected1 = "LRLLLRLLRRL"
    res1 = solution(nums1, hand1)
    print(f"테스트 1 결과: {'통과(PASS)' if res1 == expected1 else '실패(FAIL)'} (실제: {res1})")
    
    # 테스트 케이스 2
    nums2 = [7, 0, 8, 2, 8, 3, 1, 5, 7, 6, 2]
    hand2 = "left"
    expected2 = "LRLLRRLLLRR"
    res2 = solution(nums2, hand2)
    print(f"테스트 2 결과: {'통과(PASS)' if res2 == expected2 else '실패(FAIL)'} (실제: {res2})")
    
    # 테스트 케이스 3
    nums3 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
    hand3 = "right"
    expected3 = "LLRLLRLLRL"
    res3 = solution(nums3, hand3)
    print(f"테스트 3 결과: {'통과(PASS)' if res3 == expected3 else '실패(FAIL)'} (실제: {res3})")

# 테스트 실행
test_solution()