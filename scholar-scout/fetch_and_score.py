#!/usr/bin/env python3
"""
fetch_and_score.py — Fetch, score, merge, dedup social science papers.

Data sources: OpenAlex (free, no key) + Semantic Scholar (free tier or API key).
Dual-source strategy:
  - OpenAlex: recent papers (last N days), sorted by date → catch newest
  - Semantic Scholar: high-cited papers (last 12 months) → catch trending

Usage:
    python3 fetch_and_score.py > /tmp/scholar_papers_top.json
    python3 fetch_and_score.py --days 7 > /tmp/scholar_papers_top.json
    python3 fetch_and_score.py --date 2026-03-01 > /tmp/scholar_papers_top.json

Stderr: progress logs.  Stdout: JSON array of top papers.
"""

import argparse
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

_SHARED_DIR = Path(__file__).resolve().parent.parent / "_shared"
if str(_SHARED_DIR) not in sys.path:
    sys.path.insert(0, str(_SHARED_DIR))

from scholar_config import daily_papers_config, daily_papers_dir, researcher_config

# ── Configuration ──────────────────────────────────────────────────────────

_CONFIG = daily_papers_config()
_RESEARCHER = researcher_config()

KEYWORDS = _CONFIG.get("keywords", [])
NEGATIVE_KEYWORDS = _CONFIG.get("negative_keywords", [])
DOMAIN_BOOST_KEYWORDS = _CONFIG.get("domain_boost_keywords", [])
MIN_SCORE = _CONFIG.get("min_score", 2)
TOP_N = _CONFIG.get("top_n", 10)

EMAIL = _RESEARCHER.get("email", "")
S2_API_KEY = _RESEARCHER.get("semantic_scholar_api_key", "")

DAILYPAPERS_DIR = daily_papers_dir()
HISTORY_PATH = DAILYPAPERS_DIR / ".history.json"


# ── Helpers ────────────────────────────────────────────────────────────────


def fetch_url(url: str, timeout: int = 30, headers: dict = None) -> str:
    """Fetch URL with basic error handling."""
    try:
        hdrs = {"User-Agent": "scholar-scout/1.0"}
        if headers:
            hdrs.update(headers)
        req = Request(url, headers=hdrs)
        with urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except HTTPError as e:
        print(f"  [WARN] HTTP {e.code} for {url}", file=sys.stderr)
        return ""
    except Exception as e:
        print(f"  [WARN] fetch failed {url}: {e}", file=sys.stderr)
        return ""


def reconstruct_abstract(inverted_index: dict) -> str:
    """Reconstruct abstract from OpenAlex inverted index format."""
    if not inverted_index:
        return ""
    word_positions = []
    for word, positions in inverted_index.items():
        for pos in positions:
            word_positions.append((pos, word))
    word_positions.sort()
    return " ".join(word for _, word in word_positions)


def normalize_doi(doi: str) -> str:
    """Extract clean DOI from various formats."""
    if not doi:
        return ""
    doi = doi.strip()
    # Remove URL prefix
    for prefix in ["https://doi.org/", "http://doi.org/", "https://dx.doi.org/"]:
        if doi.startswith(prefix):
            doi = doi[len(prefix):]
    return doi.lower()


# ── Scoring ────────────────────────────────────────────────────────────────


def score_paper(paper: dict) -> int:
    """Score a paper based on keyword matching and citation metrics."""
    text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()
    title_lower = paper.get("title", "").lower()

    # 1. Negative keywords → instant reject
    for neg in NEGATIVE_KEYWORDS:
        if neg.lower() in text:
            return -999

    score = 0

    # 2. Positive keywords (title +3, abstract +1)
    keyword_hits = 0
    for kw in KEYWORDS:
        kw_lower = kw.lower()
        if kw_lower in title_lower:
            score += 3
            keyword_hits += 1
        elif kw_lower in text:
            score += 1
            keyword_hits += 1

    # 3. Domain boost keywords (+1 for 1 hit, +2 for 2+ hits)
    domain_hits = sum(1 for kw in DOMAIN_BOOST_KEYWORDS if kw.lower() in text)
    if domain_hits >= 2:
        score += 2
    elif domain_hits == 1:
        score += 1

    # 4. Citation boost (for high-cited source)
    cited = paper.get("cited_by_count", 0) or 0
    if cited >= 50:
        score += 3
    elif cited >= 20:
        score += 2
    elif cited >= 5:
        score += 1

    # 5. Journal quality boost
    journal = (paper.get("journal", "") or "").lower()
    # Known high-impact social science journals
    top_journals = [
        "computers in human behavior",
        "journal of personality and social psychology",
        "psychological bulletin",
        "communication research",
        "new media & society",
        "journal of computer-mediated communication",
        "cyberpsychology, behavior, and social networking",
        "internet research",
        "addictive behaviors",
        "journal of behavioral addictions",
        "social science computer review",
        "information, communication & society",
    ]
    if any(j in journal for j in top_journals):
        score += 2

    return score


