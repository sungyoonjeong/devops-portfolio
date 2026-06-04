"""
numbers : 0~9까지의 숫자 중 일부가 들어있는 정수배열
numbers에서 찾을 수 없는 0부터9까지의 숫자를 모두 찾아 더한 수를 return

<알고리즘>
1) 0~9까지의 합 = 45
2) numbers의 모든 원소의 합
3) 45 - 합
"""
def solution(numbers):
    # 0부터 9까지의 총합은 45이므로, 여기서 numbers의 합을 빼면 없는 숫자의 합이 됩니다.
    answer = 45 - sum(numbers)
    
    return answer

# 테스트 실행 함수
def test_solution():
    print("=== 없는 숫자 더하기 테스트 시작 ===")
    
    # 테스트 케이스 1 (입출력 예 #1: 5, 9가 없음)
    tc1 = [1, 2, 3, 4, 6, 7, 8, 0]
    assert solution(tc1) == 14, f"실패: TC1 결과 {solution(tc1)}"
    print("테스트 1 통과! (기댓값: 14)")
    
    # 테스트 케이스 2 (입출력 예 #2: 1, 2, 3이 없음)
    tc2 = [5, 8, 4, 0, 6, 7, 9]
    assert solution(tc2) == 6, f"실패: TC2 결과 {solution(tc2)}"
    print("테스트 2 통과! (기댓값: 6)")
    
    # 테스트 케이스 3 (추가 케이스: 모든 숫자가 다 있는 경우)
    tc3 = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert solution(tc3) == 0, f"실패: TC3 결과 {solution(tc3)}"
    print("테스트 3 통과! (기댓값: 0)")
    
    print("=== 모든 테스트를 성공적으로 통과했습니다! ===")

# 테스트 실행
test_solution()