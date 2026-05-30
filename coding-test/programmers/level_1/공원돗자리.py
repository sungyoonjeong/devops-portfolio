# 지민이는 다양한 크기의 정사각형 모양 돗자리를 가지고 공원에 소풍을 나왔습니다. 
# 공원에는 이미 돗자리를 깔고 여가를 즐기는 사람들이 많아 지민이가 깔 수 있는 가장 큰 돗자리가 어떤 건지 확인하려 합니다. 
# 예를 들어 지민이가 가지고 있는 돗자리의 한 변 길이가 5, 3, 2 세 종류이고, 
# 사람들이 다음과 같이 앉아 있다면 지민이가 깔 수 있는 가장 큰 돗자리는 3x3 크기입니다.

# 지민이가 가진 돗자리들의 한 변의 길이들이 담긴 정수 리스트 mats, 
# 현재 공원의 자리 배치도를 의미하는 2차원 문자열 리스트 park가 주어질 때 
# 지민이가 깔 수 있는 가장 큰 돗자리의 한 변 길이를 return 하도록 solution 함수를 완성해 주세요. 
# 아무런 돗자리도 깔 수 없는 경우 -1을 return합니다.

def solution(mats, park):
    # 공원의 세로(행) 길이와 가로(열) 길이를 각각 구합니다.
    rows = len(park)
    cols = len(park[0])
    
    # 가장 큰 돗자리부터 먼저 깔아보기 위해, mats 리스트를 큰 순서대로(내림차순) 정렬합니다.
    mats.sort(reverse=True)
    
    # 내림차순 정렬된 mats에서 돗자리 크기(size)를 하나씩 꺼내 검사합니다.
    for size in mats:
        
        # 공원의 모든 칸을 좌측 상단(r, c) 시작점으로 삼아 순회합니다.
        # 시작점 기준으로 size만큼의 정사각형이 공원 범위를 벗어나지 않도록 범위를 제한합니다.
        for r in range(rows - size + 1):
            for c in range(cols - size + 1):
                
                # 현재 시작점(r, c)에서 size 크기의 정사각형 자리가 모두 비어있는지 확인할 flag 변수입니다.
                is_available = True
                
                # 시작점(r, c)으로부터 가로, 세로 size만큼의 구역을 직접 다 훑어봅니다.
                for i in range(r, r + size):
                    for j in range(c, c + size):
                        # 만약 하나라도 빈칸("-1")이 아니라 다른 문자(사람)가 있다면 깔 수 없습니다.
                        if park[i][j] != "-1":
                            is_available = False
                            break # 안쪽 반복문을 탈출합니다.
                    
                    if not is_available:
                        break # 중간 반복문을 탈출합니다.
                
                # 만약 size x size 구역이 전부 "-1"이어서 flag가 True로 유지되었다면
                if is_available:
                    return size # 가장 먼저 발견된 이 크기가 깔 수 있는 최대 크기이므로 즉시 정답 반환!
                    
    # 가지고 있는 모든 돗자리를 대조해봐도 깔 수 있는 곳이 전혀 없다면 문제 요구사항대로 -1을 반환합니다.
    return -1
