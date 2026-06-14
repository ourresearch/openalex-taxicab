#!/usr/bin/env python3
"""No-storage ScienceDirect PDF route probes for Taxicab PDF Phase 2.

This script intentionally does not call Taxicab POST /taxicab and does not
write to R2/DynamoDB. It calls Zyte directly for route variants, classifies the
returned bytes with the PDF harness, and writes sanitized probe artifacts.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit, urlunsplit

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.pdf_eval_harness import PdfEvidence, classify_pdf_content  # noqa: E402

DEFAULT_SPLIT = Path(
    "/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-route-split-100-9b7d84b.json"
)


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return ""


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def sanitize_url(url: str) -> str:
    if not url:
        return ""
    parts = urlsplit(url)
    return urlunsplit((parts.scheme or "https", parts.netloc, parts.path or "/", "", ""))


def host_from_url(url: str) -> str:
    host = urlsplit(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def reconstruct_url(record: dict[str, Any]) -> str:
    candidate_host = str(record.get("candidate_host") or "").strip()
    candidate_path = str(record.get("candidate_path") or "/").strip() or "/"
    if not candidate_host:
        return ""
    return f"https://{candidate_host}{candidate_path}"


def extract_sciencedirect_pii(url: str) -> str:
    parts = urlsplit(url)
    query_pii = parse_qs(parts.query).get("pii", [""])[0]
    if query_pii and re.fullmatch(r"[A-Za-z0-9]+", query_pii):
        return query_pii.upper()

    patterns = (
        r"/science/article/(?:abs/|am/)?pii/([A-Za-z0-9]+)",
        r"/sdfe/pdf/download/eid/(?:[0-9]+-s2\.0-)?([A-Za-z0-9]+)/",
        r"/[0-9]+-s2\.0-([A-Za-z0-9]+)/[^/]+\.pdf$",
    )
    for pattern in patterns:
        match = re.search(pattern, parts.path, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    return ""


def build_sciencedirect_pdf_variants(url: str) -> list[dict[str, str]]:
    """Return safe ScienceDirect route variants for a candidate URL."""
    sanitized = sanitize_url(url)
    pii = extract_sciencedirect_pii(url) or extract_sciencedirect_pii(sanitized)
    variants: list[dict[str, str]] = []
    seen: set[str] = set()

    def add(name: str, value: str) -> None:
        safe = sanitize_url(value)
        if safe and safe not in seen:
            seen.add(safe)
            variants.append({"name": name, "url": safe})

    if sanitized:
        add("candidate", sanitized)
    if pii:
        article = f"https://www.sciencedirect.com/science/article/pii/{pii}"
        add("article", article)
        add("pdfft", f"{article}/pdfft")
        add("pdf", f"{article}/pdf")
    return variants


def zyte_fetch(url: str, *, timeout: int) -> tuple[int | None, str, bytes, str]:
    api_key = os.getenv("ZYTE_API_KEY")
    if not api_key:
        return None, "", b"", "ZYTE_API_KEY not configured"
    params = {
        "url": url,
        "httpResponseBody": True,
        "httpResponseHeaders": True,
    }
    try:
        response = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(api_key, ""),
            json=params,
            timeout=timeout,
            verify=False,
        )
        data = response.json()
    except Exception as exc:  # noqa: BLE001 - probe artifact should capture failures.
        return None, "", b"", f"zyte request failed: {type(exc).__name__}: {exc}"

    if data.get("status"):
        return data.get("status"), "", b"", str(data.get("detail") or data.get("title") or "zyte error")

    headers = {h.get("name", ""): h.get("value", "") for h in data.get("httpResponseHeaders", [])}
    content_type = headers.get("Content-Type") or headers.get("content-type") or ""
    body = base64.b64decode(data.get("httpResponseBody") or b"")
    return data.get("statusCode"), content_type, body, ""


def read_split_records(path: Path, *, cluster: str, limit: int | None) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text())
    records = [r for r in payload.get("records", []) if r.get("route_cluster") == cluster]
    if limit is not None:
        records = records[:limit]
    return records


def write_probe_artifacts(rows: list[dict[str, Any]], out_dir: Path, *, run_id: str, split_path: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "rows.ndjson"
    with rows_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")

    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_doi[row["doi"]].append(row)

    per_variant = Counter(row["variant_name"] + ":" + row["category"] for row in rows)
    best_by_doi = {}
    for doi, doi_rows in by_doi.items():
        good = [r for r in doi_rows if r["category"] == "good_pdf"]
        best_by_doi[doi] = good[0] if good else doi_rows[0]

    recovered = sorted(doi for doi, row in best_by_doi.items() if row["category"] == "good_pdf")
    summary = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "source_split": str(split_path),
        "doi_count": len(by_doi),
        "variant_rows": len(rows),
        "recovered_doi_count": len(recovered),
        "recovered_dois": recovered,
        "per_variant_category_counts": dict(sorted(per_variant.items())),
        "best_category_counts": dict(Counter(row["category"] for row in best_by_doi.values())),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    report_rows = "\n".join(
        "<tr>"
        f"<td><code>{html.escape(row['doi'])}</code></td>"
        f"<td>{html.escape(row['variant_name'])}</td>"
        f"<td><code>{html.escape(row['category'])}</code></td>"
        f"<td>{row['status_code'] if row['status_code'] is not None else ''}</td>"
        f"<td>{html.escape(row['content_type'])}</td>"
        f"<td>{row['size_bytes']}</td>"
        f"<td><code>{html.escape(row['variant_url'])}</code></td>"
        "</tr>"
        for row in rows
    )
    report = f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><title>{html.escape(run_id)}</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;margin:24px;color:#111827}}table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{border-bottom:1px solid #e5e7eb;padding:6px;text-align:left;vertical-align:top}}th{{background:#f1f5f9}}.pos{{color:#15803d;font-weight:700}}</style>
</head><body>
<h1>{html.escape(run_id)}</h1>
<p>ScienceDirect no-storage PDF route probe. Query strings and signed diagnostics are omitted from artifacts.</p>
<p><b class=\"pos\">Recovered DOI count: {len(recovered)}/{len(by_doi)}</b></p>
<table><thead><tr><th>DOI</th><th>Variant</th><th>Category</th><th>Status</th><th>Content-Type</th><th>Bytes</th><th>URL</th></tr></thead><tbody>
{report_rows}
</tbody></table>
</body></html>
"""
    (out_dir / "report.html").write_text(report)


