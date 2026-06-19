"""
[문제 요약]
- String형 배열 seoul의 원소 중 "Kim"의 위치(인덱스) x를 찾습니다.
- 찾아낸 위치를 포함하여 "김서방은 x에 있다"라는 문자열을 반환하는 함수를 완성합니다.

[알고리즘 순서]
1. 결과를 담을 변수 answer를 초기화합니다.
2. enumerate()를 사용해 seoul 배열의 인덱스(idx)와 이름(name)을 동시에 꺼내며 반복합니다.
3. 만약 현재 이름(name)이 "Kim"과 일치한다면, f-string을 이용해 결과 문자열을 만들어 answer에 저장합니다.
4. "Kim"을 찾았으므로 더 이상 반복할 필요 없이 break로 반복문을 탈출합니다.
5. 최종적으로 answer 값을 반환합니다.
"""

def solution(seoul):
    # 결과를 저장할 변수 초기화
    answer = ''
    
    # 배열의 인덱스(idx)와 원소(name)를 동시에 꺼내며 순회
    for idx, name in enumerate(seoul):
        # 만약 현재 원소가 "Kim"이라면
        if name == "Kim":
            # answer 변수에 형식에 맞는 문자열을 저장
            answer = f"김서방은 {idx}에 있다"
            # "Kim"은 오직 한 번만 나타나므로 찾았으면 반복문 탈출
            break
            
    # 최종 결과 반환
    return answer

# --- 테스트 코드 ---
if __name__ == "__main__":
    print("테스트 케이스 1 (기대값: '김서방은 1에 있다'):", solution(["Jane", "Kim"]))