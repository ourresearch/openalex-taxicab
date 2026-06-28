#!/usr/bin/env python3
"""No-storage provider PDF strategy probes for Taxicab PDF Phase 2.

This script intentionally does not call Taxicab POST /taxicab and does not
write to R2/DynamoDB. It calls Zyte directly for selected candidate URLs,
classifies returned bytes with the PDF harness, and writes sanitized evidence
artifacts that can be copied into oxjobs #461.
"""

from __future__ import annotations

import argparse
import base64
import csv
import html
import json
import os
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.pdf_eval_harness import PdfEvidence, classify_pdf_content, has_pdf_magic, host_from_url  # noqa: E402
from openalex_taxicab.publisher_index import classify_row as classify_publisher  # noqa: E402

DEFAULT_ROWS = REPO_ROOT / "pdf_eval_runs" / "pdf-full10k-after-humankinetics-bbd2225" / "rows.ndjson"
DEFAULT_STRATEGIES = ("default_body", "accept_pdf", "google_referer", "browser_html")
BEST_CATEGORY_RANK = {
    "good_pdf": 0,
    "wrong_content_pdf": 10,
    "supplement_or_preview_pdf": 20,
    "corrupt_or_truncated_pdf": 30,
    "encrypted_or_unreadable_pdf": 40,
    "html_instead_of_pdf": 50,
    "js_redirect_unresolved": 60,
    "interstitial_or_paywall": 70,
    "bot_block_403": 80,
    "empty_response": 90,
    "timeout": 100,
    "provider_error": 110,
    "taxicab_error": 120,
    "missing_pdf_harvest": 130,
    "no_pdf_expected": 140,
}
RecipeMap = dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ProbeRecord:
    doi: str
    work_id: str = ""
    title: str = ""
    publisher: str = "unknown"
    host: str = ""
    input_url: str = ""
    fetch_url: str = ""
    candidate_url: str = ""
    candidate_source: str = ""
    baseline_category: str = ""


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
    if not parts.netloc:
        return ""
    return urlunsplit((parts.scheme or "https", parts.netloc, parts.path or "/", "", ""))


def normalize_fetch_url(url: str) -> str:
    """Return a Zyte-acceptable URL while preserving query parameters."""
    if not url:
        return ""
    stripped = url.strip()
    if stripped.startswith("//"):
        stripped = f"https:{stripped}"
    parts = urlsplit(stripped)
    if parts.scheme and parts.netloc:
        return stripped
    return ""


def _first_value(row: dict[str, Any], keys: tuple[str, ...]) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return ""


def record_from_row(row: dict[str, Any]) -> ProbeRecord:
    doi = _first_value(row, ("doi", "DOI"))
    candidate_url = _first_value(
        row,
        (
            "candidate_url",
            "resolved_url",
            "PDF URL",
            "pdf_url",
            "pdf",
            "fulltext_pdf_url",
            "Link",
            "link",
            "input_url",
        ),
    )
    input_url = _first_value(row, ("input_url", "Link", "link")) or (f"https://doi.org/{doi}" if doi else "")
    host = _first_value(row, ("host", "candidate_host"))
    sanitized_candidate = sanitize_url(candidate_url)
    if not host:
        host = host_from_url(sanitized_candidate)
    publisher = _first_value(row, ("publisher", "Publisher")) or classify_publisher(
        row,
        allow_network=False,
        resolved_url=sanitized_candidate,
    )
    return ProbeRecord(
        doi=doi,
        work_id=_first_value(row, ("work_id", "Work ID", "openalex_id")),
        title=_first_value(row, ("title", "Title", "display_name")),
        publisher=publisher,
        host=host,
        input_url=sanitize_url(input_url) or input_url,
        fetch_url=normalize_fetch_url(candidate_url),
        candidate_url=sanitized_candidate,
        candidate_source=_first_value(row, ("candidate_source", "baseline_candidate_source")) or "provider_probe_input",
        baseline_category=_first_value(row, ("category", "baseline_category")),
    )


def read_input_records(path: Path) -> list[ProbeRecord]:
    records: list[ProbeRecord] = []
    if path.suffix.lower() == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                record = record_from_row(row)
                if record.doi:
                    records.append(record)
        return records
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            record = record_from_row(json.loads(line))
            if record.doi:
                records.append(record)
    return records


def filter_records(
    records: list[ProbeRecord],
    *,
    category: str,
    publisher: str,
    host: str,
    limit: int | None,
) -> list[ProbeRecord]:
    if limit is not None and limit <= 0:
        return []
    filtered = []
    publisher_lc = publisher.lower()
    host_lc = host_from_url(f"https://{host}") if host and "://" not in host else host_from_url(host)
    for record in records:
        if category and record.baseline_category != category:
            continue
        if publisher_lc and record.publisher.lower() != publisher_lc:
            continue
        if host_lc and host_lc not in (record.host or host_from_url(record.candidate_url)).lower():
            continue
        if not record.candidate_url:
            continue
        filtered.append(record)
        if limit is not None and len(filtered) >= limit:
            break
    return filtered


