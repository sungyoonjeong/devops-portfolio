"""
[문제 요약]
- 입력받은 자연수 n (2 <= n <= 1,000,000) 이하의 모든 소수의 개수를 반환하는 함수를 작성합니다.
- 소수는 1과 자기 자신으로만 나누어떨어지는 1보다 큰 양의 정수입니다.

[알고리즘 순서]
1. 0부터 n까지의 인덱스를 가진 부울(Boolean) 리스트를 생성하여 모두 True(소수)로 초기화합니다. (0과 1은 False로 설정)
2. 2부터 n의 제곱근까지 반복하며, 현재 수가 소수(True)라면 그 수의 모든 배수를 소수가 아닌 것(False)으로 제외합니다.
3. 리스트에서 True로 남아있는 개수를 세어 반환합니다.
"""

def solution(n):
    # 0부터 n까지 소수 여부를 나타내는 리스트 생성 (초기값은 모두 True)
    is_prime = [True] * (n + 1)
    # 0과 1은 소수가 아니므로 False 처리
    is_prime[0] = is_prime[1] = False
    
    # 2부터 n의 제곱근까지만 확인 (에라토스테네스의 체 원리)
    for i in range(2, int(n ** 0.5) + 1):
        # i가 소수인 경우, i의 배수들을 모두 소수에서 제외
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
                
    # True(소수)로 남아있는 개수를 합산하여 반환
    return sum(is_prime)

# --- 테스트 코드 ---
if __name__ == "__main__":
    print("테스트 케이스 1 (n=10, 기대값=4):", solution(10))
    print("테스트 케이스 2 (n=5, 기대값=3):", solution(5))