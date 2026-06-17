#!/usr/bin/env python3
"""DevOps 취업 대시보드 v5 — 문단 자동 bullet 분리 + 전체 만점 시스템"""

import json
import re
import sys
from datetime import date
from pathlib import Path

from rich import box
from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

PROGRESS_FILE = "/home/jsy/devops-portfolio/_system/PROGRESS.md"
WEEKDAYS      = ["월", "화", "수", "목", "금", "토", "일"]
EXAM_DATES    = {
    "AWS SAA": date(2026, 7, 22),
    "OPIc IH": date(2026, 7, 25),
    "CKA":     date(2026, 8,  5),
}

CORE_META = {
    "어제 실적":     ("bright_cyan",    "📋"),
    "일정 위험 신호": ("bright_red",     "🚨"),
    "시험 D-day":    ("bright_yellow",  "🎯"),
    "다가오는 Phase": ("bright_magenta", "🔜"),
    "트랙별 페이스":  ("bright_blue",    "📊"),
    "오늘 우선순위":  ("bright_white",   "⚡"),
    "업데이트 사항":  ("bright_green",   "🔄"),
}
WEB_META = {
    "채용 동향":     ("bright_green",   "💼"),
    "공고 갭 분析":  ("bright_cyan",    "🔍"),
    "시험·전형 준비": ("bright_yellow",  "📝"),
    "IT 트렌드":    ("bright_magenta",  "📡"),
    "커뮤니티":     ("bright_blue",     "💬"),
}
WEB_TITLES = set(WEB_META.keys())

console = Console()


# ── 유틸 ───────────────────────────────────────────────────────────────────────

def read_progress() -> str:
    with open(PROGRESS_FILE, encoding="utf-8") as f:
        return f.read()

def dday(target: date) -> str:
    d = (target - date.today()).days
    return "D-DAY" if d == 0 else f"D-{d}" if d > 0 else f"D+{abs(d)}"

def dday_color(target: date) -> str:
    d = (target - date.today()).days
    return "bold bright_red" if d <= 7 else "bold bright_yellow" if d <= 21 else "bold bright_green"

def get_web_intel() -> dict:
    f = Path(f"/tmp/web_intel_{date.today().strftime('%Y%m%d')}.json")
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    except Exception:
        return {}


# ── 파서 ───────────────────────────────────────────────────────────────────────

def parse_checklist(content: str) -> list[dict]:
    items, in_cl = [], False
    for line in content.split("\n"):
        if re.match(r"^##\s*✅.*(오늘|체크리스트)", line):
            in_cl = True; continue
        if in_cl:
            if line.startswith("##"): break
            m = re.match(r"^- \[([ xX])\] (.+)", line)
            if m:
                items.append({"done": m.group(1).lower() == "x", "text": m.group(2).strip()})
    return items

def parse_section_table(content: str, section_name: str) -> list[list[str]]:
    rows, in_sum, in_sec = [], False, False
    for line in content.split("\n"):
        if "## 📊 현황 요약" in line:
            in_sum = True; continue
        if in_sum and line.startswith("## ") and "현황" not in line:
            break
        if not in_sum: continue
        if f"### {section_name}" in line:
            in_sec = True; continue
        if in_sec and line.startswith("### "): break
        if in_sec and line.startswith("|") and "---" not in line:
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if cols and cols[0] not in ("항목",):
                rows.append(cols)
    return rows

def parse_week(content: str) -> list[list[str]]:
    rows, in_week = [], False
    for line in content.split("\n"):
        if "## 이번 주 일정" in line:
            in_week = True; continue
        if in_week and line.startswith("##"): break
        if in_week and line.startswith("|") and "---" not in line and "날짜" not in line:
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cols) >= 2:
                rows.append(cols)
    return rows

def parse_comment_blocks(content: str) -> tuple[list[str], str]:
    auto_lines, claude_raw = [], []
    in_comment, in_claude = False, False
    for line in content.split("\n"):
        if "## 📝 오늘의 코멘트" in line:
            in_comment = True; continue
        if in_comment:
            if line.startswith("## ") and "코멘트" not in line: break
            if line.strip() == "---": break
            if line.startswith("> "): continue
            if "**[Claude 분析]**" in line or "**[Claude 분析]**" in line or "**[Claude 분석]**" in line:
                in_claude = True; continue
            if in_claude:
                claude_raw.append(line)
            else:
                auto_lines.append(line)
    return auto_lines, "\n".join(claude_raw)