# ── OpenAlex Fetcher ───────────────────────────────────────────────────────


def fetch_openalex_recent(start_date, end_date, per_page: int = 50) -> list[dict]:
    """Fetch recent papers from OpenAlex, sorted by publication date."""
    # Build search query from keywords
    search_terms = " OR ".join(f'"{kw}"' for kw in KEYWORDS[:5])  # Top 5 keywords

    params = {
        "search": search_terms,
        "filter": f"from_publication_date:{start_date.isoformat()},to_publication_date:{end_date.isoformat()},type:article",
        "sort": "publication_date:desc",
        "per_page": per_page,
        "select": "id,doi,title,abstract_inverted_index,publication_date,cited_by_count,primary_location,authorships,open_access,type",
    }
    if EMAIL:
        params["mailto"] = EMAIL

    url = f"https://api.openalex.org/works?{urlencode(params, quote_via=quote_plus)}"
    print(f"  Fetching OpenAlex recent [{start_date} ~ {end_date}]...", file=sys.stderr)

    raw = fetch_url(url, timeout=30)
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("  [WARN] bad JSON from OpenAlex", file=sys.stderr)
        return []

    results = data.get("results", [])
    papers = []

    for r in results:
        doi = normalize_doi(r.get("doi", ""))
        abstract = reconstruct_abstract(r.get("abstract_inverted_index"))

        # Extract authors
        authors = []
        affiliations = set()
        for auth in r.get("authorships", []):
            name = auth.get("author", {}).get("display_name", "")
            if name:
                authors.append(name)
            for inst in auth.get("institutions", []):
                inst_name = inst.get("display_name", "")
                if inst_name:
                    affiliations.add(inst_name)

        # Extract journal info
        journal = ""
        loc = r.get("primary_location") or {}
        source = loc.get("source") or {}
        journal = source.get("display_name", "")

        # OA link
        oa = r.get("open_access") or {}
        oa_url = oa.get("oa_url", "")

        paper = {
            "title": r.get("title", ""),
            "authors": ", ".join(authors),
            "affiliations": ", ".join(sorted(affiliations)),
            "abstract": abstract,
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else r.get("id", ""),
            "pdf": oa_url or "",
            "date": r.get("publication_date", ""),
            "cited_by_count": r.get("cited_by_count", 0),
            "journal": journal,
            "source": "openalex-recent",
            "score": 0,
        }
        paper["score"] = score_paper(paper)
        if paper["score"] >= 0:
            papers.append(paper)

    print(f"  OpenAlex recent: {len(papers)} papers after scoring (from {len(results)} fetched)", file=sys.stderr)
    return papers