def progress_record_label(record: ProbeRecord, *, show_doi: bool = False) -> str:
    """Return a progress label that is safe for shared logs by default."""
    publisher = record.publisher or "unknown"
    host = record.host or host_from_url(record.candidate_url) or "unknown"
    baseline = record.baseline_category or "unknown"
    if show_doi:
        return f"{record.doi} {publisher} {host}"
    return f"publisher={publisher} host={host} baseline={baseline}"


def _replace_url_placeholders(value: Any, url: str) -> Any:
    if isinstance(value, str):
        return value.replace("{{url}}", url).replace("{url}", url)
    if isinstance(value, list):
        return [_replace_url_placeholders(item, url) for item in value]
    if isinstance(value, dict):
        return {
            str(key): _replace_url_placeholders(item, url)
            for key, item in value.items()
        }
    return value


def load_recipe_strategies(path: Path | str | None) -> RecipeMap:
    if not path:
        return {}
    recipe_path = Path(path)
    data = json.loads(recipe_path.read_text(encoding="utf-8"))
    raw_strategies = data.get("strategies") if isinstance(data, dict) else data
    if not isinstance(raw_strategies, list):
        raise ValueError("recipe file must contain a list or an object with a strategies list")
    recipes: RecipeMap = {}
    for item in raw_strategies:
        if not isinstance(item, dict):
            raise ValueError("each recipe strategy must be an object")
        name = str(item.get("name") or "").strip()
        params = item.get("params")
        if not name:
            raise ValueError("recipe strategy missing name")
        if name in DEFAULT_STRATEGIES:
            raise ValueError(f"recipe strategy shadows built-in strategy: {name}")
        if name in recipes:
            raise ValueError(f"duplicate recipe strategy: {name}")
        if not isinstance(params, dict):
            raise ValueError(f"recipe strategy {name} missing params object")
        recipes[name] = params
    return recipes


def strategy_params(strategy: str, url: str, recipes: RecipeMap | None = None) -> dict[str, Any]:
    recipes = recipes or {}
    if strategy in recipes:
        params = _replace_url_placeholders(recipes[strategy], url)
        if "url" not in params:
            params = {"url": url, **params}
        return params
    base = {
        "url": url,
        "httpResponseBody": True,
        "httpResponseHeaders": True,
    }
    if strategy == "default_body":
        return base
    if strategy == "accept_pdf":
        return base | {
            "customHttpRequestHeaders": [
                {"name": "Accept", "value": "application/pdf,*/*"},
            ]
        }
    if strategy == "google_referer":
        return base | {
            "customHttpRequestHeaders": [
                {"name": "Accept", "value": "application/pdf,*/*"},
                {"name": "Referer", "value": "https://www.google.com/"},
            ]
        }
    if strategy == "browser_html":
        return {
            "url": url,
            "browserHtml": True,
            "javascript": True,
        }
    raise ValueError(f"unknown strategy: {strategy}")


def _header_value(headers: Any, name: str) -> str:
    expected = name.lower()
    if isinstance(headers, dict):
        for header_name, value in headers.items():
            if str(header_name).lower() == expected:
                return str(value or "")
        return ""
    if isinstance(headers, list):
        for header in headers:
            if isinstance(header, dict):
                header_name = str(header.get("name") or "").lower()
                if header_name == expected:
                    return str(header.get("value") or "")
            elif isinstance(header, (list, tuple)) and len(header) >= 2:
                header_name = str(header[0] or "").lower()
                if header_name == expected:
                    return str(header[1] or "")
    return ""


def response_content_type(data: dict[str, Any]) -> str:
    return _header_value(data.get("httpResponseHeaders") or [], "content-type")


def _response_body_bytes(value: Any) -> bytes:
    if not value:
        return b""
    try:
        return base64.b64decode(value)
    except Exception:
        return b""


def _as_int(value: Any) -> int | None:
    try:
        if value is None or value == "":
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _captured_url(capture: dict[str, Any]) -> str:
    return sanitize_url(
        str(
            capture.get("url")
            or capture.get("responseUrl")
            or capture.get("requestUrl")
            or capture.get("targetUrl")
            or ""
        )
    )


def _network_capture_content_type(capture: dict[str, Any]) -> str:
    return _header_value(
        capture.get("httpResponseHeaders")
        or capture.get("responseHeaders")
        or capture.get("headers")
        or [],
        "content-type",
    )


