# ============================================================
# log_analyzer.py 핵심 기능
# monitor.py가 생성한 monitor.log를 읽어서:
#   ① 전체 로그 통계 (정상·경고·에러 건수)
#   ② 최근 경고·에러 내역 출력
#   ③ 어떤 지표가 가장 많이 초과됐는지 분석
#   ④ 분석 결과를 report.txt로 저장
# ============================================================


# ── 모듈 불러오기 ────────────────────────────────────────────

import re        # 정규식 모듈 - 문자열에서 특정 패턴(숫자 등) 찾을 때 사용
import os        # 운영체제 기능 - 파일 존재 확인, 파일 수정 시간 확인에 사용
import time      # 시간 관련 - time.sleep()으로 일정 시간 대기할 때 사용
from datetime import datetime      # 현재 날짜·시간 가져올 때 사용
from collections import Counter    # 요소 개수 세는 도구 (현재는 미사용, 확장 여지)


# ── 설정값 ───────────────────────────────────────────────────

LOG_FILE       = 'monitor.log'  # 분석할 로그 파일 이름 (monitor.py가 생성)
REPORT_FILE    = 'report.txt'   # 분석 결과를 저장할 파일 이름
CHECK_INTERVAL = 10             # 몇 초마다 로그 파일 변경을 확인할지 (10초)


# ── 함수 1: 로그 파일 읽기 ────────────────────────────────────

def read_log(filepath):
    # filepath: 읽을 파일 경로 (예: 'monitor.log')

    if not os.path.exists(filepath):
        # os.path.exists(): 해당 경로에 파일이 있는지 확인
        # not = 파일이 없으면 아래 실행
        print(f"❌ 로그 파일 없음: {filepath}")
        return []  # 빈 리스트 반환 → 호출한 쪽에서 빈 값으로 처리

    with open(filepath, 'r', encoding='utf-8') as f:
        # open(): 파일 열기
        # 'r' = 읽기 모드 (read)
        # encoding='utf-8' = 한글 깨짐 방지
        # with 구문: 파일 작업 끝나면 자동으로 닫힘
        lines = f.readlines()
        # readlines(): 파일 전체를 읽어서 줄 단위 리스트로 반환
        # 예: ["2026-06-03 [INFO] 정상\n", "2026-06-03 [WARNING] CPU\n"]

    return [l.strip() for l in lines if l.strip()]
    # 리스트 컴프리헨션: lines의 각 줄(l)에 대해
    # l.strip() = 앞뒤 공백·줄바꿈(\n) 제거
    # if l.strip() = 빈 줄은 제외
    # 결과: 공백 제거된 줄들의 리스트


# ── 함수 2: 로그 레벨별 분류 ─────────────────────────────────

def classify_logs(lines):
    # lines: read_log()가 반환한 줄 리스트

    info     = [l for l in lines if '[INFO]'    in l]
    # [INFO] 가 포함된 줄만 추출 → 정상 로그
    # in = 문자열 포함 여부 확인 (Python의 in 연산자)

    warnings = [l for l in lines if '[WARNING]' in l]
    # [WARNING] 이 포함된 줄만 추출 → 경고 로그

    errors   = [l for l in lines if '[ERROR]'   in l]
    # [ERROR] 가 포함된 줄만 추출 → 에러 로그

    return info, warnings, errors
    # 세 개의 리스트를 동시에 반환 (다중 반환값)


# ── 함수 3: 경고 패턴 분석 ───────────────────────────────────

def analyze_warnings(warnings):
    # warnings: classify_logs()에서 추출한 경고 로그 리스트

    cpu_count  = sum(1 for w in warnings if 'CPU'    in w)
    # warnings의 각 줄(w)에서 'CPU' 가 포함된 줄 개수 합산
    # sum(1 for ...) = 조건에 맞는 항목마다 1을 더함
    # = CPU 관련 경고가 몇 번 발생했는지

    mem_count  = sum(1 for w in warnings if '메모리' in w)
    # 메모리 관련 경고 횟수

    disk_count = sum(1 for w in warnings if '디스크' in w)
    # 디스크 관련 경고 횟수

    return {'CPU': cpu_count, '메모리': mem_count, '디스크': disk_count}
    # 딕셔너리로 반환 → {'CPU': 3, '메모리': 1, '디스크': 0}


# ── 함수 4: 수치 추출 ────────────────────────────────────────

