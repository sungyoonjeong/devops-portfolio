"""
문제:
도서관 관리 프로그램을 만들어라.

조건:
① Book 클래스 만들기
   - 속성: 제목(title), 저자(author), 대출여부(is_borrowed)
   - 메서드:
     borrow(): 대출 처리 (이미 대출 중이면 예외 발생)
     return_book(): 반납 처리
     __str__(): "제목 - 저자 (대출가능/대출중)" 출력

② 예외 처리
   - 이미 대출 중인 책을 또 빌리려 하면
     AlreadyBorrowedException 발생시키기

③ 실행 예시:
   book1 = Book("파이썬 기초", "홍길동")
   print(book1)  # 파이썬 기초 - 홍길동 (대출가능)
   book1.borrow()
   print(book1)  # 파이썬 기초 - 홍길동 (대출중)
   book1.borrow()  # AlreadyBorrowedException 발생
"""

class AlreadyBorrowedException(Exception):
    pass

class Book:
    def __init__(self,title,author):
        self.title=title
        self.author=author
        self.is_borrowed=False
    def borrow(self):
        try:
            if self.is_borrowed:
                raise AlreadyBorrowedException("이미 대출 중입니다.")
            self.is_borrowed = True #대출가능일때 true로 변경
        except AlreadyBorrowedException as e: 
        #자신이 발생시킨 예외를 여기서 붙잡아 프로그램이 죽는 것을 막습니다.
            print(e)
    def __str__(self):
        status="대출중" if self.is_borrowed else "대출가능"
        #self.is_borrowed가 true면 "대출중", False면 "대출가능"
        return f"{self.title} - {self.author} ({status})"
    def return_book(self):
        self.is_borrowed=False

book1=Book("파이썬 기초","홍길동")
print(book1)

book1.borrow()
print(book1)

book1.borrow()

book1.return_book()
print(book1)

book1.borrow()
print(book1)