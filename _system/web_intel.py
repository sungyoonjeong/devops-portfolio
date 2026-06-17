#!/usr/bin/env python3
"""
web_intel.py — 매일 아침 취업 정보 웹 수집
- 잡코리아·자소설닷컴: DDG site: 검색 + JD 본문 크롤링
- JD 크롤링 실패 시 DDG 스니펫을 fallback으로 사용 → 요구기술 추출성공률 향상
- 커뮤니티·IT트렌드·시험 정보 수집
결과: /tmp/web_intel_YYYYMMDD.json
"""
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import date, timedelta, datetime
from pathlib import Path

MARKER = Path(f"/tmp/.web_intel_{date.today().strftime('%Y%m%d')}")
OUTPUT  = Path(f"/tmp/web_intel_{date.today().strftime('%Y%m%d')}.json")

JOB_CATEGORIES = [
    ("DevOps·클라우드",  ["DevOps", "클라우드엔지니어", "인프라엔지니어", "쿠버네티스"]),
    ("IT기술영업·보안",  ["IT기술영업", "보안영업", "솔루션영업", "네트워크영업"]),
    ("금융·핀테크",      ["금융IT", "핀테크", "IT운영"]),
]
NOISE = [
    "youtube", "instagram", "facebook", "twitter", "google.com",
    "fliphtml", "blog.naver", "tistory", "таро", "Поиск",
]

# JD 크롤링 허용 도메인
# 잡코리아·자소설닷컴은 JS 렌더링 필요, urllib 크롤링 불가 → 스니펫 fallback 사용
JD_DOMAINS = ("wanted.co.kr",)  # wanted만 정적 페이지 크롤링 시도

# 크롤링 제한
MAX_JD_CRAWL  = 10
CRAWL_TIMEOUT = 10


# ── JD 크롤러 ──────────────────────────────────────────────────────────────────

def _is_individual_jd_url(url: str) -> bool:
    """목록/카테고리 페이지는 False, 개별 JD 페이지만 True"""
    jd_patterns = [
        r"jobkorea\.co\.kr/Recruit/GI",
        r"jobkorea\.co\.kr/recruit/gi/\d+",
        r"jasoseol\.com/recruit/\d+",
        r"wanted\.co\.kr/wd/\d+",
    ]
    if any(re.search(p, url, re.IGNORECASE) for p in jd_patterns):
        return True
    # 블랙리스트: 목록/검색/테마 페이지
    skip_patterns = [
        "/Recruit/Search", "search?", "stext=", "/Theme/", "/starter/",
        "/company/", "jasoseol.com/recruit?", "m.saramin.co.kr",
        "/category/", "joblist", "search.saramin", "/main",
    ]
    return not any(p.lower() in url.lower() for p in skip_patterns)


def fetch_jd(url: str) -> str:
    """채용 공고 페이지 → 주요 텍스트 추출 (최대 1500자). 실패 시 빈 문자열."""
    if not any(d in url for d in JD_DOMAINS):
        return ""
    if not _is_individual_jd_url(url):
        return ""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    for attempt in range(2):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=CRAWL_TIMEOUT) as resp:
                raw = resp.read()
                # gzip 자동 해제
                if resp.info().get("Content-Encoding") == "gzip":
                    import gzip
                    raw = gzip.decompress(raw)
                html = raw.decode("utf-8", errors="ignore")
            break
        except Exception:
            if attempt == 0:
                time.sleep(1)
            else:
                return ""

    # HTML 정리
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>',  '', text,  flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    # 직무 관련 핵심 구간 추출
    keywords = ["자격요건", "우대사항", "주요업무", "담당업무", "필수역량",
                "우대조건", "지원자격", "역량검사", "인적성", "전형절차",
                "Docker", "Kubernetes", "Terraform", "AWS", "CI/CD"]
    best_start = 0
    best_score = 0
    window = 800
    for i in range(0, max(1, len(text) - window), 100):
        chunk = text[i:i+window]
        score = sum(1 for kw in keywords if kw in chunk)
        if score > best_score:
            best_score, best_start = score, i

    return text[best_start:best_start+1500].strip()


def crawl_jd_list(jobs: list[dict], limit: int = MAX_JD_CRAWL) -> list[dict]:
    """
    1단계: DDG 스니펫(body)을 모든 job에 fallback jd_text로 설정
    2단계: URL 있는 job에 한해 전체 JD 크롤링 시도 (limit 개 까지)
           성공하면 스니펫을 전체 JD로 교체
    """
    # 1단계: snippet fallback
    for job in jobs:
        body = job.get("body", "")
        if body and not job.get("jd_text"):
            job["jd_text"] = f"[검색 스니펫] {body}"

    # 2단계: 전체 JD 크롤링
    full_crawled = 0
    for job in jobs:
        if full_crawled >= limit:
            break
        url = job.get("url") or job.get("href", "")
        if not url:
            continue
        jd = fetch_jd(url)
        if jd:
            job["jd_text"] = jd  # 전체 JD로 스니펫 교체
            full_crawled += 1
        time.sleep(0.5)

    return jobs