def best_network_capture(data: dict[str, Any]) -> tuple[str, bytes, str, int | None]:
    captures = data.get("networkCapture") or []
    if not isinstance(captures, list):
        return "", b"", "", None

    candidates: list[tuple[int, int, str, bytes, str, int | None]] = []
    for capture in captures:
        if not isinstance(capture, dict):
            continue
        body = _response_body_bytes(capture.get("httpResponseBody"))
        if not body:
            continue
        content_type = _network_capture_content_type(capture)
        url = _captured_url(capture)
        content_type_lc = content_type.lower()
        url_lc = url.lower()
        if has_pdf_magic(body):
            score = 0
        elif "application/pdf" in content_type_lc:
            score = 1
        elif ".pdf" in url_lc:
            score = 2
        else:
            score = 3
        status_code = _as_int(capture.get("statusCode") or capture.get("status"))
        candidates.append((score, -len(body), content_type, body, url, status_code))

    if not candidates:
        return "", b"", "", None
    _, _, content_type, body, url, status_code = min(candidates, key=lambda item: (item[0], item[1]))
    return content_type, body, url, status_code


def decode_zyte_payload(data: dict[str, Any]) -> tuple[int | None, str, bytes, str]:
    captured_content_type, captured_body, captured_url, captured_status = best_network_capture(data)
    if captured_body:
        return (
            captured_status or _as_int(data.get("statusCode")),
            captured_content_type,
            captured_body,
            captured_url or sanitize_url(str(data.get("url") or "")),
        )
    if data.get("httpResponseBody"):
        return (
            _as_int(data.get("statusCode")),
            response_content_type(data),
            _response_body_bytes(data.get("httpResponseBody")),
            sanitize_url(str(data.get("url") or "")),
        )
    if data.get("browserHtml"):
        return (
            _as_int(data.get("statusCode")),
            "text/html",
            str(data.get("browserHtml") or "").encode("utf-8", errors="replace"),
            sanitize_url(str(data.get("url") or "")),
        )
    return (
        _as_int(data.get("statusCode")),
        response_content_type(data),
        b"",
        sanitize_url(str(data.get("url") or "")),
    )


def decode_zyte_body(data: dict[str, Any]) -> tuple[str, bytes]:
    _, content_type, body, _ = decode_zyte_payload(data)
    return content_type, body


def zyte_fetch(params: dict[str, Any], *, timeout: int) -> tuple[int | None, str, bytes, str, str]:
    api_key = os.getenv("ZYTE_API_KEY")
    if not api_key:
        return None, "", b"", params.get("url", ""), "ZYTE_API_KEY not configured"
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
        return None, "", b"", params.get("url", ""), f"zyte request failed: {type(exc).__name__}: {exc}"

    if data.get("status"):
        return (
            data.get("statusCode") or data.get("status"),
            "",
            b"",
            sanitize_url(str(data.get("url") or params.get("url") or "")),
            str(data.get("detail") or data.get("title") or "zyte error"),
        )

    status_code, content_type, body, resolved_url = decode_zyte_payload(data)
    return (
        status_code,
        content_type,
        body,
        resolved_url or sanitize_url(str(params.get("url") or "")),
        "",
    )


def strategy_list(raw: str, recipes: RecipeMap | None = None) -> list[str]:
    recipes = recipes or {}
    if not raw or raw == "all":
        return list(DEFAULT_STRATEGIES) + list(recipes)
    strategies = [item.strip() for item in raw.split(",") if item.strip()]
    for strategy in strategies:
        strategy_params(strategy, "https://example.org/test.pdf", recipes)
    return strategies


