#!/usr/bin/env python3
"""
claude_morning.py — 터미널 첫 오픈 시 AI 분석 자동 업데이트
1. PROGRESS.md 전체를 prompt에 넣어 claude -p 호출
2. Claude는 분석 텍스트 + 구조화된 업데이트 지시 두 섹션으로 출력
3. 스크립트가 PROGRESS.md를 파싱해서 업데이트 적용
4. **[Claude 분석]** 블록 교체
하루 1회 실행 (마커 파일).
"""
import os
import re
import sys
import json
import subprocess
import tempfile
from datetime import date, datetime
from pathlib import Path

PROGRESS_FILE = Path("/home/jsy/devops-portfolio/_system/PROGRESS.md")
SKIP_FILE     = Path("/home/jsy/devops-portfolio/_system/skip_suggestions.json")
MARKER_FILE   = Path(f"/tmp/.claude_morning_{date.today().strftime('%Y%m%d')}")

BLOCK_RE    = re.compile(r'(\*\*\[Claude [^\]]+\]\*\*\n).*?(\n+---\n)', re.DOTALL)
PLAN_ROW_RE = re.compile(r'(## 📋 체크리스트 계획표.*?\n(?:\|.*\n)*\|---.*\n)((?:\|.*\n)*)', re.DOTALL)
WEEK_RE     = re.compile(r'(## 이번 주 일정\n\n\|.*\n\|.*\n)((?:\|.*\n)*)', re.DOTALL)

WEB_INTEL_FILE = Path(f"/tmp/web_intel_{date.today().strftime('%Y%m%d')}.json")


def load_web_intel() -> str:
    if not WEB_INTEL_FILE.exists():
        return ""
    try:
        data = json.loads(WEB_INTEL_FILE.read_text(encoding="utf-8"))
        lines = []

        # 사람인 JD (본문 포함)
        saramin = [j for j in data.get("saramin_jobs", []) if j.get("jd_text")]
        if saramin:
            lines.append("=== 사람인 채용공고 JD (마감 D+4) ===")
            for j in saramin[:5]:
                lines.append(f"[{j.get('company','')} / {j.get('title','')} / 마감:{j.get('deadline','')}]")
                lines.append(j["jd_text"][:600])
                lines.append("")

        # 잡코리아·자소설닷컴 JD (본문 포함)
        other = [j for j in data.get("other_jobs", []) if j.get("jd_text")]
        if other:
            lines.append("=== 잡코리아·자소설닷컴 채용공고 JD ===")
            for j in other[:5]:
                lines.append(f"[{j.get('title','')} / {j.get('href','')}]")
                lines.append(j["jd_text"][:600])
                lines.append("")

        # JD 없는 공고 타이틀만 (스니펫도 없는 완전 미확보)
        no_jd = [j for j in data.get("other_jobs",[]) if not j.get("jd_text")]
        if no_jd:
            lines.append("=== 기타 공고 (정보 미확보) ===")
            for j in no_jd[:6]:
                lines.append(f"• {j.get('title') or j.get('company','')}")

        # 시험 정보
        exam = data.get("exam_info", [])
        if exam:
            lines.append("=== 채용 전형·시험 정보 ===")
            for r in exam[:4]:
                lines.append(f"• {r['title']}: {r['body'][:150]}")

        # 커뮤니티
        community = data.get("community", [])
        if community:
            lines.append("=== 커뮤니티 동향 ===")
            for r in community[:4]:
                lines.append(f"• {r['title']}: {r['body'][:120]}")

        # IT 트렌드
        trends = data.get("it_trends", [])
        if trends:
            lines.append("=== IT 트렌드 ===")
            for r in trends[:4]:
                lines.append(f"• {r['title']}: {r['body'][:120]}")

        # CKA
        cka = data.get("cka_tips", [])
        if cka:
            lines.append("=== CKA 정보 ===")
            for r in cka[:3]:
                lines.append(f"• {r['title']}: {r['body'][:120]}")

        return "\n".join(lines)
    except Exception:
        return ""


