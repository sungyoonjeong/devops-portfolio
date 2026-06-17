#!/usr/bin/env python3
"""auto_night.py — 일과 마무리 명령어 (alias: night)"""
import subprocess
from datetime import date, timedelta
from pathlib import Path

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def main():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    tomorrow_marker = f"/tmp/.claude_morning_{tomorrow.strftime('%Y%m%d')}"
    log_path = "/tmp/claude_night.log"

    # 1. 날짜 롤오버 (즉시)
    r = subprocess.run(
        ['python3', '/home/jsy/devops-portfolio/_system/auto_day.py'],
        capture_output=True, text=True
    )
    if r.stdout.strip():
        print(r.stdout.strip())

    # 2. AI 분석 백그라운드 생성 (완료 시 내일 마커 자동 생성)
    with open(log_path, 'w') as logf:
        subprocess.Popen(
            ['python3', '/home/jsy/devops-portfolio/_system/claude_morning.py',
             '--force', '--marker', tomorrow_marker],
            stdout=logf, stderr=subprocess.STDOUT,
            start_new_session=True
        )

    tomorrow_str = f"{tomorrow.month}/{tomorrow.day}({WEEKDAYS[tomorrow.weekday()]})"
    print(f"✅ {today.month}/{today.day} 일과 마무리")
    print(f"   → 내일({tomorrow_str}) 체크리스트 세팅 완료")
    print(f"   → AI 분석 백그라운드 생성 중 (로그: {log_path})")
    print(f"   → 내일 터미널 열면 분석 완료된 대시보드 바로 표시")


if __name__ == '__main__':
    main()
