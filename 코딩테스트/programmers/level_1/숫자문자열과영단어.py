"""
숫자의 일부 자릿수가 영단어(ex: "one","two")로 바뀐 문자열 s가 주어짐
영단어로 바뀐 부분을 원래의 숫자로 모두 바꾸어 정수(int)형태로 반환
ex) "one4seveneight" => 1478

<알고리즘>
1) 0~9까지의 영단어를 순서대로 담은 리스트 생성
    - 인덱스 번호가 곧 해당 숫자가 되도록 ["zero","one","two",...] 순서로
2) 반복문을 통해 0~9까지 순회하면서 문자열 s에 포함된 영단어를 대응되는 숫자 문자열로 변경
    - s.replace("one","1")
3) 모든 영단어가 숫자로 바뀌면, 최종 문자열을 int()를 이용해 정수로 변환
"""
def solution(s):
    answer = 0
    # 0부터 9까지의 영단어를 인덱스 번호에 맞게 리스트로 정의
    words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    
    # 0부터 9까지 반복하며 문자열 내의 영단어를 숫자로 치환
    for i in range(10):
        # s 내에 있는 words[i](예: "zero")를 숫자 문자열 str(i)(예: "0")로 변경
        s = s.replace(words[i], str(i))
        
    # 최종 치환된 문자열을 정수형(int)으로 변환하여 반환
    return int(s)

# <한줄풀이>
# def solution(s):
#     # enumerate를 활용해 단어와 숫자를 동시에 순회하며 s를 갱신 (숏코딩 스타일)
#     for i, word in enumerate(["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]): s = s.replace(word, str(i))
#     return int(s)

# 설명
# 1. enumerate()의 마법: 번호와 단어를 동시에!
# 보통 영단어를 숫자로 바꾸려면 단어 리스트와 숫자 리스트가 둘 다 필요하다고 생각하기 쉽습니다. 하지만 enumerate()를 사용하면 리스트의 인덱스 번호가 곧 매칭되는 숫자가 됩니다.

# enumerate(["zero", "one", ...])를 실행하면 컴퓨터는 내부적으로 (0, "zero"), (1, "one"), (2, "two") 형태로 묶어서 한 쌍씩 꺼내줍니다.

# 덕분에 i에는 숫자(정수), word에는 영단어가 매끄럽게 담겨 단 한 줄로 순회가 가능해집니다.

# 2. 파이썬 줄 바꿈 생략 규칙
# 파이썬에서는 for문이나 if문 다음에 오는 실행 코드가 딱 한 줄짜리 명령문일 경우, 줄을 바꾸지 않고 콜론(:) 바로 오른쪽에 붙여 쓸 수 있습니다.

# 3. s = s.replace(...) 연속 치환의 흐름루프가 돌면서 문자열 s는 다음과 같이 실시간으로 변합니다. (입력값이 "one4seveneight" 일 때)
#     - i=1, word="one" $\rightarrow$ "14seveneight" (s 갱신)
#     -i=7, word="seven" $\rightarrow$ "147eight" (s 또 갱신)
#     - i=8, word="eight" $\rightarrow$ "1478" (s 최종 갱신)
    
    
# 테스트 실행 함수
def test_solution():
    print("=== 숫자 문자열과 영단어 테스트 시작 ===")
    
    # 테스트 케이스 1
    assert solution("one4seveneight") == 1478, f"실패: TC1 결과 {solution('one4seveneight')}"
    print("테스트 1 통과! (기댓값: 1478)")
    
    # 테스트 케이스 2
    assert solution("23four5six7") == 234567, f"실패: TC2 결과 {solution('23four5six7')}"
    print("테스트 2 통과! (기댓값: 234567)")
    
    # 테스트 케이스 3
    assert solution("2three45sixseven") == 234567, f"실패: TC3 결과 {solution('2three45sixseven')}"
    print("테스트 3 통과! (기댓값: 234567)")
    
    # 테스트 케이스 4 (영단어가 없는 경우)
    assert solution("123") == 123, f"실패: TC4 결과 {solution('123')}"
    print("테스트 4 통과! (기댓값: 123)")
    
    print("=== 모든 테스트를 성공적으로 통과했습니다! ===")

# 테스트 실행
test_solution()