"""
이터레이터란?

next() 함수로 값을 하나씩 꺼낼 수 있는 객체이다. 
모든 값을 꺼내면 StopIteration 예외가 발생한다.

"""

# a = [1, 2, 3]
# ia = iter(a)
#print(type(ia))

#print(next(ia))

#print(next(ia))

#print(next(ia))

#print(next(ia))

# for i in ia:
#     print(i)

# iterator.py
class MyIterator:
    # __init__ 메서드 : 이터레이터 초기화
    def __init__(self, data):
        self.data = data #반복할 데이터 저장
        self.position = 0 #현재위치추적변수(0부터)

    def __iter__(self): #이터레이터 객체 자신을 반환
        return self
    """
    - 이 메서드가 있어야 파이썬이 해당 객체를 반복 가능한 객체로 인식
    - for문, iter()함수, next()함수 등에서 사용하려면 반드시 구현해야함
    - 보통 return self로 자기 자신을 반환
    """

    def __next__(self): #다음 값을 반환
        """
    -self.position을 이용해 현재 위치의 값을 가져온다.
    -위치를 하나씩 증가시킨다.
    -더 이상 값이 없으면 stopiteration 예외 발생
        """
        if self.position >= len(self.data):
            raise StopIteration
        result = self.data[self.position]
        self.position += 1
        return result

if __name__ == "__main__":
    i = MyIterator([1,2,3])
    for item in i:
        print(item)




"""
제너레이터란?
제너레이터는 이터레이터를 쉽게 만들어 주는 함수이다.
"""

#제너레이터 표현식
# generator.py
def mygen():
    for i in range(1, 1000):
        result = i * i
        yield result

gen = mygen()

print(next(gen))
print(next(gen))
print(next(gen))
