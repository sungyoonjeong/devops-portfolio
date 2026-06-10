"""
주어진 숫자 3개의 수를 더했을 때 소수가 되는 경우의 수 구하기

nums: 숫자들이 들어있는 배열
return : nums에 있는 숫자들 중 서로 다른 3개를 골라 더했을때 소수가 되는 경우의 수 개수

[알고리즘 개념: 브루트 포스 (Brute Force) & 조합 (Combination)]
    - nums의 배열 크기가 최대 50개로 매우 작기 때문에, 3개를 고르는 모든 경우의 수를 직접 확인하는 완전 탐색이 가능합니다.
    - Python의 `itertools.combinations`를 사용하면 중복 없이 3개의 숫자를 뽑는 조합을 쉽게 구할 수 있습니다.

    [알고리즘 순서]
    1. `combinations(nums, 3)`을 사용하여 배열에서 서로 다른 3개의 숫자를 뽑는 모든 조합을 구합니다.
    2. 각 조합의 합(sum)을 계산합니다.
    3. 계산된 합이 소수인지 `is_prime()` 함수를 통해 판별합니다.
    4. 소수라면 카운트(answer)를 1씩 증가시킵니다.
    5. 최종 카운트 값을 반환합니다.
"""

from itertools import combinations

def is_prime(num):
    """
    [소수 판별 함수]
    - 입력받은 수(num)가 소수인지 확인합니다.
    - 2부터 num의 제곱근까지만 나누어 떨어지는지 확인하면 효율적으로 판별할 수 있습니다.
    """
    if num < 2:
        return False
    # 2부터 루트 num까지의 숫자로 나누어 떨어지는지 확인
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False  # 나누어 떨어지면 소수가 아님
    return True  # 어떤 수로도 나누어 떨어지지 않으면 소수

def solution(nums):
    answer = -1

    # [실행] 버튼을 누르면 출력 값을 볼 수 있습니다.
    print('Hello Python')
    
    # 1. 카운트를 시작하기 위해 0으로 재설정
    answer = 0
    
    # 2. 3개의 숫자를 고르는 조합 순회
    for comb in combinations(nums, 3):
        # 3. 조합의 합 구하기
        total_sum = sum(comb)
        
        # 4. 합이 소수인지 확인
        if is_prime(total_sum):
            # 5. 소수라면 경우의 수 누적
            answer += 1

    # 최종 결과 반환
    return answer

# ==========================================
# [테스트 코드]
# ==========================================
if __name__ == "__main__":
    print("\n--- 로컬 테스트 케이스 실행 ---")
    
    # 예제 1
    nums1 = [1, 2, 3, 4]
    result1 = solution(nums1)
    print(f"테스트 1 결과: {result1} (기댓값: 1) -> {'정답' if result1 == 1 else '오답'}\n")
    
    # 예제 2
    nums2 = [1, 2, 7, 6, 4]
    result2 = solution(nums2)
    print(f"테스트 2 결과: {result2} (기댓값: 4) -> {'정답' if result2 == 4 else '오답'}\n")