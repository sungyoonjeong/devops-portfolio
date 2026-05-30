"""
A 씨는 게시판 프로그램을 작성하고 있다. 
그런데 게시물의 총 개수와 한 페이지에 보여 줄 게시물 수를 입력받아 총 페이지 수를 출력하는 프로그램이 필요하다고 한다.

==> 이렇게 게시판의 페이지 수를 구하는 것을 '페이징'이라고 부른다.

- 함수 이름 : get_total_page
- 입력받는값? : 게시물의총 개수(m), 한 페이지에 보여줄 게시물 수(n)
- 출력값 : 총 페이지수

게시물의 총 개수(m)	페이지당 보여 줄 게시물 수(n)	총 페이지 수
5	                10	                        1
15	                10	                        2
25	                10	                        3
30	                10	                        3

1) 총 게시물 수(m)를 한페이지에 보여줄 게시물 수(n)으로 나누고 1을 더하면 총 페이지수
    => total_page=(m/n)+1
"""
'''
def get_total_page(m,n):
    return m//n + 1

print(get_total_page(5, 10))    # 1 출력
print(get_total_page(15, 10))   # 2 출력
print(get_total_page(25, 10))   # 3 출력
print(get_total_page(30, 10))   # 4 출력
'''

#4번째 출력값이 3이 나와야하는데 4가 나옴
#이 케이스는 나머지가 0일때 발생함
# 따라서 아래의 코드로 변경해야함

def get_total_page(m, n):
    if m % n == 0:
        return m // n
    else:
        return m // n + 1

print(get_total_page(5, 10))
print(get_total_page(15, 10))
print(get_total_page(25, 10))
print(get_total_page(30, 10))  # 3 출력