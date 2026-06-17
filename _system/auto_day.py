#!/usr/bin/env python3
"""
auto_day.py — 날짜 바뀌면 PROGRESS.md 자동 갱신
  1. 체크리스트 날짜 헤더 → 오늘로 교체
  2. 📋 체크리스트 계획표에서 오늘 항목 추출 → 새 체크리스트로 삽입
  3. 계획표에 오늘 항목 없으면 기존 체크박스만 리셋
  4. 업데이트 로그에 어제 완료 현황 기록
  5. 📝 오늘의 코멘트 자동 분석 부분 갱신 (Claude 분석 블록은 보존)
"""
import os
import re
import tempfile
from datetime import date, timedelta
from pathlib import Path

PROGRESS_FILE = "/home/jsy/devops-portfolio/_system/PROGRESS.md"
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]
HEADER_RE = re.compile(r"## ✅ 오늘 \((.+?)\) 체크리스트")

EXAM_DATES = {
    "AWS SAA": date(2026, 7, 22),
    "OPIc IH": date(2026, 7, 25),
    "CKA":     date(2026, 8, 5),
}

PHASE_MILESTONES = [
    (date(2026, 6, 20), "신찬수 55강 완료"),
    (date(2026, 6, 22), "PF2 완성"),
    (date(2026, 6, 27), "Terraform 완료"),
    (date(2026, 7, 2),  "Ansible 완료"),
    (date(2026, 7, 20), "SAA Mock 3회 완료"),
    (date(2026, 7, 25), "PF-K8s 완료"),
    (date(2026, 8, 4),  "CKA 최종 정리"),
    (date(2026, 8, 17), "CI/CD+Observability 완료"),
    (date(2026, 8, 28), "PF1 완성"),
    (date(2026, 8, 31), "포트폴리오 PPT"),
]



def backup_progress(content: str, today: date):
    """PROGRESS.md 일일 백업 (최근 7일 보관)"""
    from pathlib import Path
    backup_dir = Path("/home/jsy/devops-portfolio/_system/backup")
    backup_dir.mkdir(exist_ok=True)
    backup_file = backup_dir / f"PROGRESS_{today.strftime('%Y%m%d')}.md"
    if not backup_file.exists():
        backup_file.write_text(content, encoding="utf-8")
        # 7일 초과 백업 삭제
        old = sorted(backup_dir.glob("PROGRESS_*.md"))[:-7]
        for f in old:
            try: f.unlink()
            except Exception: pass



def safe_write(path: str, new_content: str):
    """원자적 파일 쓰기: tempfile → os.replace (중단돼도 파일 손상 없음)"""
    dir_ = os.path.dirname(path)
    with tempfile.NamedTemporaryFile("w", dir=dir_, suffix=".tmp",
                                     delete=False, encoding="utf-8") as f:
        f.write(new_content)
        tmp = f.name
    os.replace(tmp, path)


def validate_or_restore(path: str, backup_dir: str) -> str:
    """PROGRESS.md 읽기. HEADER_RE 없으면 최신 백업에서 복구."""
    try:
        text = open(path, encoding="utf-8").read()
    except FileNotFoundError:
        text = ""
    if HEADER_RE.search(text):
        return text
    # 복구 시도
    backups = sorted(Path(backup_dir).glob("PROGRESS_*.md"))
    for bk in reversed(backups):
        bk_text = bk.read_text(encoding="utf-8")
        if HEADER_RE.search(bk_text):
            safe_write(path, bk_text)
            print(f"[auto_day] PROGRESS.md 손상 → {bk.name} 으로 복구")
            return bk_text
    print("[auto_day] WARNING: PROGRESS.md 손상 & 백업 없음")
    return text


def get_plan_items(content, today):
    today_key = f"{today.month}/{today.day}"
    in_table = False
    for line in content.split("\n"):
        if "## 📋 체크리스트 계획표" in line:
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if in_table and line.startswith("|") and "---" not in line:
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if cols and cols[0].strip() == today_key:
                return [c for c in cols[1:] if c and c not in ("—", "-", "")]
    return []


def get_yesterday_result(content):
    done, total = 0, 0
    in_cl = False
    for line in content.split("\n"):
        if HEADER_RE.search(line):
            in_cl = True
            continue
        if in_cl:
            if line.startswith("##"):
                break
            m = re.match(r"- \[([xX ])\]", line)
            if m:
                total += 1
                if m.group(1).lower() == "x":
                    done += 1
    return done, total


def replace_checklist(content, new_items):
    lines = content.split("\n")
    result = []
    in_cl = False
    for line in lines:
        if HEADER_RE.search(line):
            in_cl = True
            result.append(line)
            for item in new_items:
                result.append(f"- [ ] {item}")
            continue
        if in_cl:
            if line.startswith("##") and "체크리스트" not in line:
                in_cl = False
                result.append(line)
            elif re.match(r"- \[[ xX]\]", line):
                pass
            else:
                result.append(line)
        else:
            result.append(line)
    return "\n".join(result)


def reset_checkboxes(content):
    in_cl = False
    result = []
    for line in content.split("\n"):
        if HEADER_RE.search(line):
            in_cl = True
            result.append(line)
            continue
        if in_cl and line.startswith("##") and "체크리스트" not in line:
            in_cl = False
        if in_cl:
            line = re.sub(r"(- \[)[xX](\])", r"\1 \2", line)
        result.append(line)
    return "\n".join(result)


