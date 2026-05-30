"""
문제 설명
당신은 동영상 재생기를 만들고 있습니다. 
당신의 동영상 재생기는 10초 전으로 이동, 10초 후로 이동, 오프닝 건너뛰기 3가지 기능을 지원합니다. 
 기능
    1) 10초전 이동 : prev 명령 입력시, 재생위치에서 10초전으로 이동(현위지 10초 미만인 경우 영상 처음위치로 이동 0m0s)
    2) 10초후 이동 : next 명령 입력시, 재생위치에서 10초후로 이동(남은시간이 10초미만일 경우 영상마지막위치=동영상 길이)
    3) 오프닝 건너뛰기 : 현위치가 오프닝구간(op_start<=현위치<=op_end)인 경우 오프닝 끝나는 위치로 이동
    
    video_len : 동영상 길이 문자열 (mm:ss) 34:33
    pos : 기능 수행직전 현위치 (mm:ss)     13:00
    op_start : 오프닝 시작 시각 (mm:ss)    00:55
    op_end : 오프닝 끝 시각 (mm:ss)        02:55
    commands : 사용자 입력 명령어           ["next","prev"]
    
    입력 후 동영상위치 "mm:ss"형식으로 return
    
    video_len의 길이=pos의 길이=op_start의 길이=op_end의 길이=5
    => 무조건 5글자
"""

def solution(video_len, pos, op_start, op_end, commands):
    
    # [내부 함수 지정] "mm:ss" 형태의 문자열을 받아서 총 '초'로 변환해 주는 기계입니다.
    def to_seconds(time_str):
        # 콜론(:)을 기준으로 분과 초를 나눠서 정수(int) 숫자로 바꿉니다. (위의 1번 설명)
        m, s = map(int, time_str.split(':'))
        # 1분은 60초이므로 (분 * 60)을 한 뒤 초를 더해 총 '초'를 구합니다.
        return m * 60 + s

    # 매개변수로 받은 모든 시간 데이터를 계산하기 편하게 '초' 단위 숫자로 전부 바꿉니다.
    video_limit = to_seconds(video_len) # 동영상의 전체 길이 (초)
    current = to_seconds(pos)           # 사용자의 현재 재생 위치 (초)
    start_op = to_seconds(op_start)     # 오프닝이 시작하는 시각 (초)
    end_op = to_seconds(op_end)         # 오프닝이 끝나는 시각 (초)

    # [예외 처리 1] 영상을 켜자마자 현재 위치가 오프닝 구간 안에 있는지 확인합니다.
    if start_op <= current <= end_op:
        current = end_op # 오프닝 구간 안이라면 오프닝 끝나는 위치로 강제 이동합니다.

    # 사용자가 입력한 명령어 배열(commands)에서 명령을 하나씩 꺼내어 반복 수행합니다.
    for cmd in commands:
        
        # 10초 후로 이동하는 명령어인 경우
        if cmd == "next":
            current += 10 # 현재 시간에 10초를 더합니다.
            if current > video_limit:  # 만약 더한 시간이 동영상 전체 길이를 초과했다면
                current = video_limit  # 동영상의 마지막 위치로 고정합니다.
                
        # 10초 전으로 이동하는 명령어인 경우
        elif cmd == "prev":
            current -= 10 # 현재 시간에서 10초를 뺍니다.
            if current < 0:            # 만약 뺀 시간이 0초보다 작아졌다면 (음수가 되었다면)
                current = 0            # 영상의 처음 위치인 0초로 고정합니다.
        
        # [예외 처리 2] 명령어를 수행해 시간을 이동한 직후, 또 오프닝 구간에 들어왔는지 매번 확인합니다.
        if start_op <= current <= end_op:
            current = end_op # 이동한 곳이 오프닝 구간 안이라면 오프닝 끝나는 위치로 다시 이동합니다.

    # 모든 명령어 반복 처리가 완료된 후, 결과를 "mm:ss" 형태로 되돌릴 준비를 합니다.
    # 최종 초 단위를 60으로 나눈 '목'이 '분'이 됩니다. (예: 785 // 60 = 13)
    # 정수를 str()로 문자로 바꾼 뒤, zfill(2)로 2자리를 맞춰줍니다.
    min_str = str(current // 60).zfill(2)
    
    # 최종 초 단위를 60으로 나눈 '나머지'가 '초'가 됩니다. (예: 785 % 60 = 5)
    # 마찬가지로 문자로 바꾼 뒤 zfill(2)로 2자리를 맞춰줍니다.
    sec_str = str(current % 60).zfill(2)
    
    # 문제에서 요구한 대로 "분:초" 형태로 포맷팅하여 최종 반환합니다. (예: "13:05")
    return f"{min_str}:{sec_str}"




# 위쪽에 solution 함수 코드가 있다고 가정합니다.

# 테스트 케이스 데이터 선언 (보내주신 이미지의 표 내용)
test_cases = [
    {
        "video_len": "34:33",
        "pos": "13:00",
        "op_start": "00:55",
        "op_end": "02:55",
        "commands": ["next", "prev"],
        "expected": "13:00"
    },
    {
        "video_len": "10:55",
        "pos": "00:05",
        "op_start": "00:15",
        "op_end": "06:55",
        "commands": ["prev", "next", "next"],
        "expected": "06:55"
    },
    {
        "video_len": "07:22",
        "pos": "04:05",
        "op_start": "00:15",
        "op_end": "04:07",
        "commands": ["next"],
        "expected": "04:17"
    }
]

# 반복문을 돌며 작성한 함수 검증
for i, tc in enumerate(test_cases, 1):
    result = solution(tc["video_len"], tc["pos"], tc["op_start"], tc["op_end"], tc["commands"])
    
    print(f"--- 테스트 케이스 {i} ---")
    print(f"입력 명령어: {tc['commands']}")
    print(f"실행 결과:   {result}")
    print(f"기대 정답:   {tc['expected']}")
    
    if result == tc["expected"]:
        print("결과:        ✅ 통과 (PASS)")
    else:
        print("결과:        ❌ 실패 (FAIL)")
    print()

