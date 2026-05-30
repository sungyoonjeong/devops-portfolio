# 모듈
# 함수나 변수 또는 클래스를 모아 놓은 파이썬 파일
# 다른 파이썬 프로그램에서 불러와 사용할 수 있게 만든 파이썬 파일

# 모듈 만들기

def add(a,b):
    return a+b
def sub(a,b):
    return a-b

# 위의 함수들 "mod1.py"로 저장한후 저장한 위치로부터 import mod1을하면 불러오기 가능
# from "모듈_이름" import "모듈_함수"(혹은 *:모든 함수)

# __name__변수:파이썬이 내부적으로 사용하는 특별한 변수 이름
# python mod1.py 처럼 직접 mod1.py 파일을실행할 경우 mod1.py의 __name__변수에는 __main__값이 저장된다.
# 하지만 파이썬 셸이나 다른 파이썬 모듈에서 mod1을 import 할 경우에는 mod1.py의 __name__변수에 mod1.py의 모듈이름인mod1이 저장된다.

# sys모듈:파이썬을설치할때 함께 설치되는 라이브러리 모듈
# 파이썬 라이브러리 설치되어 있는 디렉터리 확인 가능
# sys.path에 내가 만든 모듈 추가해서 사용 가능(어디서든 불러서 사용 가능)
#  =>export PYTHONPATH=