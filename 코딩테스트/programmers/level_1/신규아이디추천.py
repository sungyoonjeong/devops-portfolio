"""
새로 가입하는 유저들이 카카오 아이디 규칙에 맞지 않는 아이디를 입력하면
입력된 아이디와 유사하면서 규칙에 맞는 아이디 추천해주는 프로그램

규칙
1) 아이디의 길이는 3자 이상 ~ 15자 이하
2) 아이디는 알파벳 소문자,숫자,빼기(-),밑줄(_),마침표(.) 문자만 사용 가능
3) 단 마침표(.)는 처음과 끝에 사용할 수 없으며, 연속으로 사용할 수 없다

new_id : 신규 유저가 입력한 id
1단계 new_id의 모든 대문자를 대응되는 소문자로 치환합니다.
2단계 new_id에서 알파벳 소문자, 숫자, 빼기(-), 밑줄(_), 마침표(.)를 제외한 모든 문자를 제거합니다.
3단계 new_id에서 마침표(.)가 2번 이상 연속된 부분을 하나의 마침표(.)로 치환합니다.
4단계 new_id에서 마침표(.)가 처음이나 끝에 위치한다면 제거합니다.
5단계 new_id가 빈 문자열이라면, new_id에 "a"를 대입합니다.
6단계 new_id의 길이가 16자 이상이면, new_id의 첫 15개의 문자를 제외한 나머지 문자들을 모두 제거합니다.
     만약 제거 후 마침표(.)가 new_id의 끝에 위치한다면 끝에 위치한 마침표(.) 문자를 제거합니다.
7단계 new_id의 길이가 2자 이하라면, new_id의 마지막 문자를 new_id의 길이가 3이 될 때까지 반복해서 끝에 붙입니다.

"""
def solution(new_id):
    # 1단계: 모든 대문자를 소문자로 치환합니다.
    new_id = new_id.lower()
    
    # 2단계: 알파벳 소문자, 숫자, 빼기(-), 밑줄(_), 마침표(.)를 제외한 모든 문자를 제거합니다.
    # char.isalnum() : char에 담긴 문자가 알파벳이거나 숫자인지 확인
    # char in [...] : char에 담긴 문자가 지정한 리스트 [...] 안에 포함되어있는지 확인
    answer = ""
    for char in new_id:
        if char.isalnum() or char in ['-', '_', '.']:
            answer += char
            
    # 3단계: 마침표(.)가 2번 이상 연속된 부분을 하나의 마침표(.)로 치환합니다.
    while '..' in answer:
        answer = answer.replace('..', '.')
        
    # 4단계: 마침표(.)가 처음이나 끝에 위치한다면 제거합니다.
    if answer.startswith('.'):
        answer = answer[1:]
    if answer.endswith('.'):
        answer = answer[:-1]
        
    # 5단계: 빈 문자열이라면, "a"를 대입합니다.
    if answer == "":
        answer = "a"
        
    # 6단계: 길이가 16자 이상이면, 첫 15개 문자를 제외한 나머지를 제거하고 끝의 마침표도 제거합니다.
    if len(answer) >= 16:
        answer = answer[:15]
        if answer.endswith('.'):
            answer = answer[:-1]
            
    # 7단계: 길이가 2자 이하라면, 길이가 3이 될 때까지 마지막 문자를 반복해서 끝에 붙입니다.
    while len(answer) <= 2:
        answer += answer[-1]
        
    return answer

# --- 테스트 실행 함수 ---
def run_tests():
    # 프로그래머스 예제 1~5번 데이터: (입력값, 기대하는 정답)
    test_cases = [
        ("...!@BaT#*..y.abcdefghijklm", "bat.y.abcdefghi"),
        ("z-+.^.", "z--"),
        ("=.=", "aaa"),
        ("123_.def", "123_.def"),
        ("abcdefghijklmn.p", "abcdefghijklmn")
    ]
    
    print("========== 테스트 시작 ==========")
    for idx, (new_id, expected) in enumerate(test_cases, 1):
        result = solution(new_id)
        is_success = "통과" if result == expected else "실패"
        print(f"테스트 {idx}: 결과 '{result}' / 기대값 '{expected}' -> [{is_success}]")
    print("========== 테스트 종료 ==========")

# 테스트 함수 호출
run_tests()