def parse_claude_sections(raw: str) -> tuple[list[tuple], list[tuple]]:
    sections, cur_title, cur_body = [], None, []
    for line in raw.split("\n"):
        m = re.match(r'\*\*\[(.+?)\]\*\*\s*(.*)', line)
        if m:
            if cur_title is not None:
                sections.append((cur_title, "\n".join(cur_body).strip()))
            cur_title = m.group(1)
            inline = re.sub(r'\*\*(.+?)\*\*', r'\1', m.group(2).strip())
            cur_body = [inline] if inline else []
        elif cur_title is not None:
            cur_body.append(re.sub(r'\*\*(.+?)\*\*', r'\1', line))
    if cur_title is not None:
        sections.append((cur_title, "\n".join(cur_body).strip()))
    core = [(t, b) for t, b in sections if t not in WEB_TITLES]
    web  = [(t, b) for t, b in sections if t     in WEB_TITLES]
    return core, web


# ── 문단 자동 bullet 변환 ────────────────────────────────────────────────────────

def _smart_format(body: str) -> list[str]:
    """body 텍스트를 항목별 줄 목록으로 변환.
    · 이미 bullet 형식 → 그대로
    · ①②③이 한 줄에 합쳐진 경우 → 번호별 분리
    · 긴 문단 → '. [가-힣A-Z/날짜]' 기준 분할
    · 첫 분할이 짧으면 요약 헤더, 나머지 bullet
    """
    out = []
    for raw in body.split('\n'):
        s = raw.strip()
        if not s:
            out.append('')
            continue

        # ①②③이 한 줄에 섞인 경우 분리 (구 프롬프트 결과 대응)
        if s and s[0] in ('①', '②', '③', '④'):
            combined = re.split(r'\s+(?=[②③④⑤])', s)
            if len(combined) > 1:
                out.extend(p.strip() for p in combined if p.strip())
            else:
                out.append(s)
            continue

        # 이미 bullet 형식
        if s[0] in ('·', '•', '▸'):
            out.append(s)
            continue
        if s.startswith('- '):
            out.append('· ' + s[2:])
            continue

        # 짧은 줄
        if len(s) < 45:
            out.append(s)
            continue

        # 긴 문단 분할: '. [가-힣/영문대문자/날짜패턴]' 기준
        parts = re.split(r'\.\s+(?=[가-힣A-Z①②③④]|\d{1,2}/)', s)
        parts = [p.rstrip('.').strip() for p in parts if p.strip()]
        if len(parts) < 2:
            # ' — ' 또는 ' → ' 로 재시도
            parts = re.split(r'\s[—→]\s', s)
            parts = [p.strip() for p in parts if p.strip()]
        if len(parts) < 2:
            out.append(s)
            continue

        # 첫 파트가 짧으면 요약 헤더, 나머지 bullet
        if len(parts[0]) < 25:
            out.append(parts[0])
            out.extend(f'· {p}' for p in parts[1:])
        else:
            out.extend(f'· {p}' for p in parts)
    return out


# ── 공통 섹션 렌더러 ────────────────────────────────────────────────────────────

def _render_section(title: str, body: str, color: str, icon: str) -> Text:
    block = Text()
    block.append(f"  ▌ {icon}  ", style=f"bold {color}")
    block.append(f"{title}\n", style=f"bold {color}")

    lines = _smart_format(body)
    for fline in lines:
        if not fline:
            block.append("\n")
        elif fline[0] in ('·', '•', '▸'):
            block.append(f"      {fline}\n", style="white")
        elif fline[0] in ('①', '②', '③', '④'):
            block.append(f"      {fline}\n", style="bright_white")
        else:
            block.append(f"    {fline}\n", style="bright_white")

    block.append("\n")
    return block


# ── 섹션 렌더러 ────────────────────────────────────────────────────────────────

def render_header():
    today   = date.today()
    weekday = WEEKDAYS[today.weekday()]
    console.print()
    console.print(Rule(
        f"[bold bright_cyan]  DevOps 취업 2026[/]  "
        f"[bold white]{today.strftime('%Y.%m.%d')} {weekday}요일[/]  ",
        style="bright_cyan",
    ))
    console.print()