def extract_metrics(info_lines):
    # info_lines: INFO 로그 줄들
    # 목적: "정상 | CPU: 12.3% | 메모리: 26.3% | 디스크: 0.6%" 에서 숫자만 추출

    cpu_vals, mem_vals, disk_vals = [], [], []
    # 각 지표의 수치를 담을 빈 리스트 3개 동시 선언

    for line in info_lines:
        # 모든 INFO 줄을 하나씩 확인

        if '정상' in line and 'CPU' in line:
            # '정상'과 'CPU' 모두 포함된 줄만 처리
            # = 실제 수치가 담긴 줄 (시작 로그, 구분선 등 제외)

            try:
                # try: 파싱 실패해도 프로그램 안 멈추도록 감싸기

                cpu  = float(re.search(r'CPU: ([\d.]+)%',   line).group(1))
                # re.search(패턴, 문자열): 문자열에서 패턴 찾기
                # r'CPU: ([\d.]+)%' = 정규식 패턴
                #   CPU:      → 'CPU: ' 문자 그대로 찾기
                #   ([\d.]+)  → 숫자(0-9)와 점(.)으로 이루어진 그룹 캡처
                #   %         → '%' 문자
                # .group(1)  → 첫 번째 캡처 그룹 = 숫자 부분만 추출
                # float()    → 문자열 "12.3" → 실수 12.3으로 변환

                mem  = float(re.search(r'메모리: ([\d.]+)%', line).group(1))
                # 메모리 수치 추출 (같은 방식)

                disk = float(re.search(r'디스크: ([\d.]+)%', line).group(1))
                # 디스크 수치 추출 (같은 방식)

                cpu_vals.append(cpu)    # 추출한 CPU 수치를 리스트에 추가
                mem_vals.append(mem)    # 메모리 수치 추가
                disk_vals.append(disk)  # 디스크 수치 추가

            except (AttributeError, ValueError):
                # AttributeError: re.search()가 None 반환 시 .group(1) 호출 불가
                # ValueError: float() 변환 실패 시
                continue
                # continue: 이 줄 건너뛰고 다음 줄로

    return cpu_vals, mem_vals, disk_vals
    # 수치 리스트 3개 반환
    # 예: [12.3, 15.1, 8.4], [26.3, 27.1, 25.9], [0.6, 0.6, 0.7]


# ── 함수 5: 리포트 생성 ──────────────────────────────────────

def generate_report(lines, info, warnings, errors, pattern, cpu_vals, mem_vals, disk_vals):
    # 모든 분석 결과를 받아서 보기 좋은 리포트 문자열 생성

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # datetime.now(): 현재 날짜·시간 객체
    # .strftime("형식"): 원하는 형식의 문자열로 변환
    # 결과: "2026-06-03 14:35:00"

    avg_cpu  = sum(cpu_vals)  / len(cpu_vals)  if cpu_vals  else 0
    # if cpu_vals: 리스트에 값이 있으면 평균 계산
    # else 0: 비어있으면 0 (ZeroDivisionError 방지)
    # sum() / len() = 평균 계산

    avg_mem  = sum(mem_vals)  / len(mem_vals)  if mem_vals  else 0
    avg_disk = sum(disk_vals) / len(disk_vals) if disk_vals else 0

    report = f"""
========================================
  서버 모니터링 로그 분석 리포트
  생성일시: {now}
========================================

[ 전체 통계 ]
  총 로그 라인: {len(lines)}줄
  정상 (INFO):  {len(info)}건
  경고 (WARN):  {len(warnings)}건
  에러 (ERROR): {len(errors)}건

[ 평균 수치 ]
  CPU 평균:    {avg_cpu:.1f}%
  메모리 평균: {avg_mem:.1f}%
  디스크 평균: {avg_disk:.1f}%

[ 경고 패턴 분석 ]
  CPU 초과:    {pattern['CPU']}회
  메모리 초과: {pattern['메모리']}회
  디스크 초과: {pattern['디스크']}회
"""
    # f"""...""" = 여러 줄 f-string
    # {변수} = 변수 값을 문자열 안에 삽입
    # {avg_cpu:.1f} = 소수점 첫째 자리까지만 표시

    if warnings:
        # warnings 리스트가 비어있지 않으면 (경고가 있으면)
        report += "\n[ 최근 경고 내역 ]\n"
        # += : 기존 report 문자열에 새 문자열 이어붙이기
        for w in warnings[-3:]:
            # warnings[-3:] = 리스트의 마지막 3개만 (최근 3건)
            report += f"  {w}\n"
    else:
        report += "\n[ 최근 경고 내역 ]\n  없음\n"

    if errors:
        report += "\n[ 최근 에러 내역 ]\n"
        for e in errors[-3:]:
            report += f"  {e}\n"
    else:
        report += "\n[ 최근 에러 내역 ]\n  없음\n"

    report += "\n========================================"
    return report  # 완성된 리포트 문자열 반환


