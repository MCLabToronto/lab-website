#!/usr/bin/env python3

"""
Automatically build the MCLab publications database from the
Google Scholar IDs stored in _members/*.

Workflow:

_members/*
    ↓
read links.google-scholar
    ↓
query Google Scholar through SerpAPI
    ↓
combine publications from all lab members
    ↓
deduplicate publications
    ↓
write _data/citations.yaml

Do not edit _data/citations.yaml manually.
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
import unicodedata

from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yaml

from serpapi import GoogleSearch


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]
MEMBERS_DIR = ROOT / "_members"
OUTPUT_FILE = ROOT / "_data" / "citations.yaml"

PAGE_SIZE = 100
MAX_RESULTS_PER_AUTHOR = 1000

PREPRINT_TERMS = (
    "arxiv",
    "biorxiv",
    "medrxiv",
    "psyarxiv",
    "socarxiv",
    "osf preprints",
    "research square",
    "preprint",
)


# ============================================================
# MEMBER FRONT MATTER
# ============================================================

def read_front_matter(path: Path) -> dict:
    """Read YAML front matter from one member file."""

    text = path.read_text(encoding="utf-8-sig")

    if not text.startswith("---"):
        return {}

    parts = text.split("---", 2)

    if len(parts) < 3:
        return {}

    data = yaml.safe_load(parts[1]) or {}

    if not isinstance(data, dict):
        return {}

    return data


def normalize_scholar_id(value) -> str:
    """Return only the Google Scholar author ID."""

    if value is None:
        return ""

    value = str(value).strip()

    if not value:
        return ""

    if "scholar.google" in value:
        try:
            parsed = urlparse(value)
            user_values = parse_qs(parsed.query).get("user", [])
            if user_values:
                return user_values[0].strip()
        except Exception:
            pass

    return value


def find_scholar_profiles() -> dict[str, set[str]]:
    """Scan every member file and collect Google Scholar IDs."""

    profiles: dict[str, set[str]] = {}

    if not MEMBERS_DIR.exists():
        raise RuntimeError(
            f"Members directory does not exist: {MEMBERS_DIR}"
        )

    for path in sorted(MEMBERS_DIR.iterdir()):
        if not path.is_file():
            continue

        if path.name.lower() == "template":
            continue

        try:
            member = read_front_matter(path)
        except Exception as exc:
            print(
                f"WARNING: Could not read {path}: {exc}",
                file=sys.stderr,
            )
            continue

        if not member:
            continue

        links = member.get("links", {}) or {}

        if not isinstance(links, dict):
            continue

        scholar_id = normalize_scholar_id(
            links.get("google-scholar", "")
        )

        if not scholar_id:
            continue

        member_name = str(
            member.get("name", path.stem)
        ).strip()

        profiles.setdefault(scholar_id, set()).add(member_name)

    return profiles


# ============================================================
# GOOGLE SCHOLAR
# ============================================================

def fetch_scholar_articles(
    scholar_id: str,
    api_key: str
) -> list[dict]:
    """Retrieve available Scholar publications for an author."""

    articles: list[dict] = []
    start = 0

    while start < MAX_RESULTS_PER_AUTHOR:
        params = {
            "engine": "google_scholar_author",
            "author_id": scholar_id,
            "api_key": api_key,
            "num": PAGE_SIZE,
            "start": start,
            "sort": "pubdate",
        }

        result = GoogleSearch(params).get_dict()
        error = result.get("error")

        if error:
            raise RuntimeError(
                f"Google Scholar API error for {scholar_id}: {error}"
            )

        page_articles = result.get("articles", []) or []

        if not isinstance(page_articles, list):
            raise RuntimeError(
                f"Unexpected Scholar response for {scholar_id}"
            )

        articles.extend(page_articles)

        print(
            f"    retrieved {len(page_articles)} "
            f"publication(s) at offset {start}"
        )

        if len(page_articles) < PAGE_SIZE:
            break

        start += PAGE_SIZE

    return articles


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_title(title: str) -> str:
    """Create a stable title key for deduplication."""

    text = unicodedata.normalize("NFKD", str(title))
    text = "".join(
        char
        for char in text
        if not unicodedata.combining(char)
    )
    text = text.casefold()
    text = re.sub(r"[^a-z0-9]+", "", text)

    return text


def split_authors(authors) -> list[str]:
    """Convert Scholar's author field into a YAML list."""

    if not authors:
        return []

    if isinstance(authors, list):
        return [
            str(author).strip()
            for author in authors
            if str(author).strip()
        ]

    return [
        author.strip()
        for author in str(authors).split(",")
        if author.strip()
    ]


def clean_year(value) -> str:
    """Return a four-digit year or an empty string."""

    if value is None:
        return ""

    match = re.search(
        r"\b(19|20)\d{2}\b",
        str(value).strip(),
    )

    if not match:
        return ""

    return match.group(0)


# ============================================================
# PUBLICATION RECORDS
# ============================================================

