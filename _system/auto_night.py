#!/usr/bin/env python3
"""auto_night.py — 일과 마무리 명령어 (alias: night)"""
import subprocess
from datetime import date, timedelta
from pathlib import Path

PROGRESS_FILE = Path("/home/jsy/devops-portfolio/_system/PROGRESS.md")
REPO_DIR      = "/home/jsy/devops-portfolio"

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def _auto_commit_progress(today: date):
    """PROGRESS.md 일일 자동 커밋 (변경 있을 때만)"""
    try:
        # 변경 여부 확인
        status = subprocess.run(
            ["git", "-C", REPO_DIR, "status", "--porcelain",
             str(PROGRESS_FILE)],
            capture_output=True, text=True
        )
        if not status.stdout.strip():
            return  # 변경 없으면 커밋 안 함

        subprocess.run(
            ["git", "-C", REPO_DIR, "add", str(PROGRESS_FILE)],
            capture_output=True
        )
        msg = f"auto: PROGRESS.md {today.strftime('%Y-%m-%d')} 일일 업데이트"
        subprocess.run(
            ["git", "-C", REPO_DIR, "commit", "-m", msg],
            capture_output=True
        )
        print(f"   → PROGRESS.md 자동 커밋 완료 (push는 post-commit hook이 처리)")
    except Exception as e:
        print(f"   [auto_commit] 실패: {e}")



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

    # PROGRESS.md 자동 커밋 + push
    _auto_commit_progress(today)

    tomorrow_str = f"{tomorrow.month}/{tomorrow.day}({WEEKDAYS[tomorrow.weekday()]})"
    print(f"✅ {today.month}/{today.day} 일과 마무리")
    print(f"   → 내일({tomorrow_str}) 체크리스트 세팅 완료")
    print(f"   → AI 분석 백그라운드 생성 중 (로그: {log_path})")
    print(f"   → 내일 터미널 열면 분석 완료된 대시보드 바로 표시")


if __name__ == '__main__':
    main()
