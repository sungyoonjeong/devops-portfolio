"""
같은 시간대에 게임을 이용하는 사람이 m명 늘어날때마다 서버 1대가 추가로 필요.
어느 시간대의 사용자가 m명 미만이라면, 서버 증설 필요 안함
어느 시간대의 이용자가 n*m명 이상 (n+1)*m명 미만이라면 최소 n대의 증설된 서버가 운영중이어야함.
한번 증설한 서버는 k시간동안 운영하고 반납
ex) k=5일때 10시에 증설한 서버는 10~15시에만 운영됨.

하루동안 모든게임 이용자가 게임을 하기 위해 서버를 최소 몇번 증설해야하는지 알고 싶음.
같은 시간대에 서버를 x대 증설했다면 해당 시간대의 증설횟수는 x회.

player : 0시에서 23시까지의 시간대별 게임 이용자의 수를 나타내는 1차원 정수 배열
m : 서버 한대로 감당할 수 있는 최대 이용자의 수
k : 서버 한대가 운영 가능한 시간을 나타내는 정수
return : 모든 게임 이용자를 감당하기 위한 최소 서버 증설 횟수

<알고리즘 순서>
1) 필요한 변수 생성
    - total_extensions(총 증설 횟수) : 0으로 초기화
    - active_servers(현재 운영중인 서버 목록) : 각 시간대별로 증설된 서버가 언제 만료되는지 기록할 배열이나 리스트. 하루가 24시간이므로, 크기가 24인 리스트([0] * 24) 를 만들어 "해당 시간에 끝나는 서버의 수"를 기록하는 방식
    - current_running_servers (현재 가동중인 서버 총합) : 매 시간마다 현재 운영중인 서버의 총개수를 유지할 변수. 0으로 초기화

2) 0시부터 23시까지 매 시간 (t) 순회
    - for t in range(24)
        1.만료된 서버 반납처리
            : 현재 시간 t에 운영이 종료되는 서버가 있다면, current_running_servers에서 그만큼 차감.
            : (current_running_servers -= active_servers[t])
        2. 필요한 최소 서버 대수 계산
            : 해당 시간대의 이용자 수 player[t]를 감당하기 위해 필요한 최소 서버 대수를 구해야함.
            : 문제 조건에 따라 이용자가 n*m이상 (n+1)*m 미만일때 n대가 필요하므로, 필요한 서버 대수는 players[t] // m
        3. 서버 증설 여부 판단 및 추가
            : 만약 현재 가동 중인 서버수(current_running_servers)가 필요한 서버 대수 (players[t]//m)보다 적다면 서버를 증설해야함.
            : 증설해야할 대수 (needed) = (players[t]//m) - current_running_servers
            : 증설을 진행한다면 
                - total_extensions에 needed를 더함
                - current_running_servers에 needed를 더함
                - 이 서버들은 k 시간 동안 운영되므로, 만료되는 시점인 t+k시에 needed 만큼 반납되도록 기록.(단, t+k가 24미만일때만 배열에 기록)

<알고리즘 요약 흐름도>
[0시~23시 루프]
1. t시에 만료된 서버 수만큼 현재 가동 서버에서 제외
2. t시에 필요 서버 수 계산 => players[t]//m
3. 현재 가동서버 < 필요서버 인가?
    - yes : 부족한 만큼(needed) 서버 증설
        - 총 증설 횟수 및 현재 가동 서버수에 needed합산
        - t+k 시점에 needed 대수가 만료되도록 예약
    - No : 패스
    
<핵심 개념>
1. 그리디(greedy) & 시뮬레이션 : 매 시간(0~23시)마다 "지금 당장 필요한 서버가 몇대인가?"를 확인하고 부족한 만큼만 바로바로 채워나가는 방식
2. 슬라이딩 윈도우 / 큐(queue) 개념의 배열 : 서버는 한번 켜지면 k시간 동안만 유지되고 꺼짐. 이를 관리하기 위해 크기가 24인 리스트를 만들어 "해당 시각에 만료되어 사라질 서버대수"를 기록하고 차감해 주는 방식으로 가동중인 서버수 관리
"""
def solution(players, m, k):
    # 1. 총 증설 횟수를 기록할 변수 초기화
    total_extensions = 0
    
    # 2. 현재 가동중인 총 서버 대수를 기록할 변수 초기화
    current_running_servers = 0
    
    # 3. 각 시간대(0~23시)에 "만료되어 종료될" 서버 대수를 기록할 배열(24시간 크기)
    expire_servers = [0]*24
    
    # 4. 0시 부터 23시까지 1시간 단위로 시뮬레이션 진행
    for t in range(24):
        # 현재시간(t)에 운영이 만료된 서버가 있다면 가동 중인 서버에서 제외
        current_running_servers -= expire_servers[t]
        
        # 현재 시간대의 이용자수(players[t])를 감당하기 위해 필요한 최소 서버 대수 계산
        needed_servers = players[t]//m
        
        # 현재 가동중인 서버가 필요한 대수보다 부족한 경우 증설 진행
        if current_running_servers < needed_servers:
            # 부족한 만큼의 서버 대수 계산
            needed = needed_servers - current_running_servers
            
            # 총 증설 횟수에 누적
            total_extensions += needed
            
            # 현재 가동 중인 서버 수에 추가
            current_running_servers += needed
            
            # 이 서버들은 k 시간 뒤에 만료되므로, 만료 시점(t+k)이 하루(24시) 이내라면 만료 배열에 기록
            if t+k < 24:
                expire_servers[t+k] += needed
    
    # 모든 시간대를 순회한 후 최종 증설 횟수 반환
    answer = total_extensions
    return answer

# ==================== [ 테스트 케이스 실행 및 검증 ] ====================
if __name__ == "__main__":
    # 프로그래머스 입출력 예시 데이터 정의
    test_cases = [
        {
            "players": [0, 2, 3, 3, 1, 2, 0, 0, 0, 0, 4, 2, 0, 6, 0, 4, 2, 13, 3, 5, 10, 0, 1, 5],
            "m": 3,
            "k": 5,
            "expected": 7
        },
        {
            "players": [0, 0, 0, 10, 0, 12, 0, 15, 0, 1, 0, 1, 0, 0, 0, 5, 0, 0, 11, 0, 8, 0, 0, 0],
            "m": 5,
            "k": 1,
            "expected": 11
        },
        {
            "players": [0, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 5, 0, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1],
            "m": 1,
            "k": 1,
            "expected": 12
        }
    ]

    print("🚀 테스트 케이스 검증을 시작합니다.\n")
    
    for i, case in enumerate(test_cases, start=1):
        result = solution(case["players"], case["m"], case["k"])
        
        print(f"--- [테스트 케이스 #{i}] ---")
        print(f"입력값 (m): {case['m']}, (k): {case['k']}")
        print(f"기대 결과: {case['expected']}")
        print(f"실행 결과: {result}")
        
        if result == case["expected"]:
            print("결과: ✅ Success!\n")
        else:
            print("결과: ❌ Fail! (정답과 다릅니다.)\n")
            
    print("✨ 모든 테스트 검증 완료")