def publication_id(normalized_title: str) -> str:
    """Generate a stable internal publication ID from title."""

    digest = hashlib.sha1(
        normalized_title.encode("utf-8")
    ).hexdigest()[:16]

    return f"scholar:{digest}"


def article_to_record(
    article: dict,
    scholar_id: str,
    members: set[str]
) -> dict | None:
    """Convert one Scholar article to website publication data."""

    title = str(article.get("title", "")).strip()

    if not title:
        return None

    normalized = normalize_title(title)

    if not normalized:
        return None

    year = clean_year(article.get("year", ""))
    publisher = str(article.get("publication", "") or "").strip()
    link = str(article.get("link", "") or "").strip()

    return {
        "id": publication_id(normalized),
        "title": title,
        "authors": split_authors(article.get("authors", "")),
        "publisher": publisher,
        "date": f"{year}-01-01" if year else "",
        "year": year,
        "link": link,
        "type": "paper",
        "lab_members": sorted(members),
        "scholar_ids": [scholar_id],
    }


def is_preprint(publisher: str) -> bool:
    text = publisher.casefold()
    return any(term in text for term in PREPRINT_TERMS)


def record_score(record: dict) -> tuple:
    """Choose the preferred version when duplicate titles occur."""

    publisher = str(record.get("publisher", ""))
    year = clean_year(record.get("year", ""))

    score = 0

    if publisher:
        score += 4

    if record.get("link"):
        score += 2

    if year:
        score += 1

    if is_preprint(publisher):
        score -= 3

    numeric_year = int(year) if year else 0

    return (
        score,
        numeric_year,
        len(publisher),
    )


def merge_duplicate(existing: dict, candidate: dict) -> dict:
    """Merge duplicate records from multiple Scholar profiles."""

    lab_members = set(existing.get("lab_members", []))
    lab_members.update(candidate.get("lab_members", []))

    scholar_ids = set(existing.get("scholar_ids", []))
    scholar_ids.update(candidate.get("scholar_ids", []))

    if record_score(candidate) > record_score(existing):
        chosen = dict(candidate)
    else:
        chosen = dict(existing)

    chosen["lab_members"] = sorted(lab_members)
    chosen["scholar_ids"] = sorted(scholar_ids)

    return chosen


# ============================================================
# OUTPUT
# ============================================================

def publication_sort_key(record: dict):
    year = clean_year(record.get("year", ""))
    numeric_year = int(year) if year else 0

    return (
        numeric_year,
        str(record.get("title", "")).casefold(),
    )


def write_publications(publications: list[dict]):
    """Replace _data/citations.yaml."""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    yaml_text = yaml.safe_dump(
        publications,
        sort_keys=False,
        allow_unicode=True,
        width=1000,
    )

    content = (
        "# DO NOT EDIT, GENERATED AUTOMATICALLY\n"
        "# Source: Google Scholar profiles listed in _members/\n\n"
        + yaml_text
    )

    OUTPUT_FILE.write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

def main():
    api_key = os.environ.get(
        "GOOGLE_SCHOLAR_API_KEY",
        ""
    ).strip()

    if not api_key:
        raise RuntimeError(
            'Missing GOOGLE_SCHOLAR_API_KEY environment variable.'
        )

    print("Scanning member profiles...")

    profiles = find_scholar_profiles()

    if not profiles:
        raise RuntimeError(
            "No Google Scholar IDs were found in _members/."
        )

    print(
        f"Found {len(profiles)} unique "
        f"Google Scholar profile(s)."
    )

    publications_by_title: dict[str, dict] = {}
    errors = []

    for scholar_id, members in sorted(profiles.items()):
        member_names = ", ".join(sorted(members))

        print()
        print(f"Google Scholar: {member_names}")
        print(f"  ID: {scholar_id}")

        try:
            articles = fetch_scholar_articles(
                scholar_id,
                api_key
            )
        except Exception as exc:
            errors.append(str(exc))
            print(
                f"ERROR: {exc}",
                file=sys.stderr
            )
            continue

        print(f"  Total: {len(articles)} publication(s)")

        if not articles:
            print(
                "  WARNING: This Scholar profile returned "
                "no publications."
            )

        for article in articles:
            record = article_to_record(
                article,
                scholar_id,
                members
            )

            if not record:
                continue

            key = normalize_title(record["title"])

            if key in publications_by_title:
                publications_by_title[key] = merge_duplicate(
                    publications_by_title[key],
                    record
                )
            else:
                publications_by_title[key] = record

    # Protect the current database from transient API failures.
    if errors:
        print()
        print(
            "Publication update aborted because one or more "
            "Google Scholar requests failed.",
            file=sys.stderr
        )

        for error in errors:
            print(
                f"  - {error}",
                file=sys.stderr
            )

        sys.exit(1)

    publications = list(publications_by_title.values())

    publications.sort(
        key=publication_sort_key,
        reverse=True
    )

    print()
    print(
        f"{len(publications)} unique publication(s) "
        f"after deduplication."
    )

    write_publications(publications)

    print(f"Wrote {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
