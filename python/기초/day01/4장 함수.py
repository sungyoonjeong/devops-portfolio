# Q1. 주어진 자연수가 홀수인지 짝수인지 판별해주는 함수(is_odd)를 작성해보자.

def is_odd(num):
    if num%2==0:
        return "짝수입니다"
    else:
        return "홀수입니다"
    
result1=is_odd(3)
result2=is_odd(4)

print(result1)
print(result2)


# Q2. 입력으로 들어오는 모든 수의 평균값을 계산해주는 함수를 작성해보자.
#(단, 입력으로 들어오는 수의 개수는 정해져있지 않다.)
#평균 값을 구할때 len 함수를 사용해보자

def avg_numbers(*args):
    result=0
    for i in args:
        result+=i
    return result/len(args)

print(int(avg_numbers(1,2,3)))
print(int(avg_numbers(1,2,3,4,5)))


# Q3.다음은 두개의 숫자를 입력받아 더하여 돌려주는 프로그램이다.
''' 
input1 = input("첫 번째 숫자를 입력하세요:") 
input2 = input("두 번째 숫자를 입력하세요:") 

total = input1 + input2 
print("두 수의 합은 %s 입니다" % total) 
이 프로그램을 수행해 보자. 

첫번째 숫자를 입력하세요:3 
두번째 숫자를 입력하세요:6 
두 수의 합은 36입니다
3과 6을 입력했을 때 9가 아닌 36이라는 결괏값을 돌려주었다. 이 프로그램의 오류를 수정해 보자. 

※ int 함수를 사용해 보자. 
''' 

input1 = int(input("첫 번째 숫자를 입력하세요:"))
input2 = int(input("두 번째 숫자를 입력하세요:"))

total = input1+input2
#print("두 수의 합은 %d 입니다" %total)
print(f"두 수의 합은 {total} 입니다.")


# Q4. 다음 중 출력 결과가 다른 것 한개를 골라라
''' 
1. print("you" "need" "python") 
2. print("you"+"need"+"python") 
3. print("you", "need", "python") 
4. print("".join(["you", "need", "python"])) 
''' 

'''
정답 : 3번
띄어쓰기 해서 출력됀다
'''

# Q5. 다음은 "test.txt"라는 파일에 "Life is too short" 문자열을 저장한 후 다시 그 파일을 읽어서 출력하는 프로그램이다.
''' 
f1 = open("test.txt", 'w') 
f1.write("Life is too short") 

f2 = open("test.txt", 'r') 
print(f2.read()) 
이 프로그램은 우리가 예상한 "Life is too short"라는 문장을 출력하지 않는다. 우리가 예상한 값을 출력할 수 있도록 프로그램을 수정해 보자. 
''' 

# 정답 : f1 open 후 close를 안해주었다. 
f1 = open("test.txt", 'w',encoding="utf-8") 
f1.write("Life is too short") 
f1. close() 

f2 = open("test.txt", 'r') 
print(f2.read()) 
f2.close() 

# Q6. 사용자의 입력을 파일(test.txt)에 저장하는 프로그램을 작성해보자
#(단, 프로그램을 다시 실행하더라도 기존에 작성한 내용을 유지하고 새로 입력한 내용을 추가해야한다)

text=input("저장할 내용을 입력하세요: ")
with open("test.txt","a",encoding="utf-8") as f:
    f.write(text + "\n")

print("기존 내용에 추가하여 저장이 완료되었습니다.")


# Q7. 다음과 같은 내용을 지닌 파일 test2.txt가 있다.
#이 파일의 내용 중 "java"라는 문자열을 "python"으로 바꾸어서 저장해보자
''' 
Life is too short 
you need java 
※ replace 함수를 사용해 보자. 
''' 
with open("test2.txt","r",encoding="utf-8") as f:
    body = f.read()
#1단계 : 파일 내용 읽어오기

body=body.replace("java","python")
#2단계 : 문자열에서 "java"를 "python"으로 변경하기

with open("test2.txt","w",encoding="utf-8") as f:
    f.write(body)

