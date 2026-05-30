'''
클래스 : 함수나 자료형처럼 프로그램 작성을 위해 꼭 필요한 요소는 아니다.
객체를 생성함으로써 함수만 사용할때보다 간단하게 프로그램 작성 가능

클래스 = 과자틀
객체 = 과자틀로 찍어낸 과자
'''
'''
class FourCal:
    def setdata(self,first,second): #method:클래스 안에 구현된 함수
        self.first=first
        self.second=second
    
    def add(self):
        result=self.first+self.second
        return result

    def mul(self):
        result=self.first*self.second
        return result
    
    def sub(self):
        result=self.first-self.second
        return result
    
    def div(self):
        result=self.first/self.second
        return result
    
a=FourCal()
print(type(a)) #객체 a는 클래스 FourClass의 객체

a.setdata(4,2)
print(a.first)
print(a.second)
print(a.add())
print(a.mul())
print(a.sub())
print(a.div())

b=FourCal()
b.setdata(3,8)
print(b.first)
print(b.second)
print(b.add())
print(b.mul())
print(b.sub())
print(b.div())
'''

#위의 FourCal 클래스의 method를 아래와 같이 변경한다면 setdata를 호출하지 않아도 실행됨

class FourCal:
    def __init__(self,first,second): #method:클래스 안에 구현된 함수
        self.first=first
        self.second=second

    def setdata(self,first,second): #method:클래스 안에 구현된 함수
        self.first=first
        self.second=second
    
    def add(self):
        result=self.first+self.second
        return result

    def mul(self):
        result=self.first*self.second
        return result
    
    def sub(self):
        result=self.first-self.second
        return result
    
    def div(self):
        result=self.first/self.second
        return result
    
'''
a=FourCal(4,2) #a.setdata(4,2)를 해주지 않아도됌
print(a.first)
print(a.second)
'''

# 클래스의 상속 : 어떤 클래스를 만들 때 다른 클래스의 기능을 물려받을 수 있게 만듬

class MoreFourCal(FourCal):
    def pow(self):
        result=self.first**self.second
        return result

a=MoreFourCal(4,2)
print(a.add())
print(a.pow())


# method의 오버라이딩
# FourCal클래스에 있는 div메서드를 동일한 이름으로 다시 작성
# 부모클래스(상속한 클래스)에 있는 method를 동일한 이름으로 다시 만드는것이 메서드 오버라이딩
# 부모 클래스의 메서드 대신 오버라이딩한 메서드가 호출됨

a=FourCal(4,0)
#print(a.div())

class SafeFourCal(FourCal):
    def div(self):
        if self.second == 0:#나누는 값이 0인경우 0을 반환하도록 수정
            return 0
        else:
            return self.first/self.second
        
a=SafeFourCal(4,0)
print(a.div())


# 클래스 변수

class Family:
    lastname="김"

a=Family()
print(a.lastname)
a.lastname="최"
print(a.lastname)