def load_skip_list() -> list[str]:
    try:
        return json.loads(SKIP_FILE.read_text(encoding="utf-8")) if SKIP_FILE.exists() else []
    except Exception:
        return []


def build_prompt(content: str, now: datetime, web_intel: str = "", skip_list: list = None) -> str:
    weekdays = ["월", "화", "수", "목", "금", "토", "일"]
    day_kor = weekdays[now.weekday()]

    skip_section = ""
    if skip_list:
        skip_section = f"\n[공고 갭 분析에서 제외할 기술 — 사용자가 이미 decline 결정]: {', '.join(skip_list)}\n"

    web_section = ""
    if web_intel:
        web_section = f"""
--- 오늘의 웹 인텔리전스 (검색 결과 원문) ---
{web_intel}
---
{skip_section}"""

    return f"""오늘: {now.strftime(f'%Y년 %m월 %d일({day_kor}) %H시 %M분')}

너는 DevOps 취업 준비생 정성윤의 전담 학습 코치다. 아래 PROGRESS.md와 오늘의 웹 인텔리전스를 분석하고, 지정된 형식으로 출력해라.

--- PROGRESS.md ---
{content}
---
{web_section}

━━━ 절대 규칙: 출력 형식 ━━━

❌ 이렇게 하면 출력 불가 처리됨 (절대 금지):
**[어제 실적]** 4/7 완료(57%). 신찬수 47~51강 완료. GSAT 미완. NCS 미완 → 이월.

✅ 반드시 이렇게 — 한 줄에 한 항목:
**[어제 실적]** 4/7 완료 (57%)
· 신찬수 47~51강 ✅
· Level 1 5문제 ✅
· 기업공고 확인 ✅
· GSAT 수리 2섹션 → 미완, 오늘 이월
· NCS 2~4회차 → 미완, 오늘 이월

핵심 규칙:
- 한 줄 = 한 항목 (예외 없음)
- · 로 시작하는 각 줄에 항목 1개만
- 문단이나 긴 문장으로 묶어 쓰지 말 것
- 섹션 첫 줄: 결론·수치만 (30자 이내)
- 섹션 내 항목은 전부 · 로 시작하는 별도 줄에
- 섹션간 빈 줄 1개 필수

출력은 반드시 아래 두 섹션으로만 구성:

<<<ANALYSIS>>>

**[어제 실적]** N/M 완료 (XX%)
· (완료 항목 1개)
· (완료 항목 2개)
· (미완 항목 → 오늘 이월 영향)

**[일정 위험 신호]** (가장 위험한 것 1개 이름 + D-N)
· (세부 위험 근거)
· (구체적 대처법)

**[시험 D-day]** SAA D-N / OPIc D-N / CKA D-N
· (준비 상태 솔직 평가 — 위험도 높은 순서)

**[다가오는 Phase]** (다음 Phase 이름 + 시작까지 N일)
· (필요한 강의·자료 구체적 추천)
· (오늘 할 수 있는 사전 준비 1가지)

**[트랙별 페이스]** (코테/GSAT/NCS 세 줄 요약)
· 코테: (현황)
· GSAT: (현황)
· NCS: (현황)

**[오늘 우선순위]** ① (가장 중요한 것 이름)
· 이유: (왜 오늘 1순위인가 — 구체적 수치·마감 포함)
② (두 번째)
· 이유: (이유)

**[채용 동향]** 요구기술 TOP3 커버율 (공고 없으면 생략)
· (기술1): (공고 N건 등장)
· (기술2): ...
· 커리큘럼 커버율: X%

**[공고 갭 分析]** 커리큘럼에 없는 요구 기술 (공고 없으면 생략)
· (기술명): 공고 N건 등장 → 커리큘럼 추가 권고: [Phase] / 스킵 권고

**[시험·전형 준비]** 수집 공고 채용 전형 분析 (없으면 생략)
· (기업 유형): (필요 시험 종류)

**[IT 트렌드]** (DevOps 관련 핵심 동향, 웹 인텔 없으면 생략)
· (트렌드 1)

**[커뮤니티]** (취업 커뮤니티 인사이트, 웹 인텔 없으면 생략)
· (인사이트)

**[업데이트 사항]** UPDATES에서 적용한 변경 요약 (없으면 생략)

<<<END_ANALYSIS>>>

<<<UPDATES>>>
(아래 지시 타입만 사용. 필요 없으면 비워두거나 생략.)

# PLAN_ROW|날짜|항목1|항목2|항목3|항목4|항목5|항목6
# STATUS|항목명|새상태(✅/🔄/⬜)|새진행률(선택)
# WEEK|날짜|핵심 (오늘 포함 이번 주 전체, 한 줄씩)

<<<END_UPDATES>>>

━━━ 分析 규칙 ━━━
- 빈 칭찬·일반론·"꾸준히" 금지
- PROGRESS.md에 없는 사실 지어내기 금지
- 채용 동향·공고 갭·트렌드는 웹 인텔리전스 원문 기반으로 — 일반론 금지
- "[검색 스니펫]"으로 시작하는 JD도 기술 키워드 추출에 활용
- 공고 갭: 커버된 기술 언급 금지, 진짜 없는 것만, 빈도 근거 포함

━━━ UPDATES 규칙 ━━━
- 오늘부터 2주 후까지 계획표에 빈 날짜가 있으면 PLAN_ROW로 추가
- 완료 확인된 항목이 있으면 STATUS 업데이트
- 이번 주 일정이 현재 주와 맞지 않으면 WEEK로 교체"""

