"""
각 기사에게 1~number까지 번호가 지정되어있음(약수 인덱스에따라서)

각 기사는 자신의 번호의 약수 개수에 해당하는 공격력을 가진 무기 구매
단, 공격력의 제한수치 정하고, 
제한 수치보다 큰 공격력을 가진 무기를 구매해야하는 기사는 협약기간에서 정한 공격력을 가지는 무기를 구매해야함.

ex) 15번 기사 =>1,3,5,15 (약수 4개)
따라서, 공격력 4인 무기 구매해야함. 
if 공격력 제한 수치가 3이고, 제한수치를 초과한 기사가 사용할 무기의 공격력이 2라면,
15번 기사는 공격력 2인 무기를 구매해야함.

무기를 만들때, 무기의 공격력 1당 1kg의 철이 필요
무기점에서 무기를 모두 만들기 위해 필요한 철의 무게를 미리 계산해야함

number: 기사단원의 수
limit: 공격력 제한 수치를 나타내는 정수
power: 제한 수치를 초과한 기사가 사용할 무기의 공격력을 나타내는 정수
return: 무기점의 주인이 무기를 모두 만들기 위해 필요한 철의 무게
"""
"""
Step1) number의 약수 리스트로 저장 => 기사들의 번호
       ex) number가 5면 1부터 5까지 순회하면서 각각의 약수의 개수를 리스트로 저장
Step2) for문으로 기사들의 번호 순회 => limit과 비교
Step3) limit 보다 적으면 인덱스의 값을 append.
Step4) limit 보다 크면 power값을 append.
"""
def solution(number, limit, power):
    answer = 0
    
    # 1번 기사부터 number번 기사까지 순회
    for num in range(1, number + 1):
        # 1. 현재 기사 번호의 약수 개수를 구함
        factors_count = 0
        for i in range(1, int(num**0.5) + 1):
            if num % i == 0:
                if i * i == num:
                    factors_count += 1
                else:
                    factors_count += 2
                    
        # 2. 구한 약수 개수(공격력)가 제한수치(limit)를 넘는지 확인
        if factors_count > limit:
            answer += power  # 초과하면 협약된 power만큼 철 무게 추가
        else:
            answer += factors_count  # 안 넘으면 원래 약수 개수만큼 철 무게 추가
            
    return answer

# --- 테스트 실행 ---
print("테스트 1:", solution(5, 3, 2))   # 출력: 10
print("테스트 2:", solution(10, 3, 2))  # 출력: 21