# ── DDG 검색 ──────────────────────────────────────────────────────────────────

def ddg_search(query: str, max_results: int = 5) -> list[dict]:
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {
                "title": r.get("title", ""),
                "body":  r.get("body", "")[:500],   # 스니펫 최대 500자 (기존 200→500)
                "href":  r.get("href", ""),
            }
            for r in results
            if not any(n in r.get("href","").lower() or n in r.get("title","").lower() for n in NOISE)
        ]
    except Exception as e:
        print(f"[web_intel] DDG 검색 실패: {e}", file=sys.stderr)
        return []


def get_other_jobs() -> list[dict]:
    """잡코리아·자소설닷컴 DDG site: 검색 — 개별 공고 URL 위주로 수집"""
    jk_site = "site:jobkorea.co.kr/Recruit/GI"
    js_site = "site:jasoseol.com/recruit"
    results = []
    for label, keywords in JOB_CATEGORIES:
        kw_str = " OR ".join(keywords)
        for site in (jk_site, js_site):
            q    = f'({site}) ({kw_str}) 신입'
            hits = ddg_search(q, max_results=4)
            for h in hits:
                h["category"] = label
                h["source"]   = "잡코리아/자소설닷컴"
            results.extend(hits)
    return results


# ── 시험 정보 서치 ─────────────────────────────────────────────────────────────

def get_exam_info() -> list[dict]:
    queries = [
        "DevOps 클라우드 엔지니어 신입 채용 역량검사 인적성 전형 절차 2025 2026",
        "IT 기업 신입 역량검사 종류 준비방법 삼성 SK LG 카카오 네이버",
        "클라우드 보안 IT기술영업 채용 코딩테스트 없는 기업 전형",
    ]
    results = []
    for q in queries:
        results.extend(ddg_search(q, max_results=3))
    return results


# ── 메인 ───────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not args.force and MARKER.exists():
        sys.exit(0)

    t0 = time.time()
    print("[web_intel] 수집 시작...")

    # 잡코리아·자소설닷컴 DDG + 크롤링
    print("  잡코리아·자소설닷컴 검색...", end=" ", flush=True)
    other_jobs = get_other_jobs()
    print(f"{len(other_jobs)}건")
    print("  JD 크롤링 (실패 시 스니펫 fallback)...", end=" ", flush=True)
    other_jobs = crawl_jd_list(other_jobs, limit=MAX_JD_CRAWL)
    jd_full    = sum(1 for j in other_jobs if j.get("jd_text") and not j["jd_text"].startswith("[검색 스니펫]"))
    jd_snippet = sum(1 for j in other_jobs if j.get("jd_text") and     j["jd_text"].startswith("[검색 스니펫]"))
    print(f"전체JD {jd_full}건 · 스니펫 {jd_snippet}건")

    # 커뮤니티·트렌드·시험
    print("  커뮤니티·트렌드·시험 정보...", end=" ", flush=True)
    community = ddg_search("DevOps 신입 취업 후기 스펙 링커리어 독취사 2026", 5)
    # it_trends: site: OR 복합 쿼리가 DDG에서 동작 안 함 → 단순 키워드로
    it_trends = ddg_search("DevOps 클라우드 엔지니어 트렌드 2026 기술 스택", 4)
    it_trends += ddg_search("Kubernetes IDP GitOps 플랫폼 엔지니어링 2026", 3)
    cka_tips  = ddg_search("CKA 합격 후기 공부법 2025 2026", 4)
    exam_info = get_exam_info()
    print("완료")

    intel = {
        "date":         date.today().isoformat(),
        "saramin_jobs": [],          # 사람인 API 미사용
        "other_jobs":   other_jobs,
        "community":    community,
        "it_trends":    it_trends,
        "cka_tips":     cka_tips,
        "exam_info":    exam_info,
    }

    OUTPUT.write_text(json.dumps(intel, ensure_ascii=False, indent=2), encoding="utf-8")
    MARKER.touch()

    elapsed = time.time() - t0
    total   = sum(len(v) for v in intel.values() if isinstance(v, list))
    print(f"[web_intel] 완료 — {total}건, 소요 {elapsed:.0f}초")


if __name__ == "__main__":
    main()