def fetch_openalex_high_cited(keywords: list, months: int = 12, per_page: int = 50) -> list[dict]:
    """Fetch high-cited papers from OpenAlex, sorted by citation count."""
    search_terms = " OR ".join(f'"{kw}"' for kw in keywords[:5])
    start = (datetime.now() - timedelta(days=months * 30)).date().isoformat()

    params = {
        "search": search_terms,
        "filter": f"from_publication_date:{start},type:article",
        "sort": "cited_by_count:desc",
        "per_page": per_page,
        "select": "id,doi,title,abstract_inverted_index,publication_date,cited_by_count,primary_location,authorships,open_access,type",
    }
    if EMAIL:
        params["mailto"] = EMAIL

    url = f"https://api.openalex.org/works?{urlencode(params, quote_via=quote_plus)}"
    print(f"  Fetching OpenAlex high-cited (last {months} months)...", file=sys.stderr)

    raw = fetch_url(url, timeout=30)
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("  [WARN] bad JSON from OpenAlex high-cited", file=sys.stderr)
        return []

    results = data.get("results", [])
    papers = []

    for r in results:
        doi = normalize_doi(r.get("doi", ""))
        abstract = reconstruct_abstract(r.get("abstract_inverted_index"))

        authors = []
        affiliations = set()
        for auth in r.get("authorships", []):
            name = auth.get("author", {}).get("display_name", "")
            if name:
                authors.append(name)
            for inst in auth.get("institutions", []):
                inst_name = inst.get("display_name", "")
                if inst_name:
                    affiliations.add(inst_name)

        journal = ""
        loc = r.get("primary_location") or {}
        source = loc.get("source") or {}
        journal = source.get("display_name", "")

        oa = r.get("open_access") or {}
        oa_url = oa.get("oa_url", "")

        paper = {
            "title": r.get("title", ""),
            "authors": ", ".join(authors),
            "affiliations": ", ".join(sorted(affiliations)),
            "abstract": abstract,
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else r.get("id", ""),
            "pdf": oa_url or "",
            "date": r.get("publication_date", ""),
            "cited_by_count": r.get("cited_by_count", 0),
            "journal": journal,
            "source": "openalex-high-cited",
            "score": 0,
        }
        paper["score"] = score_paper(paper)
        if paper["score"] >= 0:
            papers.append(paper)

    print(f"  OpenAlex high-cited: {len(papers)} papers after scoring (from {len(results)} fetched)", file=sys.stderr)
    return papers


# ── Semantic Scholar Fetcher ───────────────────────────────────────────────


def fetch_s2_papers(keywords: list, year_range: str = None, limit: int = 50) -> list[dict]:
    """Fetch papers from Semantic Scholar API."""
    query = " ".join(keywords[:3])  # S2 works best with concise queries

    params = {
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,citationCount,influentialCitationCount,journal,externalIds,openAccessPdf,publicationDate,tldr",
    }
    if year_range:
        params["year"] = year_range

    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{urlencode(params, quote_via=quote_plus)}"
    print(f"  Fetching Semantic Scholar (query='{query}', year={year_range or 'any'})...", file=sys.stderr)

    headers = {}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY

    raw = fetch_url(url, timeout=30, headers=headers)
    if not raw:
        return []

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        print("  [WARN] bad JSON from Semantic Scholar", file=sys.stderr)
        return []

    results = data.get("data", [])
    papers = []

    for r in results:
        # Extract DOI
        ext_ids = r.get("externalIds") or {}
        doi = normalize_doi(ext_ids.get("DOI", ""))

        # Authors
        authors_list = r.get("authors") or []
        authors = ", ".join(a.get("name", "") for a in authors_list if a.get("name"))

        # Journal
        journal_info = r.get("journal") or {}
        journal = journal_info.get("name", "")

        # OA PDF
        oa_pdf = r.get("openAccessPdf") or {}
        pdf_url = oa_pdf.get("url", "")

        # TLDR
        tldr = r.get("tldr") or {}
        tldr_text = tldr.get("text", "")

        paper = {
            "title": r.get("title", ""),
            "authors": authors,
            "affiliations": "",  # S2 free tier doesn't include affiliations
            "abstract": r.get("abstract", "") or tldr_text,
            "doi": doi,
            "url": f"https://doi.org/{doi}" if doi else "",
            "pdf": pdf_url,
            "date": r.get("publicationDate", "") or str(r.get("year", "")),
            "cited_by_count": r.get("citationCount", 0) or 0,
            "influential_citations": r.get("influentialCitationCount", 0) or 0,
            "journal": journal,
            "source": "semantic-scholar",
            "score": 0,
        }
        paper["score"] = score_paper(paper)
        if paper["score"] >= 0:
            papers.append(paper)

    print(f"  Semantic Scholar: {len(papers)} papers after scoring (from {len(results)} fetched)", file=sys.stderr)
    return papers


# ── Merge & Dedup ──────────────────────────────────────────────────────────


