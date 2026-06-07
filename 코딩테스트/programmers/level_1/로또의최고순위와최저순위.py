"""
1~45까지 숫자 중 6개를 찍어서 맞히는 복권
1등 : 6개 모두 일치
2등 : 5개 일치
3등 : 4개 일치
4등 : 3개 일치
5등 : 2개 일치
6(낙첨) : 그 외

알아볼수 없는 번호 : 0
ex) 44,1,0,0,31,25,  당첨번호 : 31,10,45,1,6,19 일때
최고 순위 번호 : 31, 10, 44, 6, 25, 1 => 4개 번호 일치 (3등)
최저 순위 번호 : 31, 11, 44, 7, 25, 1 => 2개번호 일치 (5등)

lottos : 민우가 구매한 로또 번호를 담은 배열
win_nums : 당첨번호를 담은 배열
return : 당첨 가능한 최고순위와 최저 순위를 차례로 담은 배열

<알고리즘>
1) lottos와 win_nums를 비교하여 일치하는 만큼 카운트 +1저장(best_correct,low_correct)
2) lottos에서 0인 수 파악 후 count => best_correct에 추가
3) result에 best_correct, low correct append
"""

def solution(lottos, win_nums):
    answer = []
    
    best_correct = 0  # 최고 맞힌 개수를 저장할 변수
    low_correct = 0   # 최저 맞힌 개수를 저장할 변수
    zero_count = 0    # 알아볼 수 없는 숫자(0)의 개수를 저장할 변수
    
    # 구매한 로또 번호를 하나씩 확인합니다.
    for i in lottos:
        if i == 0:
            zero_count += 1  # 숫자가 0이면 zero_count를 1 증가시킵니다.
            
        # 당첨 번호 배열을 돌며 일치하는 번호가 있는지 확인합니다.
        for j in win_nums:
            if i == j:
                best_correct += 1  # 일치하면 최고 개수와 최저 개수를
                low_correct += 1   # 각각 1씩 증가시킵니다.
        
    # 최고로 많이 맞히는 경우는 0인 숫자가 모두 당첨 번호인 경우이므로 zero_count를 더해줍니다.
    best_correct += zero_count
    
    # 맞힌 개수(Key)에 따른 당첨 순위(Value)를 매핑한 딕셔너리입니다.
    rank = {6: 1, 5: 2, 4: 3, 3: 4, 2: 5, 1: 6, 0: 6}
    
    # 딕셔너리를 이용해 최고 개수와 최저 개수를 순위로 변환하여 리스트로 만듭니다.
    answer = [rank[best_correct], rank[low_correct]]            
    return answer

# --- 테스트 실행 코드 ---
def run_tests():
    # 프로그래머스 공식 입출력 예시 데이터
    test_cases = [
        ([44, 1, 0, 0, 31, 25], [31, 10, 45, 1, 6, 19], [3, 5]),
        ([0, 0, 0, 0, 0, 0], [38, 19, 20, 40, 15, 25], [1, 6]),
        ([45, 4, 35, 20, 3, 9], [20, 9, 3, 45, 4, 35], [1, 1])
    ]
    
    print("========== 테스트 시작 ==========")
    for idx, (lottos, win_nums, expected) in enumerate(test_cases, 1):
        result = solution(lottos, win_nums)
        is_success = "통과" if result == expected else "실패"
        print(f"테스트 {idx}: 결과 {result} / 기대값 {expected} -> [{is_success}]")
    print("========== 테스트 종료 ==========")

# 테스트 함수 호출
run_tests()