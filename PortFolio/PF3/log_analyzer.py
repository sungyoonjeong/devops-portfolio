# log_analyzer.py 핵심 기능
# monitor.py가 생성한 monitor.log를 읽어서:
#   ① 전체 로그 통계 (정상·경고·에러 건수)
#   ② 최근 경고·에러 내역 출력
#   ③ 어떤 지표가 가장 많이 초과됐는지 분석
#   ④ 분석 결과를 report.txt로 저장

import re
import os
import time                          
from datetime import datetime
from collections import Counter

LOG_FILE      = 'monitor.log'
REPORT_FILE   = 'report.txt'
CHECK_INTERVAL = 10                  # 10초마다 파일 변경 확인


def read_log(filepath):
    if not os.path.exists(filepath):
        print(f"❌ 로그 파일 없음: {filepath}")
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [l.strip() for l in lines if l.strip()]


def classify_logs(lines):
    info     = [l for l in lines if '[INFO]'    in l]
    warnings = [l for l in lines if '[WARNING]' in l]
    errors   = [l for l in lines if '[ERROR]'   in l]
    return info, warnings, errors


def analyze_warnings(warnings):
    cpu_count  = sum(1 for w in warnings if 'CPU'    in w)
    mem_count  = sum(1 for w in warnings if '메모리' in w)
    disk_count = sum(1 for w in warnings if '디스크' in w)
    return {'CPU': cpu_count, '메모리': mem_count, '디스크': disk_count}


def extract_metrics(info_lines):
    cpu_vals, mem_vals, disk_vals = [], [], []
    for line in info_lines:
        if '정상' in line and 'CPU' in line:
            try:
                cpu  = float(re.search(r'CPU: ([\d.]+)%',   line).group(1))
                mem  = float(re.search(r'메모리: ([\d.]+)%', line).group(1))
                disk = float(re.search(r'디스크: ([\d.]+)%', line).group(1))
                cpu_vals.append(cpu)
                mem_vals.append(mem)
                disk_vals.append(disk)
            except (AttributeError, ValueError):
                continue
    return cpu_vals, mem_vals, disk_vals


def generate_report(lines, info, warnings, errors, pattern, cpu_vals, mem_vals, disk_vals):
    now      = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    avg_cpu  = sum(cpu_vals)  / len(cpu_vals)  if cpu_vals  else 0
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
    if warnings:
        report += "\n[ 최근 경고 내역 ]\n"
        for w in warnings[-3:]:
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
    return report


def analyze_once():
    """한 번 분석 실행"""
    lines = read_log(LOG_FILE)
    if not lines:
        return

    info, warnings, errors           = classify_logs(lines)
    pattern                          = analyze_warnings(warnings)
    cpu_vals, mem_vals, disk_vals    = extract_metrics(info)
    report                           = generate_report(
        lines, info, warnings, errors,
        pattern, cpu_vals, mem_vals, disk_vals
    )

    print(report)

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ 리포트 업데이트: {REPORT_FILE}")


def main():
    print("📊 로그 분석기 시작")
    print(f"   대상 파일: {LOG_FILE}")
    print(f"   확인 주기: {CHECK_INTERVAL}초")
    print("   Ctrl+C 로 종료\n")

    last_modified = 0   # 마지막으로 확인한 파일 수정 시간

    while True:
        try:
            # 파일이 존재하는지 확인
            if os.path.exists(LOG_FILE):

                # 파일 수정 시간 확인
                current_modified = os.path.getmtime(LOG_FILE)

                # 수정 시간이 바뀌었으면 재분석
                if current_modified != last_modified:
                    print(f"\n🔄 로그 변경 감지 → 재분석 중...")
                    analyze_once()
                    last_modified = current_modified

                else:
                    # 변경 없으면 대기 중 표시
                    now = datetime.now().strftime("%H:%M:%S")
                    print(f"[{now}] 변경 없음 — {CHECK_INTERVAL}초 후 재확인", end='\r')

            else:
                print(f"⏳ {LOG_FILE} 대기 중...", end='\r')

            time.sleep(CHECK_INTERVAL)  # 10초 대기

        except KeyboardInterrupt:
            # Ctrl+C 누르면 종료
            print("\n\n🛑 로그 분석기 종료")
            break


if __name__ == "__main__":
    main()