def best_probe_row(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return min(
        rows,
        key=lambda row: (
            BEST_CATEGORY_RANK.get(str(row.get("category") or ""), 999),
            -(int(row.get("size_bytes") or 0)),
            str(row.get("strategy_name") or ""),
        ),
    )


def write_probe_artifacts(rows: list[dict[str, Any]], out_dir: Path, *, run_id: str, source_path: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows_path = out_dir / "rows.ndjson"
    with rows_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_doi[row["doi"]].append(row)

    best_by_doi = {}
    for doi, doi_rows in by_doi.items():
        best_by_doi[doi] = best_probe_row(doi_rows)

    recovered = sorted(doi for doi, row in best_by_doi.items() if row["category"] == "good_pdf")
    per_strategy = Counter(f"{row['strategy_name']}:{row['category']}" for row in rows)
    summary = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": git_sha(),
        "source_path": str(source_path),
        "doi_count": len(by_doi),
        "strategy_rows": len(rows),
        "recovered_doi_count": len(recovered),
        "recovered_dois": recovered,
        "best_category_counts": dict(Counter(row["category"] for row in best_by_doi.values())),
        "per_strategy_category_counts": dict(sorted(per_strategy.items())),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report_rows = "\n".join(
        "<tr>"
        f"<td><code>{html.escape(row['doi'])}</code></td>"
        f"<td>{html.escape(row['publisher'])}</td>"
        f"<td>{html.escape(row['host'])}</td>"
        f"<td>{html.escape(row['strategy_name'])}</td>"
        f"<td><code>{html.escape(row['category'])}</code></td>"
        f"<td>{row['status_code'] if row['status_code'] is not None else ''}</td>"
        f"<td>{html.escape(row['content_type'])}</td>"
        f"<td>{row['size_bytes']}</td>"
        f"<td><code>{html.escape(row['candidate_url'])}</code></td>"
        "</tr>"
        for row in rows
    )
    report = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(run_id)}</title>
<style>body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:24px;color:#111827}}table{{border-collapse:collapse;width:100%;font-size:13px}}td,th{{border-bottom:1px solid #e5e7eb;padding:6px;text-align:left;vertical-align:top}}th{{background:#f1f5f9}}.pos{{color:#15803d;font-weight:700}}</style>
</head><body>
<h1>{html.escape(run_id)}</h1>
<p>No-storage provider PDF strategy probe. Query strings, signed diagnostics, cookies, and secret values are omitted from artifacts.</p>
<p><b class="pos">Recovered DOI count: {len(recovered)}/{len(by_doi)}</b></p>
<table><thead><tr><th>DOI</th><th>Publisher</th><th>Host</th><th>Strategy</th><th>Category</th><th>Status</th><th>Content-Type</th><th>Bytes</th><th>URL</th></tr></thead><tbody>
{report_rows}
</tbody></table>
</body></html>
"""
    (out_dir / "report.html").write_text(report, encoding="utf-8")


def run_probe(args: argparse.Namespace) -> int:
    load_env_file(Path(args.env_file) if args.env_file else REPO_ROOT / ".env")
    recipes = load_recipe_strategies(args.recipe_file)
    strategies = strategy_list(args.strategies, recipes)
    records = filter_records(
        read_input_records(Path(args.input)),
        category=args.category,
        publisher=args.publisher,
        host=args.host,
        limit=args.limit,
    )
    run_id = args.run_id or f"provider-pdf-probe-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    rows: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        print(
            f"{index}/{len(records)} {progress_record_label(record, show_doi=args.show_dois)}",
            flush=True,
        )
        for strategy in strategies:
            params = strategy_params(strategy, record.fetch_url or record.candidate_url, recipes)
            status_code, content_type, body, resolved_url, error = zyte_fetch(params, timeout=args.timeout)
            row = classify_pdf_content(
                PdfEvidence(
                    doi=record.doi,
                    work_id=record.work_id,
                    title=record.title,
                    publisher=record.publisher,
                    host=record.host,
                    input_url=record.input_url,
                    candidate_url=record.candidate_url,
                    candidate_source=f"provider_probe:{strategy}",
                    resolved_url=resolved_url or record.candidate_url,
                    status_code=status_code if isinstance(status_code, int) else None,
                    content_type=content_type,
                    body=body,
                    pdf_expected=True,
                    mode="provider_probe",
                    error=error,
                ),
                run_id=run_id,
            ).to_dict()
            row["baseline_category"] = record.baseline_category
            row["strategy_name"] = strategy
            rows.append(row)
            time.sleep(args.sleep)

    out_dir = Path(args.out) / run_id
    write_probe_artifacts(rows, out_dir, run_id=run_id, source_path=Path(args.input))
    print(out_dir)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DEFAULT_ROWS), help="PDF rows.ndjson or CSV work queue")
    parser.add_argument("--category", default="missing_pdf_harvest", help="Baseline category filter; empty disables")
    parser.add_argument("--publisher", default="", help="Exact publisher filter")
    parser.add_argument("--host", default="", help="Host substring filter")
    parser.add_argument("--limit", type=int, default=3, help="Maximum DOI records to probe")
    parser.add_argument("--strategies", default="all", help="Comma list or 'all'")
    parser.add_argument(
        "--recipe-file",
        default="",
        help=(
            "Optional JSON file of provider-advised Zyte strategy templates. "
            "Format: {\"strategies\":[{\"name\":\"ticket_recipe\","
            "\"params\":{\"url\":\"{url}\",...}}]}"
        ),
    )
    parser.add_argument("--out", default="pdf_eval_runs/")
    parser.add_argument("--run-id", default="")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--sleep", type=float, default=0.5)
    parser.add_argument("--env-file", default="")
    parser.add_argument(
        "--show-dois",
        action="store_true",
        help="Include DOI values in progress logs. Off by default to keep shared probe logs redacted.",
    )
    args = parser.parse_args(argv)
    return run_probe(args)


if __name__ == "__main__":
    raise SystemExit(main())