def render_dday():
    panels = []
    for name, d in EXAM_DATES.items():
        dd_str = dday(d)
        color  = dday_color(d)
        bare   = color.replace("bold ", "")
        content = Text(justify="center")
        content.append(f"\n{dd_str}\n", style=color)
        content.append(f"{d.strftime('%m. %d')}\n", style="white")
        panels.append(Panel(
            content,
            title=f"[{bare}]◆ {name}[/]",
            border_style=bare,
            expand=True, padding=(0, 2),
        ))
    console.print(Columns(panels, equal=True, expand=True))


def render_checklist(content: str):
    items = parse_checklist(content)
    if not items: return
    done  = sum(1 for i in items if i["done"])
    total = len(items)
    pct   = int(done / total * 100) if total else 0
    bar_n = int(done / total * 28) if total else 0
    color = "bright_green" if done == total else "bright_yellow" if pct >= 50 else "bright_red"
    bare  = color.replace("bright_", "")

    bar = Text()
    bar.append("  ")
    bar.append("█" * bar_n, style="bright_green")
    bar.append("░" * (28 - bar_n), style="grey50")
    bar.append(f"  {done} / {total}  ({pct}%)\n", style=f"bold {color}")

    body = Text()
    body.append("\n")
    for item in items:
        if item["done"]:
            body.append("  ✅  ", style="bright_green")
            body.append(item["text"] + "\n", style="grey66 strike")
        else:
            body.append("  ⬜  ", style="white")
            body.append(item["text"] + "\n", style="bold bright_white")

    today   = date.today()
    weekday = WEEKDAYS[today.weekday()]
    console.print(Panel(
        Group(bar, body),
        title=f"[bold {color}]✅  {today.month}월 {today.day}일 ({weekday})  오늘 체크리스트[/]",
        border_style=bare,
        padding=(0, 1),
    ))


def render_analysis(content: str):
    auto_lines, claude_raw = parse_comment_blocks(content)
    core_sections, web_sections = parse_claude_sections(claude_raw)

    BULLET_STYLES = {
        "📉": "bold bright_yellow", "🚨": "bold bright_red", "⚠️": "bold bright_red",
        "✅": "bright_green",  "🎯": "bold bright_cyan",  "📅": "bright_cyan",
        "🔥": "bold bright_red", "🎉": "bright_yellow", "📌": "bright_cyan",
    }
    bullets = Text()
    for line in auto_lines:
        if not line.strip(): continue
        style = next((v for k, v in BULLET_STYLES.items() if line.startswith(f"- {k}")), "grey74")
        bullets.append("  " + line[2:] + "\n", style=style)

    renderables = []
    if any(l.strip() for l in auto_lines):
        renderables.append(bullets)

    if core_sections:
        if renderables:
            renderables.append(Rule(style="grey30"))
        for i, (title, body) in enumerate(core_sections):
            if i > 0:
                renderables.append(Rule(style="grey23"))
            color, icon = CORE_META.get(title, ("bright_white", "▌"))
            renderables.append(_render_section(title, body, color, icon))

    if renderables:
        console.print(Panel(
            Group(*renderables),
            title="[bold bright_white]📝  오늘의 AI 分析[/]",
            border_style="white",
            padding=(0, 1),
        ))

    if web_sections:
        web_renderables = []
        for i, (title, body) in enumerate(web_sections):
            if i > 0:
                web_renderables.append(Rule(style="grey23"))
            color, icon = WEB_META.get(title, ("bright_green", "🌐"))
            web_renderables.append(_render_section(title, body, color, icon))
        console.print(Panel(
            Group(*web_renderables),
            title="[bold bright_green]🌐  웹 인텔리전스[/]",
            border_style="green",
            padding=(0, 1),
        ))


