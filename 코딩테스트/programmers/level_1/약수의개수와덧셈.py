"""
두 정수 left, right 주어짐
left부터 right까지의 모든 수들 중에서, 약수의개수가 짝수인 수는 더하고, 홀수인수는 빼서
return 값에 출력

<알고리즘>
- 일반적인 수는 약수가 항상 쌍(12의 약수는 1*12,2*6,3*4)으로 존재하기 때문에 무조건 짝수
- 제곱수(1,4,9,16,25,...)는 중간에 자기 자신을 제곱하는 수가 있어 무조건 홀수
- 어떤수의 제곱근을 정수로 바꾼뒤 다시 제곱했을 때, 자기 자신이 되는가를 체크해야함
"""
def solution(left, right):
    answer = 0
    
    # left부터 right까지 모든 수를 차례대로 순회
    for i in range(left, right + 1):
        # i의 제곱근을 정수로 만든 후 다시 제곱했을 때 i와 같다면 '제곱수' (즉, 약수의 개수가 홀수)
        if int(i ** 0.5) ** 2 == i:
            answer -= i  # 약수의 개수가 홀수이므로 뺌
        else:
            answer += i  # 약수의 개수가 짝수이므로 더함
            
    return answer

# 한줄풀이
# def solution(left, right):
#     # 제곱수이면 -i, 아니면 i를 선택해 모두 더해줌
#     return sum(-i if int(i ** 0.5) ** 2 == i else i for i in range(left, right + 1))


# 테스트 실행 함수
def test_solution():
    print("=== 약수의 개수와 덧셈 테스트 시작 ===")
    
    # 테스트 케이스 1 (13부터 17까지 -> 16만 홀수라 차감)
    assert solution(13, 17) == 43, f"실패: TC1 결과 {solution(13, 17)}"
    print("테스트 1 통과! (기댓값: 43)")
    
    # 테스트 케이스 2 (24부터 27까지 -> 25만 홀수라 차감)
    assert solution(24, 27) == 52, f"실패: TC2 결과 {solution(24, 27)}"
    print("테스트 2 통과! (기댓값: 52)")
    
    print("=== 모든 테스트를 성공적으로 통과했습니다! ===")

# 테스트 실행
test_solution()