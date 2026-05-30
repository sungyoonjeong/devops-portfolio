"""
1. 파일 파싱 스크립트

배운 것: 5장 파일 입출력
만들 것: 텍스트 파일 읽어서 단어 카운트

흐름:
1. 텍스트 파일 만들기 (아무 내용)
2. open()으로 읽기
3. 단어별로 쪼개기
4. 딕셔너리로 단어 횟수 카운트
5. 많이 나온 단어 순서대로 출력
"""

# Step 1
#텍스트 파일 만들기
with open("sample.txt", "w") as f:
    f.write("파이썬 공부하자.")
#파일 읽기
with open("sample.txt","r") as f:
    content=f.read()

# Step 2
# 단어쪼개기
words = content.split()

# 단어 카운트
word_count={} #딕셔너리!!!!
for word in words:
    if word in word_count:
        word_count[word]+=1
    else:
        word_count[word]=1

# 많이 나온 순서대로 출력
sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
"""
word_count.items() : 딕셔너리(word_count)의 키(key)와 값(value)을 (key,value)형태의 튜플쌍으로 가져옴
    ex) {'apple':2, 'banana':5} => dict_items([('apple',2),('banana',5)])
sorted(......) : 데이터를 정렬하여 새로운 리스트를 반환하는 파이썬 내장 함수
key=lambda x: x[1] : 정렬의 기준
    x는 word_count.items()에서 나온 튜플, 즉('apple',2) 같은 데이터를 의미
    x[1]은 튜플의 두번째 요소인 값(value,빈도수)을 의미. 
    즉, 단어 이름(x[0])이 아닌 빈도수(x[1])를 기준으로 정렬하라는 뜻
reverse=True : 내림차순(가장 큰값이 맨 앞)으로 정렬. 기본값은 False

=> 단어 빈도수 딕셔너리(word_count)에서 (단어, 빈도수)쌍을 가져와, 빈도수(x[1])가 높은 순서(reverse=True)대로 정렬한 리스트를 sorted_words에 저장하라.
"""

print("=== 단어 카운트 ===")
for word, count in sorted_words:
    print(f"{word}: {count}번")
"""
for word, count in sorted_words : 언패킹(unpacking)기술이 적용된 반복문
    sorted_words는 앞에서 정렬한 [('banana',5),('apple',2)] 형태의 리스트
    반복문이 돌때마다 하나의 튜플('banana',5)을 가져와, 첫번째 요소는 word에, 두번째 요소는 count 변수에 자동으로 나누어 담음
    print(f"{word}: {count}번"): 포맷 스트링(f-string) 문법

    =>"정렬된 단어 리스트(sorted_words)에서 단어와 빈도수를 하나씩 꺼내와, 
      '{단어}: {빈도수}번' 형식으로 한 줄씩 예쁘게 출력하라."
"""


