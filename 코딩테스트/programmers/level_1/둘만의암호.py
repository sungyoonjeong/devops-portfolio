"""
두 문자열 s, skip
자연수 index

규칙1) 문자열 s의 각 알파벳을 index만큼 뒤의 알파벳으로 바꿔줌
규칙2) index 만큼의 뒤의 알파벳이 z를 넘어갈 경우 다시 a로 돌아감
규칙3) skip에 있는 알파벳은 제외하고 건너뜀

예) s= "aukks", skip = "wbqd", index = 5일때,
a에서 5만큼 뒤에 있는 알파벳은 f [b,c,d,e,f]에서 'b'와 'd'는 skip에 포함되므로
세지않는다. 따라서 'b','d'를 제외하고, 5만큼 뒤에 있는 알파벳은 [c,e,f,g,h]순서에 의해 h가 됨.
나머지 "ukks"또한 위 규칙대로 바꾸면 "appy"가 되며 happy가 출력됨

두 문자열 s와 skip, 그리고 자연수 index가 매개변수로 주어질때,
위 규칙대로 s를 변환한 결과를 return
"""
"""
1. 사용가능한 알파벳 배열 만들기
    - 전체 알파벳 a부터 z까지 중에서 skip에 포함되지 않은 문자들만 골라내어 순서대로 리스트(available.alpha)에 담는다.
2. 인덱스 초과 처리 
    - 알파벳이 z를 넘어가는 경우 a로 다시 돌아감.
    - skip을 제외한 우리만의 알파벳 리스트를 만들어두었음
    - 뒤로 이동한 인덱스가 리스트의 길이를 벗어나면 나머지 연산자(%)를 이용해 다시 처음으로 순환하게 만듬
3. 변환 및 합산 
    - s의 각 글자를 순회하면서 해당 글자가 available.alpha에서 몇번쨰 인덱스에 있는지 찾고, 거기에 index를 더한 뒤 리스트의 길이로 나눈 나머지 위치의 문자를 가져와 answer에 더해줌
"""

def solution(s, skip, index):
    # 최종 암호화된 문자열을 저장할 변수를 초기화합니다.
    answer = ''
    
    # 'a'부터 'z'까지의 알파벳 중 skip에 포함되지 않은 문자만 골라 리스트를 만듭니다.
    # ord('a')는 97, ord('z')는 122이므로 chr()을 통해 'a'~'z' 문자를 생성합니다.
    available_alpha = [chr(i) for i in range(ord('a'), ord('z') + 1) if chr(i) not in skip]
    # 1. ord()와 chr(): 문자를 숫자로, 숫자를 문자로 바꾸기
    # 컴퓨터는 내부적으로 문자도 숫자로 기억합니다. (이를 아스키코드/유니코드라고 합니다.)
    # ord('a'): 문자 'a'의 고유 숫자 번호를 가져옵니다. 값은 97입니다.
    # ord('z'): 문자 'z'의 고유 숫자 번호를 가져옵니다. 값은 122입니다.
    # chr(숫자): 숫자를 다시 문자로 되돌려줍니다. 예를 들어 chr(97)은 다시 'a'가 됩니다.
    # 즉, range(ord('a'), ord('z') + 1)은 range(97, 123)이 되어 97부터 122까지의 숫자 연속(즉, a부터 z까지의 숫자들)을 의미하게 됩니다.

    # 2. if chr(i) not in skip: 건너뛸 글자 필터링하기
    # range에 의해 i라는 변수에 97, 98, 99... 같은 숫자가 차례대로 들어옵니다.
    # chr(i)를 통해 이 숫자들을 다시 'a', 'b', 'c' 같은 문자로 바꿉니다.
    # if chr(i) not in skip: "그렇게 바꾼 문자가 skip 문자열 안에 포함되어 있지 않을 때만!"이라는 조건문입니다.
    # 만약 skip = "wbqd"라면, i가 'b'(98)일 때는 조건문이 거짓(False)이 되어 탈락시킵니다.
    
    # 아래 코드와 같은 내용
    # available_alpha = []
    # for i in range(97, 123):           # a(97)부터 z(122)까지 반복
    #     char = chr(i)                  # 숫자를 문자로 변환 ('a', 'b', 'c'...)
    #     if char not in skip:           # 만약 그 문자가 skip에 없다면
    #         available_alpha.append(char) # 리스트에 추가
    
    
    
    # skip이 제외된 알파벳 리스트의 총 길이를 구합니다. (인덱스 순환에 사용)
    length = len(available_alpha)
    
    # 변환할 문자열 s의 각 글자를 하나씩 꺼내어 순회합니다.
    for char in s:
        # 현재 글자가 skip을 제외한 알파벳 리스트에서 몇 번째 인덱스에 있는지 찾습니다.
        current_idx = available_alpha.index(char)
        
        # 현재 인덱스에서 주어진 index만큼 뒤로 이동한 새 인덱스를 구합니다.
        # 이때 리스트의 길이를 넘어가면 처음으로 돌아가도록 나머지 연산(%)을 해줍니다.
        new_idx = (current_idx + index) % length
        
        # 새 인덱스 위치에 있는 알파벳을 결과 문자열에 추가합니다.
        answer += available_alpha[new_idx]
        
    # 완성된 암호 문자열을 반환합니다.
    return answer