#!/usr/bin/env python3
"""
git_progress_update.py — git commit 후 PROGRESS.md 체크리스트 자동 업데이트
post-commit hook에서 호출됨. 백그라운드로 실행되므로 git push를 막지 않음.
"""
import re
import subprocess
import sys
from pathlib import Path

PROGRESS_FILE = Path("/home/jsy/devops-portfolio/_system/PROGRESS.md")
REPO_ROOT = Path("/home/jsy/devops-portfolio")
HEADER_RE = re.compile(r"^##\s*✅.*(오늘|체크리스트)", re.MULTILINE)


def get_committed_md_files() -> list[str]:
    try:
        # HEAD^ 가 없는 첫 커밋 대비
        r = subprocess.run(
            ["git", "diff", "--name-only", "HEAD^", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT)
        )
        if r.returncode != 0:
            r = subprocess.run(
                ["git", "diff", "--name-only", "--cached"],
                capture_output=True, text=True, cwd=str(REPO_ROOT)
            )
        files = [f.strip() for f in r.stdout.strip().split("\n") if f.strip()]
        return [f for f in files if f.endswith(".md") and not f.startswith("_system/")]
    except Exception:
        return []


def get_checklist_items(content: str) -> list[str]:
    items = []
    in_cl = False
    for line in content.split("\n"):
        if HEADER_RE.search(line):
            in_cl = True
            continue
        if in_cl:
            if line.startswith("##") and "체크리스트" not in line:
                break
            m = re.match(r"^- \[ \] (.+)", line)
            if m:
                items.append(m.group(1).strip())
    return items


def check_item(content: str, item_text: str) -> str:
    return content.replace(f"- [ ] {item_text}", f"- [x] {item_text}", 1)


def build_prompt(md_files: list[str], checklist_items: list[str]) -> str:
    file_list = "\n".join(f"  - {f}" for f in md_files)
    cl_list = "\n".join(f"  - {i}" for i in checklist_items)

    # 커밋된 파일 내용 샘플 (각 파일 첫 200자)
    samples = []
    for f in md_files[:5]:
        fp = REPO_ROOT / f
        try:
            text = fp.read_text(encoding="utf-8")[:200].replace("\n", " ")
            samples.append(f"  [{f}]: {text}")
        except Exception:
            samples.append(f"  [{f}]: (읽기 실패)")
    sample_text = "\n".join(samples)

    return f"""아래는 정성윤이 방금 git commit한 .md 파일 목록이다.
오늘 체크리스트 항목 중 이 커밋으로 완료된 것이 있으면 정확히 알려줘.

커밋된 파일:
{file_list}

파일 내용 샘플:
{sample_text}

오늘 체크리스트 (미완료 항목만):
{cl_list}

━━━ 출력 형식 ━━━
완료된 항목이 있으면 아래 형식으로만 출력. 없으면 "없음" 한 줄만.

DONE|체크리스트 항목 텍스트 (위 목록에서 정확히 복사)
DONE|...

규칙:
- 파일 경로·내용이 체크리스트 항목과 명확히 연관될 때만 DONE 출력
- 불확실하면 출력하지 않음
- 추측 금지"""


def main():
    md_files = get_committed_md_files()
    if not md_files:
        sys.exit(0)

    if not PROGRESS_FILE.exists():
        sys.exit(0)

    content = PROGRESS_FILE.read_text(encoding="utf-8")
    checklist_items = get_checklist_items(content)
    if not checklist_items:
        sys.exit(0)

    prompt = build_prompt(md_files, checklist_items)

    try:
        result = subprocess.run(
            ["claude", "-p", prompt, "--model", "claude-haiku-4-5-20251001"],
            capture_output=True, text=True, timeout=60,
            cwd=str(REPO_ROOT)
        )
    except Exception as e:
        print(f"[git_progress] 실패: {e}", file=sys.stderr)
        sys.exit(0)

    if result.returncode != 0 or not result.stdout.strip():
        sys.exit(0)

    raw = result.stdout.strip()
    if raw.strip() == "없음":
        sys.exit(0)

    checked = []
    for line in raw.splitlines():
        if line.startswith("DONE|"):
            item = line[5:].strip()
            if item in checklist_items:
                content = check_item(content, item)
                checked.append(item)

    if checked:
        PROGRESS_FILE.write_text(content, encoding="utf-8")
        print(f"[git_progress] 자동 체크: {', '.join(checked)}")


if __name__ == "__main__":
    main()
