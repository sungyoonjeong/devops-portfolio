"""
어떤 도로에 차량 신호등이 n개 있습니다. 
모든 신호등은 항상 초록불 → 노란불 → 빨간불 순서로 반복되며, 
각 신호의 지속 시간은 신호등마다 다릅니다. 시간은 1초부터 시작하며, 
각 신호등은 처음에는 초록불 상태로 시작합니다.

이 도로에서는 가끔 정전이 일어나는데, 
모든 신호등이 모두 노란불이 되면 정전이 발생한다는 사실이 밝혀졌습니다.

예를 들어 신호등이 2개이고, 
각 신호등의 주기가 다음과 같다고 가정해 보겠습니다.

신호등	초록불	노란불	빨간불
1번	    2초	    1초	    2초
2번	    5초	    1초	    1초

위 그림과 같이 13초에 처음으로 두 신호등이 모두 노란불이 됩니다.

신호등 n개의 신호 주기를 담은 2차원 정수 배열 signals가 매개변수로 주어집니다. 
모든 신호등이 노란불이 되는 가장 빠른 시각(초)을 return 하도록 solution 함수를 완성해 주세요. 
만약 모든 신호등이 노란불이 되는 경우가 존재하지 않는다면 -1을 return 해주세요.
"""

import math

def solution(signals):
    # 1. 모든 신호등 주기의 최소공배수(LCM)를 먼저 구합니다.
    # 이 시간 안에 동시에 노란불이 안 되면 평생 안 되는 것입니다.
    max_limit = 1
    for g, y, r in signals:
        period = g + y + r
        max_limit = (max_limit * period) // math.gcd(max_limit, period)
        #math.gcd:최대공약수
        # max_limit=math.lcm(max_limit,period)
    # 2. 1초부터 최소공배수 시점까지 딱 필요한 만큼만 검사합니다.
    for t in range(1, max_limit + 1):
        all_yellow = True
        
        for g, y, r in signals:
            # 1초부터 시작하는 시간에 맞춘 정확한 나머지 인덱스 계산
            remain = (t - 1) % (g + y + r)
            
            # 노란불 구간은 [초록불 시간 이상]이면서 [초록+노란불 미만]입니다.
            if not (g <= remain < g + y):
                all_yellow = False
                break
                
        # 모든 신호등이 노란불 조건에 맞았다면 바로 그 시간(t)을 리턴합니다.
        if all_yellow:
            return t
            
    # 한계 시간까지 동시에 노란불이 되는 경우가 없었다면 -1을 리턴합니다.
    return -1
