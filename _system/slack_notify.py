#!/usr/bin/env python3
"""
PROGRESS.md → Slack 알림 스크립트
사용법:
  python3 slack_notify.py today      # 오늘 체크리스트 전송
  python3 slack_notify.py progress   # 전체 진도 요약 전송
  python3 slack_notify.py done "신찬수 47~51강"  # 항목 완료 처리 + 전송
"""

import json
import sys
import re
from datetime import date, datetime
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

def _load_config() -> dict:
    try:
        return json.loads(Path("/home/jsy/devops-portfolio/_system/config.json").read_text())
    except Exception:
        return {}

_cfg          = _load_config()
WEBHOOK_URL   = _cfg.get("slack_webhook_url", "")
PROGRESS_FILE = "/home/jsy/devops-portfolio/_system/PROGRESS.md"

EXAM_DATES = {
    "AWS SAA": date(2026, 7, 22),
    "OPIc IH": date(2026, 7, 25),
    "CKA":     date(2026, 8, 5),
}

WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def read_progress():
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return f.read()


def parse_today_checklist(content):
    """PROGRESS.md에서 오늘 체크리스트 파싱"""
    lines = content.split("\n")
    in_today = False
    items = []
    for line in lines:
        if re.match(r"^##\s*✅.*(오늘|체크리스트)", line):
            in_today = True
            continue
        if in_today:
            if line.startswith("##") and "오늘" not in line and "체크리스트" not in line:
                break
            m = re.match(r"^- \[([ xX])\] (.+)", line)
            if m:
                done = m.group(1).lower() == "x"
                items.append({"done": done, "text": m.group(2).strip()})
    return items


def parse_current_phase(content):
    """현재 진행중인 Phase 파싱"""
    lines = content.split("\n")
    phase_info = []
    in_progress = False
    for line in lines:
        if "🔄" in line or "진행중" in line:
            clean = re.sub(r"[|🔄]", "", line).strip()
            if clean and len(clean) > 3:
                phase_info.append(clean)
        if len(phase_info) >= 5:
            break
    return phase_info


def calc_dday(target: date) -> str:
    delta = (target - date.today()).days
    if delta > 0:
        return f"D-{delta}"
    elif delta == 0:
        return "D-DAY"
    else:
        return f"D+{abs(delta)}"


def send_slack(blocks):
    payload = json.dumps({"blocks": blocks}).encode("utf-8")
    req = Request(WEBHOOK_URL, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=10) as resp:
            return resp.read().decode()
    except URLError as e:
        print(f"Slack 전송 실패: {e}")
        return None


def cmd_today():
    content = read_progress()
    items = parse_today_checklist(content)
    today = date.today()
    weekday = WEEKDAYS[today.weekday()]
    header = f"📅 {today.strftime('%Y-%m-%d')} ({weekday}) 오늘 체크리스트"

    done_count = sum(1 for i in items if i["done"])
    total = len(items)

    checklist_text = ""
    for item in items:
        icon = "✅" if item["done"] else "⬜"
        checklist_text += f"{icon} {item['text']}\n"

    if not checklist_text:
        checklist_text = "_(오늘 체크리스트 항목이 없습니다)_"

    dday_text = "  |  ".join(
        f"*{name}* {calc_dday(d)} ({d.strftime('%m/%d')})"
        for name, d in EXAM_DATES.items()
    )

    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": header}},
        {"type": "section", "text": {"type": "mrkdwn", "text": checklist_text.strip()}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"진행: *{done_count}/{total}* 완료\n🎯 시험 D-DAY: {dday_text}"}},
        {"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"PROGRESS.md 기준 · {datetime.now().strftime('%H:%M')} 전송"}
        ]}
    ]
    result = send_slack(blocks)
    if result == "ok":
        print(f"✅ Slack 전송 완료 ({done_count}/{total} 완료)")
    else:
        print("❌ 전송 실패")


def cmd_progress():
    content = read_progress()
    today = date.today()
    weekday = WEEKDAYS[today.weekday()]

    dday_lines = "\n".join(
        f"• *{name}*: {calc_dday(d)} ({d.strftime('%m/%d')})"
        for name, d in EXAM_DATES.items()
    )

    # 진행중 항목 간단히 추출
    progress_lines = []
    for line in content.split("\n"):
        if "🔄" in line and "|" in line:
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cols) >= 2:
                progress_lines.append(f"🔄 {cols[0]}: {cols[1]}")
        if len(progress_lines) >= 6:
            break

    progress_text = "\n".join(progress_lines) if progress_lines else "_(진행 항목 없음)_"

    blocks = [
        {"type": "header", "text": {"type": "plain_text",
            "text": f"📊 전체 진도 요약 — {today.strftime('%Y-%m-%d')} ({weekday})"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": progress_text}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn",
            "text": f"🎯 *시험 일정*\n{dday_lines}"}},
        {"type": "context", "elements": [
            {"type": "mrkdwn", "text": f"PROGRESS.md 기준 · {datetime.now().strftime('%H:%M')} 전송"}
        ]}
    ]
    result = send_slack(blocks)
    if result == "ok":
        print("✅ 진도 요약 Slack 전송 완료")
    else:
        print("❌ 전송 실패")


def cmd_done(item_text):
    """항목 완료 처리: PROGRESS.md 체크박스 업데이트 후 Slack 전송"""
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"(- \[) \] (" + re.escape(item_text) + r")")
    new_content, count = pattern.subn(r"\1x] \2", content)

    if count == 0:
        # 부분 일치로 재시도
        pattern2 = re.compile(r"(- \[) \] ([^\n]*" + re.escape(item_text) + r"[^\n]*)")
        new_content, count = pattern2.subn(r"\1x] \2", content)

    if count > 0:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        # Windows Claude 폴더에도 동기화
        try:
            import shutil
            shutil.copy("/home/jsy/devops-portfolio/_system/PROGRESS.md", "/mnt/c/Users/jeong/Claude/PROGRESS.md")
        except Exception:
            pass
        print(f"✅ '{item_text}' 완료 처리됨")
        cmd_today()
    else:
        print(f"❌ '{item_text}' 항목을 찾지 못했습니다. 정확한 텍스트를 입력해주세요.")
        cmd_today()


def main():
    args = sys.argv[1:]
    if not args or args[0] == "today":
        cmd_today()
    elif args[0] == "progress":
        cmd_progress()
    elif args[0] == "done" and len(args) >= 2:
        cmd_done(" ".join(args[1:]))
    else:
        print("사용법:")
        print("  python3 slack_notify.py today            # 오늘 체크리스트")
        print("  python3 slack_notify.py progress         # 전체 진도 요약")
        print('  python3 slack_notify.py done "항목 텍스트"  # 완료 처리')


if __name__ == "__main__":
    main()
