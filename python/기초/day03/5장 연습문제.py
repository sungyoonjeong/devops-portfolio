# Q1. Calculator 클래스를 상속하는 UpgradeCalculator를 만들고 값을 뺄 수 있는 minus 메서드를 추가해보자.
# 즉, 다음과 같이 동작하는 클래스를 만들어야한다.

class Calculator:
    def __init__(self):
        self.value=0

    def add(self,val):
        self.value+=val


class UpgradeCalculator(Calculator):
    def minus(self,val):
        self.value-=val
        return self.value

cal = UpgradeCalculator()
cal.add(10)
print(cal.value)
print(cal.minus(7))

# Q2. 객체변수 value가 100 이상의 값은 가질수 없도록 제한하는 MaxLimitCalculator 클래스를 만들어보자.
# 즉 다음과 같이 동작해야한다.
# 단 반드시 다음과 같은 Calculator 클래스를 상속해서 만들어야한다.

print(cal.value) #100 출력

class Calculator:
    def __init__(self):
        self.value=0
    def add(self,val):
        self.value += val

class MaxLimitCalcultor(Calculator):
    def add(self,val):
        self.value+=val
        if self.value>=100:
            self.value=100
            return self.value
        else:
            return self.value

cal=MaxLimitCalcultor()
print(cal.add(60)) #50더하기

print(cal.add(60)) #60더하기

# Q3. 다음 결과를 예측해보자
"""
1. 
>>> all([1, 2, abs(-3)-3]) : False

2.
>>> chr(ord('a')) == 'a' : True
"""
print(chr(ord("a")))

# Q4. filter와 lamda를 사용하여 리스트 [1,-2,3,-5,8,-3]에서 음수를 모두 제거해보자

print(list(filter(lambda x:x>0,[1,-2,3,-5,8,-2])))

# Q5. 234라는 10진수의 16진수는 다음과 같이 구할수 있다.
print(hex(234))

print(int("0xea",16)) #16진수를 10진수로 변경

# Q6. map과 lambda를 사용하여 [1,2,3,4] 리스트의 각 요소값에 3이 곱해진 리스트 [3,6,9,12]를 만들어 보자.
a=list(map(lambda a:a*3,[1,2,3,4]))
print(a)

# Q7. 다음 리스트의 최대값과 최소값의 합을 구해라
# [-8, 2, 7, 5, -3, 5, 0, 1]

a=[-8, 2, 7, 5, -3, 5, 0, 1]
result=max(a)+min(a)
print(result)

# Q8. 17/3의 결과는 다음과 같다. 
# 17/3 = 5.666666666666667
# 소수점 4자리까지만 반올림하여 표시해보자

print(round(17/3,4))

# Q9. 다음과 같이 실행할 때 입력값을 모두더하여 출력하는 스크립트 myargv.py를 작성하라
"""
C:\> cd doit
C:\doit> python myargv.py 1 2 3 4 5 6 7 8 9 10
55
"""

'''
1. import sys
파이썬 인터프리터가 제공하는 변수와 함수를 직접 제어할 수 있게 해주는 sys모듈을 불러옴
터미널에서 입력한 모든값들을 파이썬 코드 안으로 가져오려면 sys모듈의 argv라는 기능이 필요하기 때문

2. numbers=sys.argv[1:]
sys.argv란 : 명령창에 입력한 문자열들이 순서대로 담기는 리스트
ex)python myargv.py 1 2 3이라 입력하면
sys.argv[0] = 'myargv.py'(실행한 파일의 이름)
sys.argv[1] = '1'
sys.argv[2] = '2'
sys.argv[3] = '3'

3. result = 0
더한 결과값을 누적해서 저장할 변수 result를 0으로 초기화

4. for number in numbers:
numbers리스트에 들어있는 요소를 하나씩 꺼내어 number 변수에 대입하며 반복문 돌림

5. result += int(number)
int(number)의 역할 : 정수형으로 변환해줌
변환한 정수값을 result값에 계속 더해서 누적

6. print(result)
최종 결과를 출력
'''

# map을 이용한 더 간결한 코드
import sys

sys.argv=["test.py","1","2","3","4","5"]
result = sum(map(int,sys.argv[1:]))
print(result)

