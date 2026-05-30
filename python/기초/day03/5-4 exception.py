# 오류 예외 처리 기법

# 1. try-except문
'''
try:
    ...
except[발생오류[as 오류변수]]: (except ZeroDivisionError as e:)
    ...
'''

# 2. try-finally문

'''
try:
    f = open('foo.txt', 'w')
    # 무언가를 수행한다.

    (... 생략 ...)

finally:
    f.close()  # 중간에 오류가 발생하더라도 무조건 실행된다.

'''
# 3. try-else 문
'''
try:
    ...
except [발생오류 [as 오류변수]]:
    ...
else:  # 오류가 없을 경우에만 수행
    ...

'''
# 4. 오류 회피하기
'''
# process_scores.py
students = ["김철수", "이영희", "박민수", "최유진"]

for student in students:
    try:
        with open(f"{student}_성적.txt", 'r') as f:
            score = f.read()
            print(f"{student}의 성적: {score}")
    except FileNotFoundError:
        print(f"{student}의 성적 파일이 없습니다. 건너뜁니다.")
        continue  # 다음 학생으로 넘어감

'''

# 5.오류 일부러 발생시키기
'''
# error_raise.py
class Bird:
    def fly(self):
        raise NotImplementedError

rasie문을 사용하여 오류를 강제로 발생시킴
예를들어, 여러명이 함께 작업할때, 자식 클래스가 반드시 구현해야할 기능을 깜빡하고 빠뜨리는 실수를 방지
오류를 일부러 발생시키면 '이 기능을 아직 구현하지 않았다.'는 사실 바로 알 수 있음

'''

# 6.예외 만들기
