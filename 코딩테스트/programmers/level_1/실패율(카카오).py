"""
동적으로 게임 시간을 늘려서 난이도 조절
실패율을 구하는 코드 
    - 스테이지에 도달했으나 아직 클리어하지 못한 플레이어의 수 / 스테이지에 도달한 플레이어수

N : 전체 스테이지의 개수
stages : 게임을 이용하는 사용자가 현재 멈춰있는 스테이지의 번호가 담긴 배열
return : 실패율이 높은 스테이지부터 내림차순으로 스테이지의 번호가 담겨있는 배열

<알고리즘>
1) 도전자 수 파악 : stages 배열의 길이는 처음에 1번 스테이지에 도달한 총 플레이어 수(len)
2) 스테이지별 빈도 계산 : count() 나 딕셔너리를 활용해 각 스테이지에 몇 명의 유저가 머물러 있는지(클리어 하지 못했는지)구함
3) 실패율 계산 및 인원 갱신 : 1번 스테이지부터 N번 스테이지까지 순서대로 돌면서 실패율 계산
    - 해당 스테이지에 도달한 사람(length)이 0보다 크다면 실패율 = 현재 스테이지 체류인원/length
    - 실패율을 구한 뒤, 다음 스테이지에 도달한 인원을 구하기 위해 length에서 현재 스테이지 체류인원 차감
    - 도달한 사람이 없다면 문제 조건에 따라 실패율을 0으로 처리
4) 정렬 : (스테이지 번호, 실패율) 형태로 저장한 뒤, 실패율을 기준으로 내림차준 정렬.
    - 파이썬의 sort()는 기본적으로 stable sort이므로, 실패율만 내림차순 정렬 지정을 해주면 스테이지 번호는 알아서 오름차순이 유지
"""
def solution(N, stages):
    answer = []
    
    fail_rates = [] # 각 스테이지의 번호와 실패율을 저장할 리스트를 생성합니다.
    total_players = len(stages) # 1번 스테이지에 도달한 총 플레이어 수로 시작합니다.
    
    # 1번부터 N번 스테이지까지 순서대로 실패율을 계산합니다.
    for stage in range(1, N + 1):
        # 현재 스테이지에 머물러 있는(클리어하지 못한) 플레이어 수를 구합니다.
        current_stage_players = stages.count(stage)
        
        # 스테이지에 도달한 유저가 있는 경우 실패율을 계산합니다.
        if total_players > 0:
            rate = current_stage_players / total_players # (도달했으나 미클리어 유저 수) / (도달한 유저 수)
            total_players -= current_stage_players # 다음 스테이지 도달 인원 계산을 위해 현재 스테이지 인원을 제외합니다.
        else:
            rate = 0 # 스테이지에 도달한 유저가 없는 경우 실패율은 0이 됩니다.
            
        fail_rates.append((stage, rate)) # 스테이지 번호와 계산된 실패율을 튜플 형태로 저장합니다.
        
    # 실패율(x[1])을 기준으로 내림차순(reverse=True) 정렬합니다. 실패율이 같으면 기본 저장 순서(스테이지 번호 오름차순)를 유지합니다.
    fail_rates.sort(key=lambda x: x[1], reverse=True)
    
    return [stage[0] for stage in fail_rates] # 정렬된 결과에서 스테이지 번호만 추출하여 리스트로 반환합니다.
    return answer

def test_solution():
    print("2019 KAKAO BLIND RECRUITMENT [실패율] 예제 검증 시작...\n")
    
    # 입출력 예 #1
    N1 = 5
    stages1 = [2, 1, 2, 6, 2, 4, 3, 3]
    expected1 = [3, 4, 2, 1, 5]
    result1 = solution(N1, stages1)
    print(f"테스트 1 결과: {'통과(PASS)' if result1 == expected1 else '실패(FAIL)'} (실제: {result1})")
    
    # 입출력 예 #2
    N2 = 4
    stages2 = [4, 4, 4, 4, 4]
    expected2 = [4, 1, 2, 3]
    result2 = solution(N2, stages2)
    print(f"테스트 2 결과: {'통과(PASS)' if result2 == expected2 else '실패(FAIL)'} (실제: {result2})")

# 테스트 실행
test_solution()