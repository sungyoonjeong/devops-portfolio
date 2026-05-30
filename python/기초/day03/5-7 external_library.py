# 외부 라이브러리
# 사용하기 위해 설치가 필요
'''
1.pip
파이썬 모듈이나 패키지를 쉽게 설치할 수 있도록 도와주는 도구.
모듈이나 패키지를 자동으로 함께 설치해줌

python -m pip install SomePackage
python -m pip uninstall SomePackage
python -m pip install SomePackage==1.0.4
python -m pip install --upgrade SomePackage
python -m pip list

2.Faker
테스트용 가짜 데이터를 생성할 때 사용하는 라이브러리
fake.name()	이름
fake.address()	주소
fake.postcode()	우편 번호
fake.country()	국가명
fake.company()	회사명
fake.job()	직업명
fake.phone_number()	전화 번호
fake.email()	이메일 주소
fake.user_name()	사용자명
fake.pyint(min_value=0, max_value=100)	0부터 100 사이의 임의의 숫자
fake.ipv4_private()	IP 주소
fake.text()	임의의 문장 (한글 임의의 문장은 fake.catch_phrase() 사용)
fake.color_name()	색상명

3.sympy
방정식 기호(symbol)를 사용하게해주는 외부 라이브러리
python -m pip install sympy

x^2=1 방정식의 해를 구하라
>>> import sympy
>>> x = sympy.symbols("x")
>>> f = sympy.Eq(x**2, 1)
>>> sympy.solve(f)

[-1, 1]

'''