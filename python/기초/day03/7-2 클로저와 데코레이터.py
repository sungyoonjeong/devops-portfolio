"""
클로저란?

외부함수의 변수를 기억하는 내부함수
예를들어, 함수 A안에 함수 B가 있고, 함수 B가 함수 A의 변수를 사용한다
보통 함수 A가 끝나면 함수A의 변수도 사라지지만 클로저에서는 함수 A가 끝나도 계속 사용 가능

"""

# closure.py
class Mul:
    def __init__(self, m):
        self.m = m

    def mul(self, n):
        return self.m * n

if __name__ == "__main__":
    mul3 = Mul(3)
    mul5 = Mul(5)

    print(mul3.mul(10))  # 30 출력
    print(mul5.mul(10))  # 50 출력


#__call__ 메서드를 이용하면 다음과 같이 개선할 수도 있다.

# closure.py
class Mul:
    def __init__(self, m):
        self.m = m

    def __call__(self, n):
        return self.m * n

if __name__ == "__main__":
    mul3 = Mul(3)
    mul5 = Mul(5)

    print(mul3(10))  # 30 출력
    print(mul5(10))  # 50 출력
"""
__call__은 객체를 함수처럼 호출할 수 있게 해주는 특수 메서드이다. 
즉, mul3(10)처럼 객체 뒤에 괄호를 붙여 호출하면 파이썬이 자동으로 __call__ 메서드를 실행한다. 
이전 코드에서는 mul3.mul(10)처럼 메서드 이름을 명시해야 했지만, 
__call__을 사용하면 mul3(10)처럼 간결하게 호출할 수 있다.
"""


def mul(m):
    def wrapper(n):
        return m * n
    return wrapper

if __name__ == "__main__":
    mul3 = mul(3)
    mul5 = mul(5)

    print(mul3(10))  # 30 출력
    print(mul5(10))  # 50 출력

"""
클로저의 핵심
mul(3)을 호출하면 외부 함수 mul은 종료되지만, 반환된 wrapper 함수는 여전히 m=3 값을 기억하고 있다. 
이후 mul3(10)을 호출하면 wrapper 함수가 기억하고 있던 m=3 값을 사용해서 3 * 10 = 30을 계산한다.

즉, 클로저는 함수가 생성될 때의 환경(변수 값)을 기억하는 특별한 함수라고 할 수 있다. 
여기서 반환된 wrapper 함수가 바로 클로저
"""


"""
데코레이터란?

데코레이터(decorator)는 클로저를 활용하여 기존 함수를 수정하지 않고 기능을 덧붙이는 기법이다.

"""