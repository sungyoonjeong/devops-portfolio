"""
participant : 마라톤 참여한 선수들의 이름
completion : 완주한 선수들의 이름
return : 완주하지 못한 선수들의 이름

<알고리즘>
## collections.counter를 쓰는경우 ##
1) 카운터 객체 생성 : collection.Counter를 이용해 participant의 이름별 인원수를 정렬된 딕셔너리 형태로 만듬({'mislav':2, 'stanko':1,'ana':1})
2) 완주자 차감 : completion의 카운터 객체를 생성하여 전체 카운터에서 빼줌. 
3) 완주하지 못한 선수 추출
4) 결과 반환

## 안쓰는 경우 ##
1) 명단 정렬 : participant와 completion을 알파벳 순으로 정렬
2) 동일 인덱스 비교 : 두 배열을처음부터 차례대로 비교, 같은 인덱스에 있는 이름이 서로 다르면 완주하지 못한 선수
3) 마지막 주자 처리 : 만약 완주자 배열을 끝까지 돌 때까지 다른 이름을 못찾았다면, 완주하지 못한 선수
"""
## collections 사용한 경우 ##

# import collections  # 개수를 편리하게 세어주는 Counter 함수를 쓰기 위해 모듈을 불러옵니다.


# def solution(participant, completion):
#     # 1. 참여자 명단의 이름별 인원수를 구하고, 완주자 명단의 이름별 인원수를 구해 서로 뺍니다.
#     answer = collections.Counter(participant) - collections.Counter(completion)

#     # 2. 뺄셈 결과 남은 카운터 객체의 key(이름)들을 리스트로 반환한 뒤, 첫 번째 요소를 꺼냅니다.
#     answer = list(answer.keys())[0]
#     return answer


## collection 사용 안한 경우 ##
def solution(participant, completion):
    # 1. 참여자 명단과 완주자 명단을 알파벳 순서로 정렬합니다.
    participant.sort()
    completion.sort()

    # 2. 완주자 명단의 길이만큼 반복하며 두 명단을 같은 위치(인덱스)끼리 비교합니다.
    for i in range(len(completion)):
        # 3. 정렬된 상태에서 같은 위치의 이름이 다르다면, 그 참여자가 완주하지 못한 선수입니다.
        if participant[i] != completion[i]:
            return participant[i]

    # 4. 반복문이 끝날 때까지 다른 이름을 찾지 못했다면, 참여자 명단의 가장 마지막 선수가 완주하지 못한 선수입니다.
    answer = participant[-1]
    return answer



# 코드가 정확하게 동작하는지 확인하기 위한 테스트 코드입니다.
if __name__ == "__main__":
    print("--- 프로그래머스 완주하지 못한 선수 (정렬 풀이) 테스트 ---")

    # 예제 1: 완주하지 못한 선수가 중간에 정렬되는 경우
    p1 = ["leo", "kiki", "eden"]
    c1 = ["eden", "kiki"]
    print(f"테스트 1 결과: {solution(p1, c1)} (기대값: 'leo')")

    # 예제 2: 명단이 길고 정렬 후 중간에 다른 값이 나오는 경우
    p2 = ["marina", "josipa", "nikola", "vinko", "filipa"]
    c2 = ["josipa", "filipa", "marina", "nikola"]
    print(f"테스트 2 결과: {solution(p2, c2)} (기디값: 'vinko')")

    # 예제 3: 동명이인이 존재하여 맨 마지막 주자가 완주하지 못한 경우
    p3 = ["mislav", "stanko", "mislav", "ana"]
    c3 = ["stanko", "ana", "mislav"]
    print(f"테스트 3 결과: {solution(p3, c3)} (기대값: 'mislav')")
    
    
    
# ## collection counter ##
# 파이썬의 collections 모듈에 포함된 Counter는 데이터의 개수를 셀 때 사용하는 매우 강력하고 편리한 도구입니다. 쉽게 말해, "무엇이 몇 개 있는지"를 자동으로 계산해서 딕셔너리 형태로 만들어주는 객체입니다.

# 마라톤 문제처럼 데이터의 빈도수를 계산하고 비교해야 할 때 핵심적인 역할을 합니다. Counter 객체의 핵심 개념과 주요 특징을 정리

# 1. Counter의 기본 개념
#     # 일반 딕셔너리를 사용할 때
#     data = ["apple", "banana", "apple"]
#     counter_dict = {}

#     for fruit in data:
#         if fruit in counter_dict:
#             counter_dict[fruit] += 1
#         else:
#             counter_dict[fruit] = 1
#     # 결과: {'apple': 2, 'banana': 1}

#     # Counter를 사용한 경우
#     from collections import Counter

#     data = ["apple", "banana", "apple"]
#     counter_dict = Counter(data)
#     # 결과: Counter({'apple': 2, 'banana': 1})

# 2. Counter의 강력한 특징 3가지
#     ① 존재하지 않는 키를 조회해도 에러가 나지 않음 (0 반환)
#     - 일반 딕셔너리는 없는 키를 조회하면 KeyError가 발생하지만, Counter 객체는 자동으로 0을 반환합니다. 데이터가 존재하지 않는다는 것을 뜻하므로 조건문을 짤 때 매우 안전합니다.
#     - print(counter_dict["orange"])  # 출력: 0 (에러가 나지 않음!)
    
#     ② 카운터 객체끼리 "덧셈과 뺄셈"이 가능 (★ 마라톤 문제의 핵심)
#     - Counter 객체의 가장 강력한 점은 집합처럼 연산이 가능하다는 것입니다. 같은 키를 가진 요소끼리 알아서 더하거나 빼줍니다.
#     - 
#     from collections import Counter

#     participant = Counter(["leo", "kiki", "eden"])
#     completion = Counter(["eden", "kiki"])

#     # 참여자 명단에서 완주자 명단을 뺌
#     result = participant - completion
#     print(result)  # 출력: Counter({'leo': 1})
    
#     ③ 가장 빈도수가 높은 요소 추출 (most_common)
#     - most_common(n) 메소드를 사용하면 가장 많이 등장한 상위 n개의 요소를 (데이터, 개수) 형태의 튜플로 묶어 리스트로 반환해 줍니다. 데이터 분석이나 최빈값을 구할 때 자주 쓰입니다.
#     - 
#     data = ["apple", "banana", "apple", "cherry", "banana", "apple"]
#     print(Counter(data).most_common(2))
#     # 출력: [('apple', 3), ('banana', 2)] -> 가장 많이 나온 상위 2개