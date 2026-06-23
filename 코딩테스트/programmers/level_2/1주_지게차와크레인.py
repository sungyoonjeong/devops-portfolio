"""
A 회사의 물류창고에는 알파벳 대문자로 종류를 구분하는 컨테이너가 세로로 n줄, 가로로 m줄, 총 n*m개 놓여있음.

특정 종류 컨테이너의 출고 요청이 들어올때마다 지게차로 창고에서 접근 가능한 해당 종류의 컨테이너를 모두 꺼냄.
접근이 가능한 = 4면 중 적어도 1면이 창고 외부와 연결된 컨테이너

창고 외부와 연결되지 않은 컨테이너도 꺼낼수 있는 크레인 도입

storage : 처음 물류 창고에 놓인 컨테이너의 정보를 담은 1차원 문자열 배열
requests : 출고할 컨테이너의 종류와 출고방법을 요청 순서대로 담은 1차원 문자열 배열
return : 모든 요청을 순서대로 완료한 후 남은 컨테이너의 수를 return


<알고리즘 설계 (단계별 순서)>
   - 1단계 [격자판 확장/패딩]: 창고 테두리 4면이 모두 외부와 연결되어 있음을 쉽게 판별하기 위해, 
     기존 n x m 격자판의 상하좌우를 1칸씩 늘린 (n+2) x (m+2) 크기의 격자판을 생성하고 테두리를 '.'으로 채웁니다.
   - 2단계 [요청 순회]: requests 배열의 요청을 순서대로 하나씩 꺼내어 처리합니다.
     ① 크레인 요청 (길이 2, 예: "BB"): 접근 가능 여부와 상관없이 격자판 전체에서 해당 알파벳을 모두 '.'으로 바꿉니다.
     ② 지게차 요청 (길이 1, 예: "A"): 외부 테두리인 (0,0)에서 시작해 BFS를 돌며, 빈 공간('.')을 타고 들어가 요청된 알파벳 컨테이너를 만나면 제거 대상(출고 대상) 리스트에 추가합니다. 탐색이 끝나면 대상들을 한 번에 '.'으로 변경합니다.
   - 3단계 [남은 컨테이너 수 계산]: 모든 요청 처리가 끝난 후 격자판에 남아있는 알파벳(대문자)의 총 개수를 세어 반환합니다.

<필요 개념>
   - BFS (너비 우선 탐색): 외부 통로('.')를 연결 단위로 삼아, 가장자리부터 안쪽으로 파고들며 벽(컨테이너)을 찾는 탐색 알고리즘입니다.
   - 격자판 패딩(Padding): 좌표계의 경계선 조건 처리(0 <= x < m 등)를 생략하거나 단순화하기 위해 테두리를 여유 공간으로 감싸는 기법입니다.
"""
from collections import deque

def solution(storage, requests):
    n = len(storage)
    m = len(storage[0])
    
    # [코드 설명] 외부 접근성 체크를 유연하게 하기 위해 상하좌우 1칸씩 패딩을 넣은 격자판 생성 (초기값은 전부 빈 공간 '.')
    grid = [['.'] * (m + 2) for _ in range(n + 2)]
    for i in range(n):
        for j in range(m):
            # [코드 설명] 원본 창고 데이터를 확장 격자판의 중심 영역(1~n, 1~m)에 매핑
            grid[i + 1][j + 1] = storage[i][j]
            
    # [코드 설명] 4방향(상, 하, 좌, 우) 이동을 위한 인덱스 변화량 배열 정의
    dy = [-1, 1, 0, 0]
    dx = [0, 0, -1, 1]
    
    # [코드 설명] 주어진 출고 요청을 순서대로 하나씩 꺼내어 시뮬레이션 시작
    for req in requests:
        # [코드 설명] 요청 문자열 길이가 2이면 크레인 작동 (벽에 가로막혀 있어도 전부 제거 가능)
        if len(req) == 2:
            target = req[0]  # 제거할 대상 알파벳 추출
            for i in range(1, n + 1):
                for j in range(1, m + 1):
                    # [코드 설명] 위치 불문하고 창고 내부 전체를 탐색하며 대상 알파벳을 빈 공간('.')으로 변경
                    if grid[i][j] == target:
                        grid[i][j] = '.'
                        
        # [코드 설명] 요청 문자열 길이가 1이면 지게차 작동 (외부 통로와 닿아있는 타겟만 제거 가능)
        else:
            target = req
            visited = [[False] * (m + 2) for _ in range(n + 2)] # [코드 설명] BFS 중복 방문 방지용 배열
            queue = deque([(0, 0)]) # [코드 설명] 무조건 빈 공간인 맨 왼쪽 위 테두리 (0, 0)에서 시작
            visited[0][0] = True
            
            targets_to_remove = [] # [코드 설명] 이번 지게차 작동으로 제거될 컨테이너들의 좌표를 모아둘 리스트
            
            # [코드 설명] BFS를 통해 바깥쪽 테두리부터 연결된 빈 공간들을 탐색
            while queue:
                y, x = queue.popleft()
                
                for d in range(4):
                    ny, nx = y + dy[d], x + dx[d]
                    
                    # [코드 설명] 확장된 격자판의 경계 내부에 있고 아직 방문하지 않은 위치인 경우
                    if 0 <= ny < n + 2 and 0 <= nx < m + 2 and not visited[ny][nx]:
                        # [코드 설명] 다음 칸이 빈 공간('.')이면 통로가 뚫려있는 것이므로 계속 탐색을 이어감
                        if grid[ny][nx] == '.':
                            visited[ny][nx] = True
                            queue.append((ny, nx))
                        # [코드 설명] 다음 칸이 출고 요청된 타겟 컨테이너라면 접근 가능한 외부 벽이므로 제거 대상으로 등록 (탐색은 진행 안 함)
                        elif grid[ny][nx] == target:
                            visited[ny][nx] = True
                            targets_to_remove.append((ny, nx))
                            
            # [코드 설명] 지게차가 접근 가능한 것으로 판명된 컨테이너들을 일괄적으로 빈 공간('.') 처리 (동시 출고 처리)
            for ry, rx in targets_to_remove:
                grid[ry][rx] = '.'
                
    # [코드 설명] 모든 요청이 완료된 후 창고 내부에 남아있는 유효한 컨테이너 개수 카운트
    answer = 0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if grid[i][j] != '.':
                answer += 1
                
    return answer


# ================================================================================
# 🧪 테스트 코드 및 검증 결과 출력부
# ================================================================================
if __name__ == "__main__":
    test_cases = [
        {
            "storage": ["AZWQY", "CAABX", "BBDDA", "ACACA"],
            "requests": ["A", "BB", "A"],
            "expected": 11
        },
        {
            "storage": ["HAH", "HBH", "HHH", "HAH", "HBH"],
            "requests": ["C", "B", "B", "B", "B", "H"],
            "expected": 4
        }
    ]

    print("🚀 지게차와 크레인 테스트 케이스 검증 시작\n")
    
    for i, case in enumerate(test_cases, start=1):
        result = solution(case["storage"], case["requests"])
        print(f"--- [테스트 케이스 #{i}] ---")
        print(f"기대 결과: {case['expected']}")
        print(f"실행 결과: {result}")
        
        if result == case["expected"]:
            print("결과: ✅ Success!\n")
        else:
            print("결과: ❌ Fail!\n")
            
    print("✨ 모든 검증이 완료되었습니다.")