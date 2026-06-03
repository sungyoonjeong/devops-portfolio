"""
사과 상태 : 1점 ~ k점
k점 = 최상품
1점 = 최하품
사과 한 상자의 가격은 아래와 같이 결정
    1) 한 상자에 사과를 m개씩 담아 포장.
    2) 상자에 담긴 사과 중 가장 낮은 점수가 p(1<=p<=k)점인 경우, 사과 한 상자의 가격은 p*m
가능한 많은 사과를 팔았을 때, 얻을 수 있는 최대 이익 계산(사과는 상자 단위로만 판매, 남은 사과는 버림)
ex) k=3,m=4, 사과 7개의 점수가 [1,2,3,1,2,3,1]이라면, 다음과 같이 [2,3,2,3]으로 구성된 사과 상자 1개 만듬
    최대 이익 가능=>(최저 사과 점수) * (한 상자에 담긴 사과 개수) * (상자의 개수) = 2*4*1 = 8

k : 사과의 최대 점수
m : 한 상자에 들어가는 사과의 수 
score : 사과들의 점수 
return : 과일 장수가 얻을 수 있는 최대 이익
"""

"""
Step1) len(score) => 사과의 개수
Step2) score 추적하면서 1<=score[i]<=k 범위 안의 값을 따로 저장(rescore)
Step3) 저장한 리스트 내림차순으로 정렬 (rescore.sort(reverse=True))
Step4) [0:m],[m:2*m]...식으로 리스트 저장.
Step5) 각 리스트 추적하며 min*m 을 append
Step6) append한 값 모두 합하여 결과 출력
"""
def solution(k, m, score):
    answer = 0       # 최종 누적 이익을 저장할 변수를 0으로 초기화합니다.
    rescore = []     # 조건에 맞는 정상적인 사과 점수들만 따로 담을 빈 리스트를 만듭니다.
    num_apple = len(score)  # 입력받은 전체 사과의 개수를 구합니다. (현재 코드에선 선언 후 사용되지 않음)
    box = []         # 상자들을 담을 빈 리스트를 만듭니다. (현재 코드에선 선언 후 사용되지 않음)
    
    # [Step 2] 입력받은 사과 점수 리스트(score)를 처음부터 끝까지 순회합니다.
    for i in range(len(score)):
        # 만약 사과 점수가 최고 등급(k)을 초과하거나, 0보다 작다면 (잘못된 데이터라면)
        if int(score[i]) > k or int(score[i]) < 0:
            continue  # 이번 사과는 무시하고 다음 사과로 넘어갑니다.
        else:
            # 정상적인 범위의 사과 점수라면 rescore 리스트에 추가합니다.
            rescore.append(score[i])
            
    # [Step 3] 가장 높은 점수의 사과부터 묶기 위해 rescore 리스트를 내림차순(큰 수부터) 정렬합니다.
    rescore.sort(reverse=True)
    
    # [Step 4~6] 0부터 rescore의 길이까지, 상자 크기인 m씩 인덱스를 건너뛰며 반복합니다.
    # 예: m이 3이면 i는 0, 3, 6, 9... 순서로 변합니다.
    for i in range(0, len(rescore), m):
        # 현재 인덱스(i)부터 m개를 채웠을 때, 리스트 전체 범위를 벗어나지 않는지 확인합니다.
        # 즉, 남은 사과로 '온전한 상자 하나(m개)'를 만들 수 있는지 검사하는 조건입니다.
        if i + m <= len(rescore):
            # 내림차순 정렬 상태이므로, 현재 상자(i부터 i+m-1까지)의 마지막 원소가 가장 낮은 점수(p)입니다.
            min_score = rescore[i + m - 1]
            # (최저 사과 점수 * 한 상자의 사과 개수)를 계산하여 총 이익(answer)에 더해줍니다.
            answer += min_score * m
                    
    # 모든 상자 계산이 끝나면 최종 누적된 최대 이익을 반환합니다.
    return answer


# ==========================================
# 🧪 테스트 케이스 실행 및 검증 코드
# ==========================================
if __name__ == "__main__":
    print("=== [과일 장수] 테스트 케이스 검증 시작 ===")
    
    # 테스트 케이스 1
    k1, m1, score1 = 3, 4, [1, 2, 3, 1, 2, 3, 1]
    expected1 = 8
    result1 = solution(k1, m1, score1)
    print(f"\n[테스트 1]")
    print(f"입력값 〉 k={k1}, m={m1}, score={score1}")
    print(f"기댓값 〉 {expected1}")
    print(f"실행결과 〉 {result1}")
    print(f"통과여부 〉 {'실패 ❌' if result1 != expected1 else '성공  (수정됨)'}")
    
    # 테스트 케이스 2
    k2, m2, score2 = 4, 3, [4, 1, 2, 2, 4, 4, 4, 4, 1, 2, 4, 2]
    expected2 = 33
    result2 = solution(k2, m2, score2)
    print(f"\n[테스트 2]")
    print(f"입력값 〉 k={k2}, m={m2}, score={score2}")
    print(f"기댓값 〉 {expected2}")
    print(f"실행결과 〉 {result2}")
    print(f"통과여부 〉 {'실패 ❌' if result2 != expected2 else '성공  (수정됨)'}")

    print("\n==========================================")