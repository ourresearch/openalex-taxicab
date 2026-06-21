#!/usr/bin/env python3
"""No-storage local http_get route validation for Taxicab PDF branches.

This runner validates the actual Taxicab `http_get` branch behavior for a
filtered set of PDF rows. It does not call POST /taxicab and does not write to
R2/DynamoDB. Row-level artifacts are local evidence; summary/report artifacts
are aggregate-only and safe to summarize into oxjobs after review.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.http_cache import http_get  # noqa: E402
from openalex_taxicab.pdf_eval_harness import (  # noqa: E402
    PDF_CATEGORY_GOOD_PDF,
    PDF_CATEGORY_NO_PDF_EXPECTED,
    PDF_CATEGORY_TAXICAB_ERROR,
    PDF_CATEGORY_TIMEOUT,
    PdfEvidence,
    classify_pdf_content,
    host_from_url,
    make_pdf_transport_row,
)
from scripts.provider_pdf_probe import (  # noqa: E402
    BEST_CATEGORY_RANK,
    DEFAULT_ROWS as PROVIDER_DEFAULT_ROWS,
    ProbeRecord,
    filter_records,
    git_sha,
    load_env_file,
    read_input_records,
)

DEFAULT_ROWS = REPO_ROOT / "pdf_eval_runs" / "pdf-full10k-after-freshtail-f4f4a28" / "rows.ndjson"
if not DEFAULT_ROWS.exists():
    DEFAULT_ROWS = PROVIDER_DEFAULT_ROWS


@dataclass(frozen=True)
class RouteProbeConfig:
    run_id: str
    read_timeout: int
    connect_timeout: int


def header_value(headers: dict[str, Any] | None, name: str) -> str:
    if not isinstance(headers, dict):
        return ""
    target = name.lower()
    for key, value in headers.items():
        if str(key).lower() == target:
            return str(value or "")
    return ""


def is_timeout_exception(exc: BaseException) -> bool:
    name = type(exc).__name__.lower()
    text = str(exc).lower()
    return "timeout" in name or "timeout" in text or "timed out" in text or "retryerror" in name


def classify_route_exception(record: ProbeRecord, exc: BaseException, *, run_id: str, duration_ms: int) -> dict[str, Any]:
    category = PDF_CATEGORY_TIMEOUT if is_timeout_exception(exc) else PDF_CATEGORY_TAXICAB_ERROR
    row = make_pdf_transport_row(
        run_id=run_id,
        doi=record.doi,
        work_id=record.work_id,
        publisher=record.publisher,
        host=record.host or host_from_url(record.candidate_url),
        input_url=record.input_url,
        candidate_url=record.candidate_url,
        candidate_source="http_get_route_probe",
        resolved_url=record.candidate_url,
        category=category,
        duration_ms=duration_ms,
        mode="http_get_route_probe",
        error=f"{type(exc).__name__}: {exc}",
    ).to_dict()
    row["baseline_category"] = record.baseline_category
    return row


def classify_route_response(record: ProbeRecord, response: Any, *, run_id: str, duration_ms: int) -> dict[str, Any]:
    content_type = header_value(getattr(response, "headers", None), "Content-Type")
    row = classify_pdf_content(
        PdfEvidence(
            doi=record.doi,
            work_id=record.work_id,
            title=record.title,
            publisher=record.publisher,
            host=record.host or host_from_url(record.candidate_url),
            input_url=record.input_url,
            candidate_url=record.candidate_url,
            candidate_source="http_get_route_probe",
            resolved_url=getattr(response, "url", "") or record.candidate_url,
            status_code=getattr(response, "status_code", None),
            content_type=content_type,
            body=getattr(response, "content", b""),
            pdf_expected=True,
            duration_ms=duration_ms,
            mode="http_get_route_probe",
        ),
        run_id=run_id,
    ).to_dict()
    row["baseline_category"] = record.baseline_category
    return row


def best_route_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return min(
        rows,
        key=lambda row: (
            BEST_CATEGORY_RANK.get(str(row.get("category") or ""), 999),
            -(int(row.get("size_bytes") or 0)),
        ),
    )


def write_route_artifacts(rows: list[dict[str, Any]], out_dir: Path, *, run_id: str, source_path: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "rows.ndjson"
    with rows_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_doi[row["doi"]].append(row)
    best_by_doi = {doi: best_route_row(doi_rows) for doi, doi_rows in by_doi.items()}

    baseline_counts = Counter(str(row.get("baseline_category") or "unknown") for row in best_by_doi.values())
    category_counts = Counter(str(row.get("category") or "unknown") for row in best_by_doi.values())
    transitions = Counter(
        f"{row.get('baseline_category') or 'unknown'}->{row.get('category') or 'unknown'}"
        for row in best_by_doi.values()
    )
    prior_non_good_recovered = sum(
        1
        for row in best_by_doi.values()
        if row.get("category") == PDF_CATEGORY_GOOD_PDF
        and row.get("baseline_category") not in {PDF_CATEGORY_GOOD_PDF, PDF_CATEGORY_NO_PDF_EXPECTED}
    )
    already_good_preserved = sum(
        1
        for row in best_by_doi.values()
        if row.get("baseline_category") == PDF_CATEGORY_GOOD_PDF and row.get("category") == PDF_CATEGORY_GOOD_PDF
    )
    already_good_regressed = sum(
        1
        for row in best_by_doi.values()
        if row.get("baseline_category") == PDF_CATEGORY_GOOD_PDF and row.get("category") != PDF_CATEGORY_GOOD_PDF
    )

    summary = {
        "run_id": run_id,
        "artifact_kind": "http_get_route_probe_aggregate",
        "aggregate_only": True,
        "contains_doi_lists": False,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "source_path": str(source_path),
        "doi_count": len(best_by_doi),
        "row_count": len(rows),
        "baseline_category_counts": dict(sorted(baseline_counts.items())),
        "category_counts": dict(sorted(category_counts.items())),
        "category_transitions": dict(sorted(transitions.items())),
        "prior_non_good_recovered": prior_non_good_recovered,
        "already_good_preserved": already_good_preserved,
        "already_good_regressed": already_good_regressed,
        "local_row_artifact": "rows.ndjson",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    category_rows = "\n".join(
        f"<tr><td><code>{html.escape(category)}</code></td><td>{count}</td></tr>"
        for category, count in sorted(category_counts.items())
    )
    transition_rows = "\n".join(
        f"<tr><td><code>{html.escape(transition)}</code></td><td>{count}</td></tr>"
        for transition, count in sorted(transitions.items())
    )
    report = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(run_id)}</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:24px;color:#111827}}table{{border-collapse:collapse;width:100%;font-size:13px;margin:12px 0}}td,th{{border-bottom:1px solid #e5e7eb;padding:6px;text-align:left;vertical-align:top}}th{{background:#f1f5f9}}.pos{{color:#15803d;font-weight:700}}.neg{{color:#b91c1c;font-weight:700}}</style>
</head><body>
<h1>{html.escape(run_id)}</h1>
<p>No-storage local <code>http_get</code> route validation. This aggregate report omits DOI and URL lists; row-level evidence is local only.</p>
<p><b class="pos">Prior non-good recovered: {prior_non_good_recovered}</b> / {len(best_by_doi)} rows. Already-good preserved: {already_good_preserved}. Already-good regressed: <b class="neg">{already_good_regressed}</b>.</p>
<h2>Best Category Counts</h2>
<table><thead><tr><th>Category</th><th>Count</th></tr></thead><tbody>{category_rows}</tbody></table>
<h2>Transitions</h2>
<table><thead><tr><th>Transition</th><th>Count</th></tr></thead><tbody>{transition_rows}</tbody></table>
</body></html>
"""
    (out_dir / "report.html").write_text(report, encoding="utf-8")


