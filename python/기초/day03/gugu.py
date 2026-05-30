#구구단 프로그램 만들기

def gugu(n):
    result=[]
    i=1
    while i<10:
        result.append(n*i)
        i+=1
    return result


print(gugu(2))