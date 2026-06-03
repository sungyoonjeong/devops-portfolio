"""
유저 목록 id_list와 신고 정보 report("신고한_사람 신고당한_사람"), 그리고 정지 기준 횟수 k가 주어집니다.

한 유저가 동일한 유저를 여러 번 신고한 것은 무조건 1회로 처리합니다.

총 신고 횟수가 k번 이상인 유저는 이용 정지 처리가 됩니다.

각 유저가 내가 신고한 사람 중 정지된 사람이 몇 명인지(받을 메일 수)를 계산하여 id_list 순서대로 배열에 담아 반환해야 합니다.

<알고리즘>
Step 1) 중복 신고를 원천 차단하기 위해 set(report)를 취해 중복 요소를 제거합니다.

Step 2) 유저별로 신고당한 횟수를 기록할 딕셔너리(reported_count)와, 각 유저가 누구를 신고했는지 리스트로 저장할 딕셔너리(user_report_list)를 초기화합니다.

Step 3) 중복이 제거된 신고 기록을 하나씩 순회하며 "공백"을 기준으로 신고자(from)와 피신고자(to)를 분리합니다.

Step 4) 피신고자의 신고당한 횟수를 1 늘리고, 신고자의 신고 목록에 피신고자 이름을 추가합니다.

Step 5) id_list 순서대로 유저를 하나씩 확인하면서, 해당 유저가 신고한 사람들 중 reported_count가 k 이상인 사람이 몇 명인지 세어서 정답 배열에 담아 반환합니다.
"""
def solution(id_list, report, k):
    # 한 유저가 같은 유저를 여러 번 신고한 중복 케이스를 set을 통해 미리 제거합니다.
    report = list(set(report))
    
    # 각 유저별로 '신고당한 횟수'를 0으로 초기화하여 저장할 딕셔너리입니다.
    reported_count = {user: 0 for user in id_list}
    
    # 각 유저별로 '자신이 신고한 유저들의 이름'을 리스트로 모아둘 딕셔너리입니다.
    user_report_list = {user: [] for user in id_list}
    
    # 중복이 제거된 신고 내역을 하나씩 꺼내어 처리합니다.
    for r in report:
        # "muzi frodo" 형태의 문자열을 공백 기준으로 잘라 신고자와 피신고자로 나눕니다.
        reporter, reported = r.split()
        
        # 피신고자의 신고 누적 횟수를 1 증가시킵니다.
        reported_count[reported] += 1
        
        # 신고자가 누구를 신고했는지 기록하기 위해 피신고자 이름을 리스트에 추가합니다.
        user_report_list[reporter].append(reported)
        
    answer = []
    # id_list에 담긴 유저 순서대로 차례대로 메일 점수를 계산합니다.
    for user in id_list:
        mail_count = 0  # 이 유저가 받게 될 메일의 개수입니다.
        
        # 해당 유저가 신고했던 피신고자들을 하나씩 꺼내어 확인합니다.
        for reported in user_report_list[user]:
            # 만약 그 피신고자의 누적 신고 횟수가 k번 이상이라면 (정지 대상이라면)
            if reported_count[reported] >= k:
                mail_count += 1  # 결과 메일 발송 대상으로 카운트합니다.
                
        # 최종 계산된 메일 개수를 결과 리스트에 차례대로 추가합니다.
        answer.append(mail_count)
        
    return answer


# ==========================================
# 🧪 [신고 결과 받기] 테스트 및 검증 코드
# ==========================================
if __name__ == "__main__":
    print("=== [신고 결과 받기] 테스트 시작 ===")
    
    # 테스트 케이스 1 (입출력 예 #1)
    id_list1 = ["muzi", "frodo", "apeach", "neo"]
    report1 = ["muzi frodo","apeach frodo","frodo neo","muzi neo","apeach muzi"]
    k1 = 2
    expected1 = [2, 1, 1, 0]
    result1 = solution(id_list1, report1, k1)
    print(f"\n[테스트 1]")
    print(f"기댓값 〉 {expected1}")
    print(f"실행결과 〉 {result1}")
    print(f"통과여부 〉 {'성공  (수정됨)' if result1 == expected1 else '실패 ❌'}")
    
    # 테스트 케이스 2 (입출력 예 #2 - 중복 신고 조건 확인)
    id_list2 = ["con", "ryan"]
    report2 = ["ryan con", "ryan con", "ryan con", "ryan con"]
    k2 = 3
    expected2 = [0, 0]
    result2 = solution(id_list2, report2, k2)
    print(f"\n[테스트 2]")
    print(f"기댓값 〉 {expected2}")
    print(f"실행결과 〉 {result2}")
    print(f"통과여부 〉 {'성공  (수정됨)' if result2 == expected2 else '실패 ❌'}")

    print("\n==========================================")