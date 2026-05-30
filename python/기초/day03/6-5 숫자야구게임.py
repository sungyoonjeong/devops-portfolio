"""
숫자 야구는 상대방이 정한 서로 다른 3자리 숫자를 맞히는 게임이다.
숫자를 추측하면 스트라이크와 볼로 힌트를 알려주고, 이 힌트를 바탕으로 정답을 찾아가는 것이 이 게임의 핵심
3자리 숫자 중 0은 제외한다.

게임의 규칙은 다음과 같다.

판정	            조건
스트라이크	         숫자와 위치가 모두 맞음
볼	               숫자는 맞지만 위치가 다름

- 기능 : 서로 다른 3자리 난수 생성, 스트라이크/볼 판정, 반복입력
- 입력값 : 사용자가 추측한 3자리 숫자
- 출력값 : 스트라이크, 볼 개수(정답이면 축하 메시지와 시도 횟수)
"""
#1) 서로다른 3자리 난수 생성
'''
import random

nums=random.sample(range(1,10),3)
print(nums)
'''
#2) 사용자에게 숫자를 입력받도록 코드 추가
'''
import random
nums=random.sample(range(1,10),3)

question=input("3자리 숫자를 입력하세요: ")
print(question)
'''

#3) 입력받은 문자열을 숫자 리스트로 변환해야 컴퓨터의 숫자와 비교할수 있음
'''
import random

nums=random.sample(range(1,10),3)

question=input("3자리 숫자를 입력하세요: ")
guess=list(map(int,question))
print(guess)
'''

#4) 스트라이크, 볼 판정하는 코드 
'''
import random

nums=random.sample(range(1,10),3)

question=input("3자리 숫자를 입력하세요: ")
guess=list(map(int,question))

strike=0
ball=0

for i in range(3):
    if guess[i] == nums[i]:
        strike += 1
    elif guess[i] in nums:
        ball+=1

print(f"{strike}스트라이크 {ball}볼")
'''
#5) 정답을 맞출때까지 반복
import random

nums=random.sample(range(1,10),3)
count=0

while True:
    question=input("3자리 숫자를 입력하세요: ")
    guess=list(map(int,question))
    count+=1

    strike=0
    ball=0

    for i in range(3):
        if guess[i]==nums[i]:
            strike+=1
        elif guess[i] in nums:
            ball+=1
    
    if strike == 3:
        print(f"정답! {count}번 만에 맞혔습니다.")
        break

    print(f"{strike}스트라이크 {ball}볼")
#count 변수로 시도 횟수를 세고, 3스트라이크가 되면 메시지와 함께 시도 횟수를 출력
#break로 반복을 종료
#3스트라이크가 아니면 스트라이크와 볼 개수를 알려주고 다시 입력 받는다.

