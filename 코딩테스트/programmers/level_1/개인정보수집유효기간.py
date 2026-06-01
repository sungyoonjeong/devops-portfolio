"""
1~n번으로 분류되는 개인정보 n개가 있음
약관 종류는 여러가지
각 약관마다 개인정보 보관 유효기간 정해져있음
당신은 각 개인정보가 어떤 약관으로 수집됐는지 알고 있음
수집된 개인정보는 유효기간 전까지만 보관 가능
유효기간 지났다면 반드시 파기해야함

오늘 날짜로 파기해야할 개인정보 번호들을 구해야함
모든 달은 28일까지 존재한다고 가정

today : 오늘 날짜 의미하는 문자열
terms : 약관의 유효기간을 담은 1차원 문자열 배열
privacies : 수집된 개인정보의 정보를 담은 1차원 문자열 배열

파기해야할 개인정보의 번호를 오름차순으로 1차원 정수 배열에 담아 return
"""

"""
1. 날짜를 day(일)로 통일
    - 1년 = 12달*28일 = 336일
    - 1달 = 28일
    - YYYY.MM.DD가 주어지면 (YYYY*12*28) + (MM*28) + DD 공식을 이용
    - 단 하나의 정수(일수)로 변경
    - 오늘 날짜 또한 미리 숫자로 변경

2. 약관 딕셔너리 정비
    - terms 배열을 돌면서 각 약관 종류별 유효기간을 달(month)수 * 28 을 해두어, 몇일이 유효한지 딕셔너리에 저장
    
3. 만료 여부 계산
    - privacies를 돌면서 수집일자를 "일" 단위로 변경
    - 해당 약관의 유효일수를 더함

4. 비교 및 판정
    - (수집일 + 유효기간)이 오늘 날짜보다 작거나 같다면 유효기간이 만료된 것이므로 파기대상(정답리스트)에 추가
"""
def solution(today, terms, privacies):
    # 파기해야 할 개인정보 번호를 담을 빈 리스트를 생성합니다.
    answer = []
    
    # "YYYY.MM.DD" 문자열을 받아 전체 '일(Day)' 수로 변환하는 헬퍼 함수를 정의합니다.
    def convert_to_days(date_str):
        # 점(.)을 기준으로 연, 월, 일을 분리하고 각각 정수형으로 변환합니다.
        year, month, day = map(int, date_str.split('.'))
        # 모든 달은 28일까지 있으므로 연도와 월을 일 단위로 환산하여 모두 더합니다.
        return (year * 12 * 28) + (month * 28) + day

    # 오늘 날짜를 총 '일' 수로 변환하여 기준점을 만듭니다.
    today_days = convert_to_days(today)
    
    # 약관 종류와 유효기간(일 단위)을 매핑할 딕셔너리를 생성합니다.
    term_dict = {}
    # terms 배열을 순회하며 약관 이름과 기간을 분리합니다.
    for term in terms:
        kind, period = term.split()
        # 유효기간(달 수)에 28을 곱해 '일' 단위로 변환한 뒤 딕셔너리에 저장합니다.
        term_dict[kind] = int(period) * 28
        
    # privacies 배열을 index와 함께 순회합니다. (정보 번호는 1번부터 시작하므로 i + 1 사용)
    for i, privacy in enumerate(privacies):
        # 1. privacies:
        #    - 문제에서 주어진 개인정보들이 담긴 리스트입니다. 
        #    (예: ["2021.05.02 A", "2021.07.01 B", ...])
        # 2. enumerate(privacies):
        #   - 리스트를 입력받아 (인덱스, 값)의 쌍으로 묶어서 차례대로 반환해 주는 파이썬 내장 함수
        # 3. for i, privacy in ...:
        #   enumerate가 넘겨주는 두 개의 값 중, 앞의 인덱스(번호표)는 변수 i에 담고, 
        #   뒤의 실제 값(개인정보 문자열)은 변수 privacy에 담아 반복문을 실행합니다.
    
        # 수집 일자와 약관 종류를 공백을 기준으로 분리합니다.
        date, kind = privacy.split()
        
        # 수집 일자를 총 '일' 수로 변환합니다.
        collected_days = convert_to_days(date)
        # 수집된 날짜에 해당 약관의 유효 기간(일 수)을 더해 만료일을 구합니다.
        expire_days = collected_days + term_dict[kind]
        
        # 만약 만료일이 오늘 날짜보다 작거나 같다면 이미 유효기간이 지난 것입니다.
        if expire_days <= today_days:
            # 1부터 시작하는 개인정보 번호(인덱스 + 1)를 정답 배열에 추가합니다.
            answer.append(i + 1)
            
    # 파기해야 할 번호들이 담긴 리스트를 반환합니다. (순서대로 순회했으므로 이미 오름차순 정렬 상태)
    return answer

# --- 테스트케이스 실행 코드 ---

test_cases = [
    {
        "today": "2022.05.19",
        "terms": ["A 6", "B 12", "C 3"],
        "privacies": ["2021.05.02 A", "2021.07.01 B", "2022.02.19 C", "2022.02.20 C"],
        "expected": [1, 3]
    },
    {
        "today": "2020.01.01",
        "terms": ["Z 3", "D 5"],
        "privacies": ["2019.01.01 D", "2019.11.15 Z", "2019.08.02 D", "2019.07.01 D", "2018.12.28 Z"],
        "expected": [1, 4, 5]
    }
]

for i, case in enumerate(test_cases, 1):
    result = solution(case["today"], case["terms"], case["privacies"])
    is_success = result == case["expected"]
    
    print(f"== 테스트 케이스 {i} ==")
    print(f"오늘 날짜(today) : {case['today']}")
    print(f"기댓값(expected) : {case['expected']}")
    print(f"실행결과(result) : {result}")
    print(f"결과: {'정답 (Pass)' if is_success else '오답 (Fail)'}")
    print("-" * 30)