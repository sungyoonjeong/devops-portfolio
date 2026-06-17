#!/usr/bin/env python3
"""
job_watch.py — 취업준비2026 폴더 변경 감지 + 내용 분석
사용법:
  jobcheck         → 새 파일 / 변경 파일 탐지 후 내용 요약 출력
  jobcheck --all   → 전체 파일 재분석

윈도우 바탕화면 경로: /mnt/c/Users/jeong/OneDrive/Desktop/취업준비2026
분석 결과: _system/job_notes/ 폴더에 저장
매니페스트: _system/job_manifest.json
"""
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

JOB_DIR = Path("/mnt/c/Users/jeong/OneDrive/Desktop/취업준비2026")
NOTES_DIR = Path("/home/jsy/devops-portfolio/_system/job_notes")
MANIFEST_FILE = Path("/home/jsy/devops-portfolio/_system/job_manifest.json")

SKIP_EXT = {".png", ".jpg", ".gif", ".jpeg", ".hwp", ".gif", ".xlsx", ".doc"}
TEXT_EXT = {".txt", ".md", ".html"}
DOCX_EXT = {".docx"}
PDF_EXT = {".pdf"}


def extract_text(path: Path, timeout: int = 15) -> str:
    import signal

    def _handler(signum, frame):
        raise TimeoutError()

    ext = path.suffix.lower()
    signal.signal(signal.SIGALRM, _handler)
    signal.alarm(timeout)
    try:
        if ext in TEXT_EXT:
            return path.read_text(encoding="utf-8", errors="ignore")[:8000]
        elif ext in DOCX_EXT:
            from docx import Document
            doc = Document(str(path))
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())[:8000]
        elif ext in PDF_EXT:
            from pdfminer.high_level import extract_text as pdf_extract
            text = pdf_extract(str(path))
            return (text or "")[:8000]
    except TimeoutError:
        return f"[타임아웃: {timeout}s 초과]"
    except Exception as e:
        return f"[추출 실패: {e}]"
    finally:
        signal.alarm(0)
    return ""


def scan_files() -> dict:
    result = {}
    for f in JOB_DIR.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() in SKIP_EXT:
            continue
        rel = str(f.relative_to(JOB_DIR))
        result[rel] = {
            "mtime": f.stat().st_mtime,
            "size": f.stat().st_size,
            "path": str(f),
        }
    return result


def load_manifest() -> dict:
    if MANIFEST_FILE.exists():
        return json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    return {}


def save_manifest(manifest: dict):
    MANIFEST_FILE.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def save_note(rel_path: str, content: str):
    NOTES_DIR.mkdir(exist_ok=True)
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", rel_path)
    note_file = NOTES_DIR / (safe_name + ".txt")
    note_file.write_text(content, encoding="utf-8")


def load_note(rel_path: str) -> str:
    safe_name = re.sub(r'[\\/:*?"<>|]', "_", rel_path)
    note_file = NOTES_DIR / (safe_name + ".txt")
    if note_file.exists():
        return note_file.read_text(encoding="utf-8")
    return ""


def main():
    force_all = "--all" in sys.argv
    silent    = "--silent" in sys.argv  # 터미널 자동 실행 시 변경 없으면 무출력

    # Windows 드라이브 미마운트 시 조용히 종료
    if not JOB_DIR.exists():
        if not silent:
            print("[job_watch] 취업준비2026 폴더 없음 (Windows 드라이브 미마운트)")
        return

    current  = scan_files()
    manifest = load_manifest()

    new_files, changed_files, removed_files = [], [], []
    for rel, info in current.items():
        if rel not in manifest:
            new_files.append(rel)
        elif abs(info["mtime"] - manifest[rel].get("mtime", 0)) > 1:
            changed_files.append(rel)
    for rel in manifest:
        if rel not in current:
            removed_files.append(rel)

    if force_all:
        to_analyze = list(current.keys())
    else:
        to_analyze = new_files + changed_files

    # 변경 없으면 무소음 종료 (자동 실행 시)
    if not to_analyze and not removed_files:
        if not silent:
            print(f"✅ 변경사항 없음 — {len(manifest)}개 파일 추적 중\n")
        return

    # 변경 있을 때만 출력
    print(f"\n📂 취업준비2026 변경 감지됨\n")
    if new_files:
        print(f"  🆕 신규 {len(new_files)}개:")
        for f in new_files: print(f"     + {f}")
    if changed_files:
        print(f"  ✏️  변경 {len(changed_files)}개:")
        for f in changed_files: print(f"     ~ {f}")
    if removed_files:
        print(f"  🗑  삭제 {len(removed_files)}개:")
        for f in removed_files:
            print(f"     - {f}")
            manifest.pop(f, None)

    print(f"\n  📄 {len(to_analyze)}개 파일 내용 파악 중...\n")
    for rel in to_analyze:
        info = current[rel]
        path = Path(info["path"])
        print(f"  ▶ {rel}")
        text = extract_text(path)
        if text and not text.startswith("[추출 실패"):
            preview = text[:300].replace("\n", " ").strip()
            print(f"    └ {preview[:120]}...")
            save_note(rel, text)
            manifest[rel] = {**info, "analyzed": datetime.now().isoformat(), "note_saved": True}
        else:
            print(f"    └ {text or '내용 없음'}")
            manifest[rel] = {**info, "analyzed": datetime.now().isoformat(), "note_saved": False}

    save_manifest(manifest)
    print(f"\n  ✅ 완료. 총 {len(manifest)}개 파일 추적 중\n")


if __name__ == "__main__":
    main()
