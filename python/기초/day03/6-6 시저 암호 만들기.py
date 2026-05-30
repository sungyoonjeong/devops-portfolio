# 시저 암호 : 문자열을 암호화 하는 프로그램
# 고대 로마의 율리우스 카이사르가 사용한 암호 방식
# 알파벳을 일정한 수만큼 밀어서 다른 글자로 바꾸는 것
# 예를들어 A를 3칸 밀면 D가 되고, B는 E가 된다.
"""
A B C D E F G H I J K L M N O P Q R S T U V W X Y Z (원본)
D E F G H I J K L M N O P Q R S T U V W X Y Z A B C (3칸)

이 방식대로라면 "PYTHON"은 3칸 밀어 "SBWKRQ"이 된다.

필요한 기능은? 알파벳을 원하는 칸 수만큼 밀어 암호화하기
입력받는 값은? 문자열, 밀 칸 수
출력하는 값은? 암호화된 문자열
"""

# 1) 알바펫 한 글자를 원하는 칸 수 만큼미는 방법
# 파이썬에서 문자를 숫자로 바꾸려면 ord함수 사용
# 숫자를 다시 문자로 바꾸려면 chr함수 사용
"""
word = "PYTHON"
key = 3
result = ""

for char in word:
    num = ord(char) - ord('A')       # 알파벳을 0~25 숫자로 변환
    shifted = (num + key) % 26        # 밀고 26으로 나눈 나머지
    result += chr(shifted + ord('A')) # 다시 알파벳으로 변환

print(result)
"""

# 2) 함수를 만들고, 사용자가 직접 문자열과 밀 칸수를입력할수 있도록
def caesar(word, key):
    result = ""
    for char in word:
        num = ord(char) - ord('A')
        shifted = (num + key) % 26
        result += chr(shifted + ord('A'))
    return result

word = input("문자열을 입력하세요: ")
key = int(input("밀 칸 수를 입력하세요: "))

print(f"암호화: {caesar(word, key)}")