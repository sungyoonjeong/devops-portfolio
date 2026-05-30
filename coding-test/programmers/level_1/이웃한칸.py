# 문제

# 각 칸마다 색이 칠해진 2차원 격자 보드판이 있습니다. 
# 그중 한 칸을 골랐을 때, 위, 아래, 왼쪽, 오른쪽 칸 중 같은 색깔로 칠해진 칸의 개수를 구하려고 합니다.

# 보드의 각 칸에 칠해진 색깔 이름이 담긴 이차원 문자열 리스트 board와 고른 칸의 위치를 나타내는 
# 두 정수 h, w가 주어질 때 board[h][w]와 이웃한 칸들 중 같은 색으로 칠해져 있는 칸의 개수를 
# return 하도록 solution 함수를 완성해 주세요.

# 이웃한 칸들 중 몇 개의 칸이 같은 색으로 색칠되어 있는지 확인하는 과정은 다음과 같습니다.

# board : 각 칸에 칠해진 색깔 이름 (2차원 문자열 리스트)
#     h,w : 고른 칸의 위치를 나타내는 두 정수
#     board[h][w] 와 이웃한 칸들 중 같은 색으로 칠해져 있는 칸의 개수를 return
    
#     1) 정수를 저장할 변수 n <- len(board)
#     2) 같은 색으로 색칠된 칸의 개수를 저장한 변수 count <- 0
#     3) h,w 변화량을 저장할 정수 리스트 dh,dw <- [0,1,-1,0],[1, 0, 0, -1] 
#     4) 반복문 i 값을 0~3까지 1씩 증가시키며 아래 작업 반복
#       4-1) 체크할 칸의 h,w좌표를 나타내는 변수 h_check, w_check <- h + dh[i], w + dw[i]
#       4-2) h_check가 0 이상 n 미만이고 w_check가 0 이상 n 미만이라면 다음을 수행합니다.
#           a) if board[h][w] == board[h_check][w_check]:count+=1
#     5) return count

def solution(board, h, w):
    answer = 0
    n=len(board)
    count=0
    dh=[0,1,-1,0]
    dw=[1,0,0,-1]
    
    for i in range(4):
        h_check=h+dh[i]
        w_check=w+dw[i]
        
        if n>h_check>=0 and 0<=w_check<n:
                if board[h][w]==board[h_check][w_check]:
                    count+=1
    answer = count
    return answer



# ================= [ 테스트 케이스 실행 구문 ] =================
if __name__ == "__main__":
    print("--- 테스트 케이스 실행 결과 ---")
    
    # [테스트 케이스 1]
    board1 = [
        ["blue", "red", "orange", "red"], 
        ["red", "red", "blue", "orange"], 
        ["blue", "orange", "red", "red"], 
        ["orange", "orange", "red", "blue"]
    ]
    h1, w1 = 1, 1
    expected1 = 2
    result1 = solution(board1, h1, w1)
    print(f"케이스 1 결과: {result1} (기대값: {expected1}) -> {'성공' if result1 == expected1 else '실패'}")
    
    # [테스트 케이스 2]
    board2 = [
        ["yellow", "green", "blue"], 
        ["blue", "green", "yellow"], 
        ["yellow", "blue", "blue"]
    ]
    h2, w2 = 0, 1
    expected2 = 1
    result2 = solution(board2, h2, w2)
    print(f"케이스 2 결과: {result2} (기대값: {expected2}) -> {'성공' if result2 == expected2 else '실패'}")