"""
원하는 메모를 파일에 저장하고 추가 및 조회가 가능한 간단한 메모장을 만들어 보자.

- 필요한 기능은? 메모 추가하기, 메모 조회하기
- 입력값 : 메모 내용, 프로그램 실행 옵션
- 출력값 : memo.txt
"""

# 1) 메모를 추가하기
#python memo.py -a "Life is too short"
"""
import sys

option = sys.argv[1]
memo = sys.argv[2]

print(option)
print(memo)


sys.argv는 프로그램 실행 시 입력된 값을 읽어 들이는 파이썬 라이브러리. 
sys.argv[0]:파이썬 프로그램 이름인 memo.py
sys.argv[1]:프로그램 실행 옵션
sys.argv[2]:메모 내용
"""