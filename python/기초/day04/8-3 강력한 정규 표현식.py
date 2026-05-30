"""
1. 문자열 소비가 없는 메타 문자
    1) | : or
    2) ^ : 문자열의 맨 처음과 일치하다는 것을 의미 (각줄)
    3) $ : 문자열의 끝과 매치한다는 것을 의미(각줄)
    4) \A : 문자열의 맨 처음과 일치하다는 것을 의미 (전체 문자열)
    5) \Z : 문자열의 끝과 매치한다는 것을 의미(전체 문자열)
    6) \b : 단어 구분자 (사용시에는 r'\bclass\b' 로 사용; \b : 백스페이스를 의미하므로)
    7) \B : \b의 반대경우(화이트 스페이스로 구분된 단어가 아닌 경우)

2. 그루핑
    1) 여러문자를 하나로 묶어서 반복처리하기 위함
    2) 매치된 문자열에서 원하는 부분만 추출

    - 여러 문자를 하나로 묶어서 반복 처리하기
        >>> p = re.compile('(ABC)+')
        >>> m = p.search('ABCABCABC OK?')
        >>> print(m)
        <re.Match object; span=(0, 9), match='ABCABCABC'>
        >>> print(m.group())
        ABCABCABC

    - 매치된 문자열에서 원하는 부분만 추출하기    
        >>> p = re.compile(r"(\w+)\s+\d+[-]\d+[-]\d+")
        >>> m = p.search("park 010-1234-1234")
        >>> print(m.group(1))
        park

        \w+\s+\d+[-]\d+[-]\d+은 이름 + 공백 + 전화번호
        이름에 해당하는 \w+ 부분을 (\w+)과 같이 그룹으로 만들면 match 객체의 group(인덱스) 메서드를 사용하여 그루핑된 부분의 문자열만 뽑아낼 수 있다
        group(0)	매치된 전체 문자열 (group()과 동일)
        group(1)	첫 번째 그룹에 해당하는 문자열
        group(2)	두 번째 그룹에 해당하는 문자열
        group(n)	n 번째 그룹에 해당하는 문자열

    - 그루핑된 문자열 재참조 하기
    - 그루핑된 문자열에 이름 붙이기

3. 전방탐색
    1) 긍정형 전방탐색
        (?=...): "뒤에 ...가 오는지 확인하되, 실제로는 포함하지 않기"
    2) 부정형 전방탐색
        (?!...): "뒤에 ...가 오지 않는지 확인하되, 실제로는 포함하지 않기"
        .*[.](?!bat$|exe$).*$ : bat, exe 파일 제외

4. 문자열 바꾸기 
    sub 메서드를 사용:정규식과 매치되는 부분을 다른 문자로 쉽게 바꿀 수 있다
        >>> p = re.compile('(blue|white|red)')
        >>> p.sub('colour', 'blue socks and red shoes')
        'colour socks and colour shoes'

        첫 번째 인수는 "바꿀 문자열(replacement)"
        두 번째 인수는 "대상 문자열"


        >>> p.sub('colour', 'blue socks and red shoes', count=1)
        'colour socks and red shoes'
        #한번만 바꿀때 count=1을 사용

    1) sub 메서드 사용 시 참조 구문 사용하기
    2) sub 메서드의 매개변수로 함수 넣기

5. greedy와 non-greedy
    
    """