"""
두 정수 a, d와 길이가 n인 boolean 배열 included가 주어집니다. 
첫째항이 a, 공차가 d인 등차수열에서 included[i]가 i + 1항을 의미할 때, 
이 등차수열의 1항부터 n항까지 included가 true인 항들만 더한 값을 return 하는 solution 함수를 작성해 주세요.
"""
def solution(a, d, included):
    answer = 0
    # included 배열의 인덱스 i를 0부터 하나씩 순회합니다.
    for i in range(len(included)):
        # 만약 included[i]가 True라면
        if included[i]:
            # i번째 항의 값인 a + d * i 를 더해줍니다.
            answer += a + (d * i)
    return answer
