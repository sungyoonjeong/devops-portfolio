"""
영어 알파벳으로 이루어진 문자열 str이 주어집니다. 
각 알파벳을 대문자는 소문자로 소문자는 대문자로 변환해서 출력하는 코드를 작성해 보세요.
"""

# 1번방법
#str = input()
#print(str.swapcase())

# 2번 방법
str=input()
result=""

for char in str:
    if char.isupper():
        result+=char.lower()
    else:
        result+=char.upper()

print(result)