def run_probe(args: argparse.Namespace) -> int:
    load_env_file(Path(args.env_file) if args.env_file else REPO_ROOT / ".env")
    records = filter_records(
        read_input_records(Path(args.input)),
        category=args.category,
        publisher=args.publisher,
        host=args.host,
        limit=args.limit,
    )
    run_id = args.run_id or f"http-get-route-probe-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        print(f"{index}/{len(records)} {record.doi} {record.publisher} {record.host}", flush=True)
        target_url = record.fetch_url or record.candidate_url
        started = time.monotonic()
        try:
            response = http_get(
                target_url,
                doi=record.doi,
                read_timeout=args.read_timeout,
                connect_timeout=args.connect_timeout,
            )
            duration_ms = int((time.monotonic() - started) * 1000)
            row = classify_route_response(record, response, run_id=run_id, duration_ms=duration_ms)
        except Exception as exc:  # noqa: BLE001 - route validation should classify failures.
            duration_ms = int((time.monotonic() - started) * 1000)
            row = classify_route_exception(record, exc, run_id=run_id, duration_ms=duration_ms)
        rows.append(row)
        time.sleep(args.sleep)

    out_dir = Path(args.out) / run_id
    write_route_artifacts(rows, out_dir, run_id=run_id, source_path=Path(args.input))
    print(out_dir)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_ROWS), help="PDF rows.ndjson or CSV work queue")
    parser.add_argument("--category", default="missing_pdf_harvest", help="Baseline category filter; empty disables")
    parser.add_argument("--publisher", default="", help="Exact publisher filter")
    parser.add_argument("--host", default="", help="Host substring filter")
    parser.add_argument("--limit", type=int, default=3, help="Maximum DOI records to probe")
    parser.add_argument("--out", default="pdf_eval_runs/")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--read-timeout", type=int, default=60)
    parser.add_argument("--connect-timeout", type=int, default=5)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--env-file", default="")
    args = parser.parse_args(argv)
    return run_probe(args)


if __name__ == "__main__":
    raise SystemExit(main())
