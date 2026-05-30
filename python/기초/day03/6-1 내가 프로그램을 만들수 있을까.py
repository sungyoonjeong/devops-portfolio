# 프로그램을 만들려면 가장 먼저 "입력"과 "출력"을 생각하라.
"""
구구단 프로그램
- 함수 이름은? gugu로 짓자
- 입력받는 값은? 2
- 출력하는 값은? 2단(2, 4, 6, 8, …, 18)
- 결과는 어떤 형태로 저장하지? 연속된 자료형이므로 리스트!
"""
'''
def gugu(n):
    result=[]
    result.append(n*1)
    result.append(n*2)
    result.append(n*3)
    result.append(n*4)
    result.append(n*5)
    result.append(n*6)
    result.append(n*7)
    result.append(n*8)
    result.append(n*9)
    return result
'''
# 위 방식은 너무 무식한 방법

def gugu(n):
    result=[]

    i=1
    while i<10:
        result.append(n*i)
        i+=1
    return result


print(gugu(2))
# while함수를 사용하여 간략하게 작성