def run_probe(args: argparse.Namespace) -> int:
    if args.env_file:
        load_env_file(Path(args.env_file))
    else:
        load_env_file(REPO_ROOT / ".env")

    records = read_split_records(Path(args.split), cluster=args.cluster, limit=args.limit)
    rows: list[dict[str, Any]] = []
    run_id = args.run_id or f"sciencedirect-probe-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    for index, record in enumerate(records, start=1):
        doi = str(record.get("doi") or "")
        candidate = reconstruct_url(record)
        variants = build_sciencedirect_pdf_variants(candidate)
        print(f"{index}/{len(records)} {doi} variants={len(variants)}", flush=True)
        for variant in variants:
            status_code, content_type, body, error = zyte_fetch(variant["url"], timeout=args.timeout)
            row = classify_pdf_content(
                PdfEvidence(
                    doi=doi,
                    work_id=str(record.get("work_id") or ""),
                    publisher="elsevier",
                    input_url=f"https://doi.org/{doi}",
                    candidate_url=variant["url"],
                    candidate_source=f"sciencedirect_probe:{variant['name']}",
                    resolved_url=variant["url"],
                    status_code=status_code,
                    content_type=content_type,
                    body=body,
                    pdf_expected=True,
                    mode="probe",
                    error=error,
                ),
                run_id=run_id,
            ).to_dict()
            row["variant_name"] = variant["name"]
            row["variant_url"] = variant["url"]
            rows.append(row)
            time.sleep(args.sleep)

    write_probe_artifacts(rows, Path(args.out) / run_id, run_id=run_id, split_path=Path(args.split))
    print(Path(args.out) / run_id)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", default=str(DEFAULT_SPLIT))
    parser.add_argument("--cluster", default="sciencedirect_article_or_pdf_route")
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--out", default="pdf_eval_runs/")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--env-file", default="")
    args = parser.parse_args()
    return run_probe(args)


if __name__ == "__main__":
    raise SystemExit(main())
