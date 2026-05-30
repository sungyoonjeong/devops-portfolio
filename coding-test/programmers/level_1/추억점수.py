'''
사진들을 보며 추억에 젖어 있던 루는 사진별로 추억 점수를 매길려고 합니다. 
사진 속에 나오는 인물의 그리움 점수를 모두 합산한 값이 해당 사진의 추억 점수가 됩니다. 
예를 들어 사진 속 인물의 이름이 ["may", "kein", "kain"]이고 각 인물의 그리움 점수가 [5점, 10점, 1점]일 때 해당 사진의 추억 점수는 16(5 + 10 + 1)점이 됩니다. 
다른 사진 속 인물의 이름이 ["kali", "mari", "don", "tony"]이고 ["kali", "mari", "don"]의 그리움 점수가 각각 [11점, 1점, 55점]]이고, "tony"는 그리움 점수가 없을 때, 
이 사진의 추억 점수는 3명의 그리움 점수를 합한 67(11 + 1 + 55)점입니다.

그리워하는 사람의 이름을 담은 문자열 배열 name, 
각 사람별 그리움 점수를 담은 정수 배열 yearning, 
각 사진에 찍힌 인물의 이름을 담은 이차원 문자열 배열 photo가 매개변수로 주어질 때, 
사진들의 추억 점수를 photo에 주어진 순서대로 배열에 담아 return하는 solution 함수를 완성해주세요.
'''

'''
사진별 추억점수 매기려고 함
그리움 점수 합 = 추억 점수
name = 사람이름
yearning = 그리움 점수를 담은 정수 배열
photo = 인물의 이름을 담은 문자열 배열

step1) 데이터 매핑
    - name 배열과 yearning 배열을 딕셔너리형태로 묶어줌
step2) 사진별 인물 확인
    - photo를 순회하면서 사진 한장씩(p) 꺼냄
step3) 점수 합산 및 예외처리
    - 사진에 찍힌 인물들을 한명씩 확인하며 딕셔너리에서 점수를 찾아 더함
    - name리스트에 없는경우 => 0점 처리
'''
def solution(name, yearning, photo):
    answer = []
    
    # step1: {이름 : 점수} 딕셔너리 만들기
    # zip 함수를 사용하면 두 배열을 쉽게 쌍으로 묶을 수 있음
    # zip(name, yearning) : 두 배열을 ('may',5),('kein',10) 형태로 짝지어줌
    # 이를 dict()로 감싸면 {'may':5, 'kein':10} 같은 딕셔너리가 한줄로 완성
    score_map = dict(zip(name,yearning))
    
    # step2: 각 사진을 하나씩 순회
    for p in photo:
        total_score=0
        
        #step3: 사진 속에 있는 사람들의 점수 합산
        for person in p:
            #딕셔너리에 이름이 있으면 점수를 반환, 없으면 0
            #score_map.get(person,0):파이썬 딕셔너리의 get 함수는 매우 유용
            #person이라는 Key가 딕셔너리에 존재하면 해당 점수를 가져오고, 존재하지 않으면 두번째 인자로 준 0을 기본값으로 반환 => 예외처리 깔끔
            total_score += score_map.get(person,0)
        
        # 계산된 사진의 총점을 결과 배열에 추가
        answer.append(total_score)
    
    
    return answer



# --- 테스트케이스 실행 코드 ---

# 입출력 예 #1
name1 = ["may", "kein", "kain", "radi"]
yearning1 = [5, 10, 1, 3]
photo1 = [
    ["may", "kein", "kain", "radi"],
    ["may", "kein", "brin", "deny"],
    ["kon", "kain", "may", "coni"]
]
print(f"테스트 1 결과: {solution(name1, yearning1, photo1)} (기댓값: [19, 15, 6])")


# 입출력 예 #2
name2 = ["kali", "mari", "don"]
yearning2 = [11, 1, 55]
photo2 = [
    ["kali", "mari", "don"],
    ["pony", "tom", "teddy"],
    ["con", "mona", "don"]
]
print(f"테스트 2 결과: {solution(name2, yearning2, photo2)} (기댓값: [67, 0, 55])")


# 입출력 예 #3
name3 = ["may", "kein", "kain", "radi"]
yearning3 = [5, 10, 1, 3]
photo3 = [
    ["may"],
    ["kein", "deny", "may"],
    ["kon", "coni"]
]
print(f"테스트 3 결과: {solution(name3, yearning3, photo3)} (기댓값: [5, 15, 0])")

# 검증 (틀리면 에러가 발생합니다)
assert solution(name1, yearning1, photo1) == [19, 15, 6]
assert solution(name2, yearning2, photo2) == [67, 0, 55]
assert solution(name3, yearning3, photo3) == [5, 15, 0]
print("\n모든 입출력 예시 테스트를 통과했습니다! 🎉")