def generate_auto_lines(today, done, total):
    """자동 분석 라인 생성 (날짜·완료율·D-day·마일스톤 기반)"""
    lines = []

    # 어제 완료율
    if total > 0:
        rate = done / total
        if rate >= 1.0:
            lines.append(f"🔥 어제 {done}/{total} 전부 완료")
        elif rate >= 0.7:
            lines.append(f"✅ 어제 {done}/{total} 완료")
        elif rate > 0:
            lines.append(f"📉 어제 {done}/{total} 완료 — 오늘 집중 필요")
        else:
            lines.append(f"⚠️ 어제 체크리스트 0/{total} — 무슨 일이 있었는지 확인")

    # 시험 D-day (60일 이내)
    for name, d in EXAM_DATES.items():
        delta = (d - today).days
        if 0 < delta <= 60:
            if delta <= 3:
                emoji = "🚨"
            elif delta <= 7:
                emoji = "⚠️"
            elif delta <= 14:
                emoji = "📌"
            else:
                emoji = "📅"
            lines.append(f"{emoji} {name} D-{delta}")
        elif delta == 0:
            lines.append(f"🎉 오늘 {name} 시험일!")

    # 가까운 마일스톤 (7일 이내)
    for d, label in PHASE_MILESTONES:
        delta = (d - today).days
        if delta == 0:
            lines.append(f"🎉 오늘 {label} 마감!")
        elif 0 < delta <= 3:
            lines.append(f"🚨 {label} D-{delta} — 마감 임박")
        elif 0 < delta <= 7:
            lines.append(f"🎯 {label} D-{delta}")
        elif delta < 0 and delta >= -1:
            lines.append(f"⚠️ {label} 어제 마감 — 완료 여부 확인")

    return lines


def update_comment_section(content, today, auto_lines):
    """
    ## 📝 오늘의 코멘트 섹션에서 자동 분석 부분만 교체.
    **[Claude 분석]** 블록 이하는 보존.
    """
    today_str = f"{today.year}-{today.month:02d}-{today.day:02d}"
    auto_text = "\n".join(f"- {l}" for l in auto_lines) if auto_lines else "- 오늘도 계획대로 진행 중"

    header_pat = re.compile(r"^## 📝 오늘의 코멘트$", re.MULTILINE)
    claude_pat = re.compile(r"^\*\*\[Claude 분[석析]\]\*\*", re.MULTILINE)

    h_m = header_pat.search(content)
    c_m = claude_pat.search(content)
    if not h_m or not c_m or c_m.start() < h_m.start():
        return content

    # 섹션 헤더 직후 ~ Claude 분석 블록 직전까지만 교체 (산술 없음)
    new_auto = f"\n> {today_str} 업데이트\n\n{auto_text}\n\n"
    return content[:h_m.end()] + new_auto + content[c_m.start():]


def run():
    today = date.today()
    today_str = f"{today.month}/{today.day} {WEEKDAYS[today.weekday()]}"

    content = validate_or_restore(
        PROGRESS_FILE, "/home/jsy/devops-portfolio/_system/backup"
    )

    # 오늘 날짜 백업 (없으면 생성)
    backup_progress(content, today)

    match = HEADER_RE.search(content)
    if not match:
        return

    if match.group(1) == today_str:
        return  # 이미 오늘 날짜

    old_str = match.group(1)
    done, total = get_yesterday_result(content)

    # 날짜 헤더 교체
    content = HEADER_RE.sub(f"## ✅ 오늘 ({today_str}) 체크리스트", content)

    # 체크리스트 항목 갱신
    plan_items = get_plan_items(content, today)
    if plan_items:
        content = replace_checklist(content, plan_items)
        note = f"계획표 {len(plan_items)}항목 자동 삽입"
    else:
        content = reset_checkboxes(content)
        note = "계획표 없음 → 체크박스 리셋"

    # 업데이트 로그 추가 (최근 30개 유지)
    yesterday_str = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    log_line = f"| {yesterday_str} | 체크리스트 완료 {done}/{total} ({note}) |"

    def trim_log(m):
        header   = m.group(1)  # "## 업데이트 로그\n\n| 날짜 | 내용 |\n|------|------|\n"
        new_line = log_line + "\n"
        existing = m.group(2)  # 기존 행들
        rows = [r for r in existing.splitlines(keepends=True) if r.strip()]
        rows = rows[-29:] if len(rows) >= 30 else rows  # 29개만 남기고 새 1개 추가
        return header + new_line + "".join(rows)

    log_pat = re.compile(r"(## 업데이트 로그\n\n\|[^\n]+\|\n\|[^\n]+\|\n)((?:\|[^\n]+\|\n)*)")
    content = log_pat.sub(trim_log, content)

    # 오늘의 코멘트 자동 분석 갱신
    auto_lines = generate_auto_lines(today, done, total)
    content = update_comment_section(content, today, auto_lines)

    safe_write(PROGRESS_FILE, content)

    print(f"[auto_day] {old_str} → {today_str}  어제 {done}/{total}  {note}")


if __name__ == "__main__":
    run()
