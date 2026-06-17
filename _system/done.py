#!/usr/bin/env python3
"""
done.py — 오늘 체크리스트 항목 체크 / 언체크
사용법:
  check 신찬수 52강       # 키워드 매칭 항목 체크 ([ ] → [x])
  uncheck 신찬수 52강     # 체크 취소 ([x] → [ ])  ← 잘못 체크했을 때
  check                   # 현재 체크리스트만 출력
"""
import os
import re
import sys
import tempfile
from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

PROGRESS_FILE = "/home/jsy/devops-portfolio/_system/PROGRESS.md"
WEEKDAYS  = ["월", "화", "수", "목", "금", "토", "일"]
HEADER_RE = re.compile(r"^##\s*✅.*(오늘|체크리스트)", re.MULTILINE)
STOPWORDS = {"오늘", "완료", "했어", "함", "다", "이거", "이것", "방금", "끝", "했음", "완", "취소", "undo"}

console = Console()



def safe_write(path: str, content: str):
    dir_ = os.path.dirname(path)
    with tempfile.NamedTemporaryFile("w", dir=dir_, suffix=".tmp",
                                     delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp = f.name
    os.replace(tmp, path)


def load() -> str:
    with open(PROGRESS_FILE, encoding="utf-8") as f:
        return f.read()


def save(content: str):
    safe_write(str(PROGRESS_FILE), content)


def extract_keywords(query: str) -> list[str]:
    return [w for w in query.strip().split() if w not in STOPWORDS and len(w) >= 2]


def matches(item_text: str, keywords: list[str]) -> bool:
    return all(kw in item_text for kw in keywords)


def mark(content: str, keywords: list[str], check: bool) -> tuple[str, list[str]]:
    """check=True → [ ]→[x] (체크), check=False → [x]→[ ] (언체크)"""
    src_mark = " " if check else "x"
    dst_mark = "x" if check else " "
    lines, changed, in_cl = [], [], False
    for line in content.split("\n"):
        if HEADER_RE.search(line):
            in_cl = True
            lines.append(line)
            continue
        if in_cl and line.startswith("##") and "체크리스트" not in line:
            in_cl = False
        if in_cl:
            m = re.match(r"^(- \[)([xX ])(\] .+)", line)
            if m and m.group(2).lower() == src_mark:
                item_text = m.group(3)[2:]
                if matches(item_text, keywords):
                    lines.append(f"{m.group(1)}{dst_mark}{m.group(3)}")
                    changed.append(item_text)
                    continue
        lines.append(line)
    return "\n".join(lines), changed


def print_checklist(content: str):
    today   = date.today()
    weekday = WEEKDAYS[today.weekday()]
    items   = []
    in_cl   = False
    for line in content.split("\n"):
        if HEADER_RE.search(line):
            in_cl = True; continue
        if in_cl:
            if line.startswith("##") and "체크리스트" not in line: break
            m = re.match(r"^- \[([ xX])\] (.+)", line)
            if m:
                items.append({"done": m.group(1).lower() == "x", "text": m.group(2)})
    if not items:
        console.print("[dim]체크리스트 없음[/]"); return
    done_n = sum(1 for i in items if i["done"])
    total  = len(items)
    t = Text()
    for item in items:
        if item["done"]:
            t.append("  ✅ ", style="green")
            t.append(item["text"] + "\n", style="dim strike")
        else:
            t.append("  ⬜ ", style="white")
            t.append(item["text"] + "\n", style="white")
    bar_n  = int(done_n / total * 20) if total else 0
    bar    = "█" * bar_n + "░" * (20 - bar_n)
    color  = "green" if done_n == total else "yellow"
    console.print(Panel(
        t,
        title=f"[bold {color}]✅ {today.month}/{today.day} ({weekday}) 체크리스트  [{color}]{bar}[/]  {done_n}/{total}[/]",
        border_style=color, padding=(0, 1),
    ))


def main():
    # argv[0] 기준으로 check / uncheck 구분
    prog      = sys.argv[0].split("/")[-1].replace(".py", "")
    is_uncheck = (prog == "uncheck") or (len(sys.argv) > 1 and sys.argv[1] == "--undo")

    args  = sys.argv[1:]
    if is_uncheck and args and args[0] == "--undo":
        args = args[1:]
    query = " ".join(args).strip()

    content = load()

    if not query:
        print_checklist(content)
        return

    keywords = extract_keywords(query)
    if not keywords:
        console.print("[yellow]인식된 키워드가 없습니다.[/]")
        print_checklist(content); return

    new_content, changed = mark(content, keywords, check=not is_uncheck)

    if not changed:
        action = "언체크" if is_uncheck else "체크"
        console.print(f"[red]{action}할 항목 없음:[/] '{' '.join(keywords)}'")
        print_checklist(content); return

    save(new_content)
    for item in changed:
        if is_uncheck:
            console.print(f"[yellow]↩ 체크 취소:[/] {item}")
        else:
            console.print(f"[green]✅ 체크 완료:[/] {item}")
    print_checklist(new_content)


if __name__ == "__main__":
    main()
