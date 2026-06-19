"""
[문제 요약]
- 문자열 s의 길이가 4 혹은 6이고, 숫자로만 구성되어 있는지 확인하는 함수를 완성합니다.
- 조건(길이가 4 또는 6인 동시에 숫자로만 구성)을 만족하면 True, 아니면 False를 반환합니다.

[알고리즘 순서]
1. 결과를 저장할 변수 answer를 기본값 True로 초기화합니다.
2. 문자열 s의 길이가 4 또는 6인지 확인합니다. 만약 둘 다 아니라면 answer를 False로 변경합니다.
3. 문자열 s가 숫자로만 구성되어 있는지 s.isdigit()를 통해 확인합니다. 만약 숫자가 아닌 문자가 섞여 있다면 answer를 False로 변경합니다.
4. 최종 결과인 answer 값을 반환합니다.
"""

def solution(s):
    # 결과를 저장할 변수 초기화
    answer = True
    
    # 1. 문자열의 길이가 4도 아니고 6도 아니라면 False
    if len(s) != 4 and len(s) != 6:
        answer = False
    # 2. 문자열이 숫자로만 이루어져 있지 않다면 False (.isdigit()은 숫자로만 채워져 있으면 True를 반환)
    elif not s.isdigit():
        answer = False
        
    # 최종 결과 반환
    return answer

# --- 테스트 코드 ---
if __name__ == "__main__":
    print("테스트 케이스 1 (s='a234', 기대값=False):", solution("a234"))
    print("테스트 케이스 2 (s='1234', 기대값=True):", solution("1234"))