# ── 함수 6: 한 번 분석 실행 ──────────────────────────────────

def analyze_once():
    """한 번 분석 실행 - main()의 while 루프에서 반복 호출됨"""

    lines = read_log(LOG_FILE)   # 로그 파일 읽기
    if not lines:
        return   # 파일이 없거나 비어있으면 함수 종료

    info, warnings, errors        = classify_logs(lines)
    # 로그를 INFO·WARNING·ERROR로 분류
    # 세 변수에 동시에 결과 저장 (다중 할당)

    pattern                       = analyze_warnings(warnings)
    # 경고에서 어떤 지표가 몇 번 초과됐는지 분석

    cpu_vals, mem_vals, disk_vals = extract_metrics(info)
    # INFO 로그에서 수치 추출

    report = generate_report(
        lines, info, warnings, errors,
        pattern, cpu_vals, mem_vals, disk_vals
    )
    # 모든 분석 결과로 리포트 문자열 생성

    print(report)   # 터미널에 출력

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    # 'w' = 쓰기 모드 (write) → 기존 내용 덮어쓰기
    # 매번 최신 리포트로 갱신됨

    print(f"✅ 리포트 업데이트: {REPORT_FILE}")


# ── 함수 7: 메인 실행 (자동 반복) ────────────────────────────

def main():
    print("📊 로그 분석기 시작")
    print(f"   대상 파일: {LOG_FILE}")
    print(f"   확인 주기: {CHECK_INTERVAL}초")
    print("   Ctrl+C 로 종료\n")

    last_modified = 0
    # 마지막으로 확인한 파일 수정 시간을 기억하는 변수
    # 0으로 초기화 → 처음 실행 시 반드시 분석 실행됨

    while True:
        # 무한 루프 → Ctrl+C로만 종료
        try:
            # try: 루프 실행 중 KeyboardInterrupt(Ctrl+C) 감지

            if os.path.exists(LOG_FILE):
                # 로그 파일이 존재하는지 확인

                current_modified = os.path.getmtime(LOG_FILE)
                # os.path.getmtime(): 파일의 마지막 수정 시간 반환
                # 숫자(타임스탬프)로 반환: 예) 1748920235.123

                if current_modified != last_modified:
                    # 현재 수정 시간 ≠ 마지막 확인 수정 시간
                    # = 파일이 변경됐다는 뜻

                    print(f"\n🔄 로그 변경 감지 → 재분석 중...")
                    analyze_once()              # 분석 실행
                    last_modified = current_modified
                    # 현재 수정 시간을 기억해둠 → 다음 비교에 사용

                else:
                    # 수정 시간이 같으면 = 파일 변경 없음
                    now = datetime.now().strftime("%H:%M:%S")
                    print(f"[{now}] 변경 없음 — {CHECK_INTERVAL}초 후 재확인", end='\r')
                    # end='\r' = 줄바꿈 대신 커서를 줄 맨 앞으로
                    # → 같은 줄을 계속 덮어씀 (깔끔한 대기 표시)

            else:
                print(f"⏳ {LOG_FILE} 대기 중...", end='\r')
                # 파일 없으면 대기 중 표시

            time.sleep(CHECK_INTERVAL)
            # CHECK_INTERVAL초(10초) 동안 대기
            # 대기 후 while 처음으로 돌아가서 다시 확인

        except KeyboardInterrupt:
            # Ctrl+C 누르면 여기로 점프
            print("\n\n🛑 로그 분석기 종료")
            break   # while 루프 완전 탈출


# ── 진입점 ────────────────────────────────────────────────────

if __name__ == "__main__":
    # 이 파일을 직접 실행할 때만 main() 호출
    # 다른 파일에서 import할 때는 main() 자동 실행 안 됨
    main()