# Q10.os모듈을 사용하여 다음과 같이 동작하도록 코드를 작성
# 1. C:\doit 디렉터리로 이동
# 2. dir 명령을 실행하고 그 결과를 변수에 담는다.
# 3. dir 명령의 결과를 출력한다.

import os
#파일 매니저나 터미널에서 하던 작업을 코드로 할 수 있게 해줌

#1. C:\doit 디렉터리로 이동한다.
#os.chdir("C:\doit")
#chdir:change directory, cd 명령어와 똑같음

#2. dir 명령을 실행하고 그 결과를 변수에 담는다.
#result = os.popen("dir").read()
# os.popen("명령어"):시스템 내부의 cmd를 열고 "dir"명령을실행
# popen: Pipe Open의 줄임말
# .read(): 명령어가 실행되면서 터미널 화면에 뿌려진 텍스트 결과물을 파이썬이 읽어와서 문자열(String)데이터로 변환
# 최종적으로 result변수에 저장

#3. dir 명령의 결과를 출력한다.
#print(result)

# Q11. glob 모듈을 사용하여 C:\doit 디렉터리의 파일 중 확장자가 .py인 파일만 출력하는 프로그램을 작성
'''
import glob
glob.glob("C:\doit\*.py")
'''

"""
1. import glob
파일 시스템에서 파일을 찾을때 사용하는 glob 내장 모듈을 불러옴
여러 파일 이름의 패턴을 매칭하는것을 "글로빙(globbing)"이라함

2. glob.glob("C:\doit\*.py")
glob 모듈 안의 glob() 함수를 실행합니다.
괄호 안의 경로 조건에 맞는 모든 파일들의 전체 경로를 리스트 형태로 반환
*:모든 글자

실제 화면에 결과를 깔끔하게 한줄씩 출력하는 방법
import glob

#조건에 맞는 파일 리스트를 가져와서 반복문 실행
for file in glob.glob("C:/doit/*.py"):
    print(file)  #파일 경로를 하나씩 출력
"""

# Q12. time 모듈을 사용하여 현재 날짜와 시간을 다음과 같은 형식으로 출력해보자
# 2018/04/03 17:20:32

import time
time.strftime("%Y/%m/%d %H:%M:%S")

print(time.strftime("%Y/%m/%d %H:%M:%S"))

"""
1. time.sleep(초)
   프로그램 일시 정지 (★가장 많이 씀)기능
   입력한 '초'만큼 프로그램 실행을 완전히 멈추게 합니다. 
   소수점(0.5초 등)도 가능합니다.
   활용: 웹 크롤링 시 서버 과부하를 막기 위해 간격을 둘 때, 또는 매크로 프로그램을 만들 때 필수적입니다.

2. time.time() : Epoch 시간(타임스탬프) 구하기
    1970년 1월 1일 0시 0분 0초를 기준으로 현재까지 흐른 시간을 초(second) 단위의 실수로 반환합니다.
    주로 알고리즘이나 코드의 실행 속도(성능)를 측정할 때 사용합니다.

3. time.strftime("포맷", 구조화된_시간) : 원하는 형식으로 출력
    시간 데이터를 우리가 읽을 수 있는 문자열 형식으로 변환합니다. 두 번째 인자를 생략하면 현재 시간을 기준으로 변환합니다.
    활용: 로그(Log) 파일 기록, 날짜 기반 파일명 생성 등.

4. time.localtime() : 시간 데이터를 튜플 형태로 분해
    time.time()이 주는 복잡한 실수를 변환하여, 연/월/일/시/분/초를 각각 꺼내 쓰기 좋게 분해해 줍니다.
    활용: 현재 시각의 '분'이나 '요일'만 따로 떼어내서 조건문(if)을 걸 때 유용합니다.

"""

# Q13. random모듈을 사용하여 로또 번호 (1~45 사이의 숫자 6개)를 생성해보자(단 중복된 숫자가 있으면 안됨)
import random

result=[]
while len(result)<6:
    num=random.randint(1,45) #1부터 45까지의 난수 생성
    if num not in result:
        result.append(num)
print(result)