def parse_output(raw: str) -> tuple[str, list[dict]]:
    """<<<ANALYSIS>>>와 <<<UPDATES>>> 섹션 파싱"""
    analysis = ""
    updates = []

    a_match = re.search(r'<<<ANALYSIS>>>\n(.*?)<<<END_ANALYSIS>>>', raw, re.DOTALL)
    if a_match:
        analysis = a_match.group(1).strip()

    u_match = re.search(r'<<<UPDATES>>>\n(.*?)<<<END_UPDATES>>>', raw, re.DOTALL)
    if u_match:
        for line in u_match.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) < 2:
                continue
            cmd = parts[0].upper()
            if cmd == 'PLAN_ROW' and len(parts) >= 3:
                updates.append({'type': 'PLAN_ROW', 'date': parts[1], 'items': parts[2:]})
            elif cmd == 'STATUS' and len(parts) >= 3:
                updates.append({'type': 'STATUS', 'item': parts[1], 'status': parts[2],
                                'progress': parts[3] if len(parts) > 3 else None})
            elif cmd == 'WEEK' and len(parts) >= 3:
                updates.append({'type': 'WEEK', 'date': parts[1], 'core': parts[2]})

    return analysis, updates


def apply_plan_row(content: str, date_str: str, items: list[str]) -> str:
    """체크리스트 계획표에 날짜 행 추가 또는 교체"""
    # 이미 해당 날짜 행이 있으면 교체, 없으면 마지막 행 뒤에 추가
    padded = list(items) + ['—'] * (6 - len(items))
    new_row = '| ' + ' | '.join([date_str] + padded[:6]) + ' |'

    existing = re.compile(rf'^\|\s*{re.escape(date_str)}\s*\|.*$', re.MULTILINE)
    if existing.search(content):
        return existing.sub(new_row, content)

    # 계획표 마지막 행 뒤에 삽입
    table_end = re.compile(r'(## 📋 체크리스트 계획표.*?)(^\|[^\n]+\|$)(\n\n---)', re.DOTALL | re.MULTILINE)
    m = table_end.search(content)
    if m:
        return content[:m.end(2)] + '\n' + new_row + content[m.end(2):]
    return content


