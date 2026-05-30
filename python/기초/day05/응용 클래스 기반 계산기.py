"""
배운 것: 5장 클래스
만들 것: 사칙연산 계산기 클래스

흐름:
1. Calculator 클래스 만들기
2. add·subtract·multiply·divide 메서드
3. 0으로 나누면 예외 발생
4. 계산 기록 저장·출력
"""

class Calculator:
    def __init__(self):
        self.history = []  # 계산 기록 저장

    def add(self, a, b):
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a, b):
        result = a - b
        self.history.append(f"{a} - {b} = {result}")
        return result

    def multiply(self, a, b):
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result

    def divide(self, a, b):
        if b == 0:
            raise ZeroDivisionError("0으로 나눌 수 없습니다.")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result

    def print_history(self):
        print("=== 계산 기록 ===")
        for record in self.history:
            print(record)


# 실행
calc = Calculator()
print(calc.add(10, 5))
print(calc.subtract(10, 5))
print(calc.multiply(10, 5))
print(calc.divide(10, 5))

try:
    calc.divide(10, 0)
except ZeroDivisionError as e:
    print(e)

calc.print_history()