def render_job_postings():
    intel  = get_web_intel()
    others = intel.get("other_jobs", [])
    if not others: return

    CAT_COLORS = {
        "DevOps·클라우드":  "bright_cyan",
        "IT기술영업·보안": "bright_yellow",
        "금융·핀테크":     "bright_magenta",
    }
    t = Text()
    t.append("\n")
    by_cat: dict[str, list] = {}
    for j in others:
        by_cat.setdefault(j.get("category", "기타"), []).append(j)

    for cat, items in by_cat.items():
        cat_color = CAT_COLORS.get(cat, "bright_white")
        t.append(f"  ◆ {cat}\n", style=f"bold {cat_color}")
        for item in items[:3]:
            title    = item.get("title", "")[:52]
            href     = item.get("href", "")
            url_disp = href[:58] + "…" if len(href) > 58 else href
            t.append(f"    · {title}\n", style="white")
            if href:
                t.append(f"      {url_disp}\n", style="grey74")
        t.append("\n")

    console.print(Panel(
        t,
        title="[bold bright_cyan]🔍  채용공고 탐색  (잡코리아 · 자소설닷컴)[/]",
        border_style="cyan",
        padding=(0, 1),
    ))


def render_curriculum(content: str):
    devops = parse_section_table(content, "DevOps")
    coding = parse_section_table(content, "코딩테스트")
    gsat   = parse_section_table(content, "GSAT · NCS")

    def make_table(rows, cols, border_color, title):
        if not rows: return None
        t = Table(
            box=box.SIMPLE_HEAD, border_style=border_color,
            show_header=True, header_style=f"bold {border_color}",
            expand=True, padding=(0, 1),
        )
        for name, ratio, justify in cols:
            t.add_column(name, ratio=ratio, justify=justify)
        for row in rows:
            vals = [row[i] if i < len(row) else "" for i in range(len(cols))]
            s = vals[1] if len(vals) > 1 else ""
            row_style = "grey58" if "✅" in s else f"bold {border_color}" if "🔄" in s else "bright_white"
            t.add_row(*vals, style=row_style)
        return Panel(
            t, title=f"[bold {border_color}]{title}[/]",
            border_style=border_color, padding=(0, 0),
        )

    panels = []
    p = make_table(devops,
        [("항목", 5, "left"), ("상태", 1, "center"), ("목표일", 2, "center")],
        "bright_blue", "🛠  DevOps 커리큘럼")
    if p: panels.append(p)

    p = make_table(coding,
        [("항목", 3, "left"), ("상태", 1, "center"), ("진행률", 2, "left"), ("목표일", 2, "center")],
        "bright_magenta", "💻 코딩테스트")
    if p: panels.append(p)

    p = make_table(gsat,
        [("항목", 5, "left"), ("상태", 1, "center"), ("목표일", 2, "center")],
        "bright_cyan", "📚 GSAT · NCS")
    if p: panels.append(p)

    for panel in panels:
        console.print(panel)
        console.print()


def render_week(content: str):
    rows = parse_week(content)
    if not rows: return
    t = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0, 2))
    t.add_column("날짜", ratio=2, no_wrap=True)
    t.add_column("내용", ratio=7)
    for row in rows:
        is_today = "오늘" in row[0]
        t.add_row(
            row[0],
            row[1] if len(row) > 1 else "",
            style="bold bright_yellow" if is_today else "grey74",
        )
    console.print(Panel(
        t, title="[bold bright_green]📅  이번 주 일정[/]",
        border_style="green", padding=(0, 0),
    ))


def render_footer():
    console.print()
    console.print(Rule(style="grey35"))
    console.print("[grey58]  [bold white]check[/] / [bold white]uncheck[/] 항목명   "
                  "[bold white]dash[/] 갱신   [bold white]cl[/] 체크만   "
                  "[bold white]night[/] 마무리[/]")
    console.print("[grey58]  [bold white]rerun[/] 웹+AI 재실행   [bold white]reai[/] AI만   "
                  "[bold white]accept[/] / [bold white]decline[/] 기술제안   "
                  "[bold white]jobcheck[/] 채용파일[/]")
    console.print()


# ── 메인 ─────────────────────────────────────────────────────────────────────

def render():
    content = read_progress()
    render_header()
    render_dday()
    console.print()
    render_checklist(content)
    console.print()
    render_analysis(content)
    console.print()
    render_job_postings()
    console.print()
    render_week(content)
    console.print()
    render_curriculum(content)
    render_footer()


def render_checklist_only():
    render_checklist(read_progress())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "checklist":
        render_checklist_only()
    else:
        render()