def apply_status(content: str, item: str, status: str, progress: str | None) -> str:
    """현황 요약 테이블에서 항목 상태 업데이트"""
    # 항목 행: | 항목명 | 상태 | ... |
    pattern = re.compile(
        rf'(\|\s*{re.escape(item)}\s*\|\s*)(✅|🔄|⬜)(\s*\|)',
    )
    if pattern.search(content):
        content = pattern.sub(rf'\g<1>{status}\3', content)

    if progress:
        prog_pattern = re.compile(
            rf'(\|\s*{re.escape(item)}\s*\|\s*(?:✅|🔄|⬜)\s*\|\s*)([^\|]+)(\|)',
        )
        content = prog_pattern.sub(rf'\g<1>{progress} \3', content)

    return content


def apply_week(content: str, week_rows: list[dict]) -> str:
    """이번 주 일정 테이블 교체"""
    if not week_rows:
        return content

    rows_text = '\n'.join(f"| {r['date']} | {r['core']} |" for r in week_rows)
    week_pattern = re.compile(
        r'(## 이번 주 일정\n\n\| 날짜 \| 핵심 \|\n\|---.*\n)((?:\|.*\n)*)',
        re.DOTALL
    )
    if week_pattern.search(content):
        return week_pattern.sub(r'\g<1>' + rows_text + '\n', content)
    return content



def safe_write(path: str, content: str):
    """원자적 파일 쓰기: 중단돼도 파일 손상 없음"""
    dir_ = os.path.dirname(str(path))
    with tempfile.NamedTemporaryFile("w", dir=dir_, suffix=".tmp",
                                     delete=False, encoding="utf-8") as f:
        f.write(content)
        tmp = f.name
    os.replace(tmp, str(path))


def update_analysis_block(content: str, analysis: str) -> tuple[str, bool]:
    new_content, count = BLOCK_RE.subn(
        lambda m: m.group(1) + analysis + m.group(2),
        content
    )
    return new_content, count > 0


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--force', action='store_true')
    parser.add_argument('--marker', default=None)
    args = parser.parse_args()

    marker = Path(args.marker) if args.marker else MARKER_FILE

    if not args.force and marker.exists():
        sys.exit(0)

    if not PROGRESS_FILE.exists():
        print("[claude_morning] PROGRESS.md 없음", file=sys.stderr)
        sys.exit(0)

    content = PROGRESS_FILE.read_text(encoding='utf-8')
    now = datetime.now()
    web_intel  = load_web_intel()
    skip_list  = load_skip_list()
    prompt     = build_prompt(content, now, web_intel, skip_list)

    print("[claude_morning] AI 분석 생성 중...", end=' ', flush=True)

    try:
        result = subprocess.run(
            ['claude', '-p', prompt, '--model', 'claude-sonnet-4-6'],
            capture_output=True, text=True, timeout=180,
        )
    except subprocess.TimeoutExpired:
        print("타임아웃 (180s)")
        sys.exit(1)
    except FileNotFoundError:
        print("claude CLI 없음")
        sys.exit(1)

    if result.returncode != 0 or not result.stdout.strip():
        print(f"실패\n{result.stderr[:300]}")
        sys.exit(1)

    raw = result.stdout.strip()
    analysis, updates = parse_output(raw)

    if not analysis:
        print("분석 섹션 없음 — 출력 형식 오류")
        sys.exit(1)

    # 업데이트 적용
    week_rows = [u for u in updates if u['type'] == 'WEEK']
    if week_rows:
        content = apply_week(content, week_rows)

    for u in updates:
        if u['type'] == 'PLAN_ROW':
            content = apply_plan_row(content, u['date'], u['items'])
        elif u['type'] == 'STATUS':
            content = apply_status(content, u['item'], u['status'], u.get('progress'))

    # 분석 블록 교체
    new_content, updated = update_analysis_block(content, analysis)

    if updated:
        safe_write(str(PROGRESS_FILE), new_content)
        marker.touch()
        n_updates = len([u for u in updates if u['type'] != 'WEEK']) + (1 if week_rows else 0)
        print(f"완료 (분석 {len(analysis)}자, 업데이트 {n_updates}건)")
    else:
        print("**[Claude 분석]** 블록 없음")


if __name__ == '__main__':
    main()
