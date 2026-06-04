"""
원래 이용료 : price
N번째 이용 시 원래 이용료의 N배
count : 놀이기구 이용횟수
return : 현재 자신이 가지고 있는 금액에서 얼마가 모자라는지 
금액이 부족하지 않으면 0을 return

<알고리즘>
*방법 A
1) 총 필요한 금액 저장할 변수 total_price 0 으로 초기화
2) 1부터 count 까지 반복하면서 price*i를 total_price에 누적
3) money가 총 금액보다 크거나 같다면 0 반환
4) 작다면 total_price-money 반환

*방법 B
1) 1~count까지의 합은 count*(count+1)//2
2) price * count합
3) max(0, 전체 이용금액-money)
"""
def solution(price, money, count):
    total_price = 0
    
    # 1부터 count까지 순회하며 N번째 이용료(price * i)를 누적 계산
    for i in range(1, count + 1):
        total_price += price * i
        
    # 가진 돈(money)이 총 이용료보다 많다면 부족한 금액은 0
    if money >= total_price:
        return 0
    # 돈이 부족하다면 부족한 만큼의 액수를 반환
    else:
        return total_price - money

# 한줄풀이
# def solution(price, money, count):
#     # 등차수열 합 공식으로 총 금액을 구한 뒤, 가진 돈을 뺀 값과 0 중 큰 값을 반환
#     return max(0, price * (count * (count + 1) // 2) - money)

# 테스트 실행 함수
def test_solution():
    print("=== 부족한 금액 계산하기 테스트 시작 ===")
    
    # 테스트 케이스 1 (입출력 예 #1: 가진 돈 20원, 총 금액 30원 -> 10원 부족)
    assert solution(3, 20, 4) == 10, f"실패: TC1 결과 {solution(3, 20, 4)}"
    print("테스트 1 통과! (기댓값: 10)")
    
    # 테스트 케이스 2 (돈이 딱 맞게 떨어지는 경우 -> 0 반환)
    # 총 금액: 3 * (1+2) = 9원, 가진 돈 9원
    assert solution(3, 9, 2) == 0, f"실패: TC2 결과 {solution(3, 9, 2)}"
    print("테스트 2 통과! (기댓값: 0)")
    
    # 테스트 케이스 3 (돈이 여유 있게 남는 경우 -> 0 반환)
    # 총 금액: 5 * 1 = 5원, 가진 돈 100원
    assert solution(5, 100, 1) == 0, f"실패: TC3 결과 {solution(5, 100, 1)}"
    print("테스트 3 통과! (기댓값: 0)")
    
    print("=== 모든 테스트를 성공적으로 통과했습니다! ===")

# 테스트 실행
test_solution()