def load_history() -> list[dict]:
    """Load recommendation history for dedup."""
    if HISTORY_PATH.exists():
        try:
            return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return []


def merge_and_dedup(
    openalex_recent: list[dict],
    openalex_cited: list[dict],
    s2_papers: list[dict],
    days: int = 1,
    top_n: int = TOP_N,
) -> list[dict]:
    """Merge all sources, dedup by DOI, apply history dedup, return top N."""

    # Merge by DOI, keep higher score
    by_doi: dict[str, dict] = {}
    by_title: dict[str, dict] = {}  # Fallback for papers without DOI

    for p in openalex_recent + openalex_cited + s2_papers:
        doi = p.get("doi", "")
        if doi:
            if doi not in by_doi or p["score"] > by_doi[doi]["score"]:
                by_doi[doi] = p
        else:
            # Dedup by title similarity (lowercase, strip spaces)
            title_key = re.sub(r"\s+", " ", p.get("title", "").lower().strip())
            if title_key and (title_key not in by_title or p["score"] > by_title[title_key]["score"]):
                by_title[title_key] = p

    all_papers = list(by_doi.values()) + list(by_title.values())
    print(f"  Merged: {len(all_papers)} unique papers", file=sys.stderr)

    # History dedup (single-day mode)
    if days <= 1:
        history = load_history()
        history_dois = {h.get("doi", ""): h.get("date", "") for h in history if h.get("doi")}
        history_titles = {h.get("title", "").lower().strip(): h.get("date", "") for h in history if h.get("title")}

        deduped = []
        removed = 0
        for p in all_papers:
            doi = p.get("doi", "")
            title = p.get("title", "").lower().strip()
            if doi and doi in history_dois:
                removed += 1
            elif title and title in history_titles:
                removed += 1
            else:
                deduped.append(p)

        print(f"  After history dedup: {len(deduped)} (removed {removed})", file=sys.stderr)
        all_papers = deduped

    # Filter by min score and sort
    candidates = [p for p in all_papers if p["score"] >= MIN_SCORE]
    candidates.sort(key=lambda x: x["score"], reverse=True)

    top = candidates[:top_n]
    print(f"  Final: {len(top)} papers (target {top_n})", file=sys.stderr)
    return top


# ── Main ───────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Fetch and score social science papers")
    parser.add_argument("--date", help="Target date YYYY-MM-DD (default: today)")
    parser.add_argument("--days", type=int, default=1, help="Number of days to look back for recent papers (default: 1)")
    parser.add_argument("--high-cited-months", type=int, default=12, help="Months to look back for high-cited papers (default: 12)")
    args = parser.parse_args()

    target_date = (
        datetime.strptime(args.date, "%Y-%m-%d").date()
        if args.date
        else datetime.now().date()
    )
    days = max(1, args.days)
    start_date = target_date - timedelta(days=max(30, days * 30))  # OpenAlex min 30 days window
    top_n = TOP_N * days

    print(f"[scholar-scout] {target_date}, days={days}, top_n={top_n}", file=sys.stderr)
    print(f"  Keywords: {KEYWORDS[:5]}...", file=sys.stderr)

    # Source 1: OpenAlex recent papers (new publications)
    oa_recent = fetch_openalex_recent(start_date, target_date)

    # Small delay to be polite
    time.sleep(1)

    # Source 2: OpenAlex high-cited papers (trending/impactful)
    oa_cited = fetch_openalex_high_cited(KEYWORDS, months=args.high_cited_months)

    # Small delay before S2
    time.sleep(1)

    # Source 3: Semantic Scholar (complementary, different ranking)
    current_year = target_date.year
    s2_year = f"{current_year - 1}-{current_year}"
    s2_papers = fetch_s2_papers(KEYWORDS, year_range=s2_year)

    # Merge, dedup, rank
    top = merge_and_dedup(oa_recent, oa_cited, s2_papers, days=days, top_n=top_n)

    # Output (force UTF-8 on Windows to avoid GBK encoding errors)
    import io
    stdout_utf8 = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    json.dump(top, stdout_utf8, ensure_ascii=False, indent=2)
    stdout_utf8.write("\n")
    stdout_utf8.flush()


if __name__ == "__main__":
    main()
