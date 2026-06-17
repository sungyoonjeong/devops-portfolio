#!/usr/bin/env python3
"""
suggest_cmd.py — 대시보드 AI 제안에 대한 즉각 응답
accept [기술명]  → PROGRESS.md 커리큘럼에 자동 추가
decline [기술명] → 스킵 목록에 기록 (다음 분석부터 제안 안 함)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PROGRESS_FILE = Path("/home/jsy/devops-portfolio/_system/PROGRESS.md")
SKIP_FILE     = Path("/home/jsy/devops-portfolio/_system/skip_suggestions.json")


def load_skip() -> list[str]:
    try:
        return json.loads(SKIP_FILE.read_text(encoding="utf-8")) if SKIP_FILE.exists() else []
    except Exception:
        return []


def save_skip(lst: list[str]):
    SKIP_FILE.write_text(json.dumps(lst, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_decline(tech: str):
    skips = load_skip()
    if tech in skips:
        print(f"[decline] '{tech}' 는 이미 스킵 목록에 있음")
        return
    skips.append(tech)
    save_skip(skips)
    print(f"[decline] '{tech}' 스킵 목록에 추가 — 다음 분석부터 제안 안 함")


def cmd_accept(tech: str):
    if not PROGRESS_FILE.exists():
        print("[accept] PROGRESS.md 없음", file=sys.stderr)
        sys.exit(1)

    content = PROGRESS_FILE.read_text(encoding="utf-8")

    prompt = f"""정성윤(DevOps 취업 준비생)의 커리큘럼에 '{tech}' 를 추가한다.

현재 커리큘럼 전체 (DevOps / 코딩테스트 / GSAT·NCS 3개 테이블):
{_extract_curriculum_tables(content)}

━━━ 출력 형식 (정확히 지켜라) ━━━

<<<PLAN>>>
[3~6줄. 왜 지금 이 시점에 이 기술이 필요한지 + 어떤 테이블(DevOps/코딩테스트/GSAT)에 어디 배치했는지 근거]

학습 계획:
  · 예상 소요: N일 (기존 커리큘럼 밀도 고려)
  · 선행 조건: [이미 커리큘럼에서 배운 것 중 연관 항목]
  · 학습 순서: ① → ② → ③ (구체적 단계)
  · 추천 자료: [무료 공식 문서 or 유튜브 채널 or 실습 환경 — 실제 존재하는 것만]
  · 포트폴리오 연결: [기존 PF1/PF2/PF-K8s 중 어디에 통합할 수 있는지]
<<<END_PLAN>>>

<<<TABLE>>>
INSERT_AFTER|[바로 앞에 올 기존 행의 항목명 — 테이블 셀과 공백 포함 정확히 일치]
NEW_ROW|{tech}|⬜|[목표일 범위]
<<<END_TABLE>>>

규칙:
- INSERT_AFTER 는 현재 커리큘럼 테이블 셀 텍스트와 정확히 일치해야 함
- NEW_ROW 컬럼 수: DevOps·GSAT 테이블은 3컬럼(항목|상태|목표일), 코딩테스트 테이블은 4컬럼(항목|상태|진행률|목표일) — 배치될 테이블에 맞게 컬럼 수 선택
- 예상 소요일은 기존 항목들 밀도(K8s=3주, Terraform=5일 등) 대비 현실적으로
- 추천 자료는 실제 존재하는 공식 문서/채널만 (지어내기 금지)
- PLAN은 한국어로"""

    print(f"\n[accept] '{tech}' 학습 계획 수립 중...", end=" ", flush=True)

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", "claude-sonnet-4-6"],
            capture_output=True, text=True, timeout=90,
        )
    except Exception as e:
        print(f"실패: {e}", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0 or not result.stdout.strip():
        print(f"실패\n{result.stderr[:300]}", file=sys.stderr)
        sys.exit(1)

    raw = result.stdout.strip()

    # 계획 파싱
    plan_match = re.search(r'<<<PLAN>>>\n(.*?)<<<END_PLAN>>>', raw, re.DOTALL)
    plan_text  = plan_match.group(1).strip() if plan_match else ""

    # 테이블 삽입 파싱
    table_match = re.search(r'<<<TABLE>>>\n(.*?)<<<END_TABLE>>>', raw, re.DOTALL)
    after_item, new_row = None, None
    if table_match:
        for line in table_match.group(1).splitlines():
            line = line.strip()
            if line.startswith("INSERT_AFTER|"):
                after_item = line[len("INSERT_AFTER|"):].strip()
            elif line.startswith("NEW_ROW|"):
                parts = [p.strip() for p in line[len("NEW_ROW|"):].split("|")]
                if len(parts) >= 4:
                    # 4컬럼 (코딩테스트: 항목|상태|진행률|목표일)
                    new_row = f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} |"
                elif len(parts) >= 3:
                    # 3컬럼 (DevOps·GSAT: 항목|상태|목표일)
                    new_row = f"| {parts[0]} | {parts[1]} | {parts[2]} |"

    print("완료\n")

    # 학습 계획 출력
    sep = "─" * 60
    print(sep)
    print(f"  ✅ '{tech}' 커리큘럼 추가 — 학습 계획")
    print(sep)
    if plan_text:
        for line in plan_text.split("\n"):
            print(f"  {line}")
    print(sep)

    if not after_item or not new_row:
        print(f"\n[accept] 테이블 파싱 실패 — 수동으로 추가해줘")
        print(f"  {new_row or '(행 생성 실패)'}")
        sys.exit(1)

    # PROGRESS.md 테이블에 삽입 — 현황 요약 섹션 안에서만 매칭
    lines      = content.split("\n")
    new_lines  = []
    inserted   = False
    in_summary = False
    for line in lines:
        new_lines.append(line)
        if "## 📊 현황 요약" in line:
            in_summary = True
        elif in_summary and line.startswith("## ") and "현황" not in line:
            in_summary = False
        # 현황 요약 섹션 안 커리큘럼 테이블 행에서만 매칭
        if (in_summary and after_item in line
                and line.strip().startswith("|") and "---" not in line
                and not inserted):
            new_lines.append(new_row)
            inserted = True

    if not inserted:
        print(f"\n[accept] '{after_item}' 행을 찾지 못함 — 수동 추가 필요:")
        print(f"  {new_row}")
        sys.exit(1)

    PROGRESS_FILE.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"\n  → PROGRESS.md 커리큘럼에 추가됨: {new_row}")
    print(f"  → `dash` 명령으로 업데이트된 커리큘럼 확인\n")


def _extract_curriculum_tables(content: str) -> str:
    """DevOps·코딩테스트·GSAT·NCS 3개 테이블 전부 추출"""
    lines, in_summary = [], False
    for line in content.split("\n"):
        if "## 📊 현황 요약" in line:
            in_summary = True
            continue
        if in_summary:
            if line.startswith("## ") and "현황" not in line:
                break
            lines.append(line)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 3:
        print("사용법: accept [기술명] / decline [기술명]")
        sys.exit(1)

    cmd  = sys.argv[1].lower()
    tech = " ".join(sys.argv[2:]).strip()

    if cmd == "accept":
        cmd_accept(tech)
    elif cmd == "decline":
        cmd_decline(tech)
    else:
        print(f"알 수 없는 명령: {cmd}  (accept / decline 만 가능)")
        sys.exit(1)


if __name__ == "__main__":
    main()
