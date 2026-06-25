#!/usr/bin/env python3
"""Run one 100-DOI Taxicab -> Parseland end-to-end batch.

The batch input is the PDF availability sidecar. The script keeps the language
simple in the output: each row says whether Taxicab found a real PDF, whether
Taxicab found useful HTML, and whether Parseland extracted anything useful from
that HTML.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse, urlsplit, urlunsplit

import requests


DEFAULT_SIDECAR = Path("/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/data/merged-FINAL-pdf-availability.draft.csv")
DEFAULT_TAXICAB = "http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com"
DEFAULT_PARSELAND = "http://parseland-load-balancer-667160048.us-east-1.elb.amazonaws.com"

BOT_OR_LOGIN_RE = re.compile(
    r"(captcha|cloudflare|access denied|anubis|login\.wolterskluwer|sign in|log in|institution)",
    re.IGNORECASE,
)


def clean_url(url: str) -> str:
    text = (url or "").strip()
    if not text:
        return ""
    parts = urlsplit(text)
    if not parts.scheme or not parts.netloc:
        return text
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def host(url: str) -> str:
    try:
        return urlparse(url or "").netloc.lower().removeprefix("www.")
    except Exception:
        return ""


def is_real_url(value: str) -> bool:
    text = (value or "").strip()
    return bool(text and text.upper() != "N/A" and text.lower().startswith(("http://", "https://")))


def read_sidecar(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader if (row.get("DOI") or "").strip()]
    return rows


def pick_batch(rows: list[dict[str, str]], batch_number: int, batch_size: int) -> list[dict[str, str]]:
    if batch_number < 1:
        raise SystemExit("--batch-number must be 1 or greater")
    start = (batch_number - 1) * batch_size
    end = start + batch_size
    batch = rows[start:end]
    if not batch:
        raise SystemExit(f"no rows for batch {batch_number}")
    return batch


def latest_record(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not records:
        return None

    def key(record: dict[str, Any]) -> str:
        return str(record.get("created_date") or record.get("created_timestamp") or "")

    return sorted(records, key=key, reverse=True)[0]


def get(session: requests.Session, url: str, timeout: float) -> tuple[int | None, dict[str, str], bytes, str, int]:
    start = time.perf_counter()
    try:
        response = session.get(url, timeout=timeout)
        ms = int((time.perf_counter() - start) * 1000)
        return response.status_code, dict(response.headers), response.content, "", ms
    except requests.RequestException as exc:
        ms = int((time.perf_counter() - start) * 1000)
        return None, {}, b"", str(exc), ms


def post_reharvest(session: requests.Session, base_url: str, doi: str, url: str, timeout: float) -> dict[str, Any]:
    payload = {"native_id": doi, "native_id_namespace": "doi", "url": url}
    start = time.perf_counter()
    try:
        response = session.post(f"{base_url.rstrip()}/taxicab", json=payload, timeout=timeout)
        ms = int((time.perf_counter() - start) * 1000)
        data: Any = None
        if response.content:
            try:
                data = response.json()
            except ValueError:
                data = None
        return {
            "status": response.status_code,
            "duration_ms": ms,
            "content_type": data.get("content_type", "") if isinstance(data, dict) else "",
            "resolved_url": clean_url(data.get("resolved_url", "")) if isinstance(data, dict) else "",
            "id_present": bool(data.get("id")) if isinstance(data, dict) else False,
            "error": "",
        }
    except requests.RequestException as exc:
        ms = int((time.perf_counter() - start) * 1000)
        return {"status": None, "duration_ms": ms, "content_type": "", "resolved_url": "", "id_present": False, "error": str(exc)}


def parse_parseland_payload(body: bytes) -> dict[str, Any]:
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception as exc:
        return {"parseland_json_error": str(exc)}
    if not isinstance(data, dict):
        return {"parseland_json_error": "payload was not an object"}
    urls = data.get("urls") or []
    pdf_urls: list[str] = []
    for item in urls:
        value = item.get("url") if isinstance(item, dict) else str(item)
        if value and re.search(r"pdf|pdfft|download", value, re.IGNORECASE):
            pdf_urls.append(clean_url(value))
    return {
        "parseland_error": str(data.get("error") or ""),
        "parseland_authors_count": len(data.get("authors") or []),
        "parseland_urls_count": len(urls),
        "parseland_has_abstract": bool(str(data.get("abstract") or "").strip()),
        "parseland_pdf_url_count": len(pdf_urls),
        "parseland_first_pdf_url": pdf_urls[0] if pdf_urls else "",
    }


def check_one(row: dict[str, str], *, taxicab_url: str, parseland_url: str, timeout: float, reharvest: bool) -> dict[str, Any]:
    session = requests.Session()
    doi = (row.get("DOI") or "").strip()
    pdf_gold_url = (row.get("pdf_gold_url") or "").strip()
    public_choice = (row.get("pdf_gold_include_in_public_denominator") or "").strip().upper()
    pdf_status = (row.get("pdf_gold_status") or "").strip()
    expected_pdf = public_choice == "TRUE"
    review_needed = public_choice == "REVIEW"
    input_url = f"https://doi.org/{doi}"

    result: dict[str, Any] = {
        "DOI": doi,
        "pdf_gold_status": pdf_status,
        "pdf_gold_url": clean_url(pdf_gold_url),
        "expected_pdf": expected_pdf,
        "needs_manual_review": review_needed,
        "input_url": input_url,
    }

    if reharvest:
        result["html_reharvest"] = post_reharvest(session, taxicab_url, doi, input_url, timeout)
        if is_real_url(pdf_gold_url):
            result["pdf_reharvest"] = post_reharvest(session, taxicab_url, doi, pdf_gold_url, timeout)
        time.sleep(2)

    status, _headers, body, error, ms = get(session, f"{taxicab_url.rstrip()}/taxicab/doi/{quote(doi, safe='')}", timeout)
    result.update({"taxicab_lookup_status": status, "taxicab_lookup_ms": ms, "taxicab_lookup_error": error})
    if status != 200 or error:
        result.update({"row_result": "review", "row_reason": "Taxicab DOI lookup failed"})
        return result
    try:
        lookup = json.loads(body.decode("utf-8"))
    except Exception as exc:
        result.update({"row_result": "review", "row_reason": f"Taxicab returned bad JSON: {exc}"})
        return result

    html_records = lookup.get("html") or []
    pdf_records = lookup.get("pdf") or []
    result["html_record_count"] = len(html_records)
    result["pdf_record_count"] = len(pdf_records)

    html = latest_record(html_records)
    if html:
        html_uuid = str(html.get("id") or "")
        html_resolved_url = str(html.get("resolved_url") or html.get("url") or "")
        result.update(
            {
                "html_uuid": html_uuid,
                "html_resolved_url": clean_url(html_resolved_url),
                "html_host": host(html_resolved_url),
            }
        )
        h_status, h_headers, h_body, h_error, h_ms = get(session, f"{taxicab_url.rstrip()}/taxicab/{quote(html_uuid, safe='')}", timeout)
        text_head = h_body[:4096].decode("utf-8", "replace")
        html_ok = bool(
            h_status == 200
            and len(h_body) > 1000
            and ("html" in h_headers.get("Content-Type", "").lower() or "<html" in text_head.lower())
            and not BOT_OR_LOGIN_RE.search(text_head)
        )
        result.update(
            {
                "html_download_status": h_status,
                "html_download_ms": h_ms,
                "html_download_error": h_error,
                "html_content_type": h_headers.get("Content-Type", ""),
                "html_size_bytes": len(h_body),
                "taxicab_found_useful_html": html_ok,
            }
        )
        p_status, _p_headers, p_body, p_error, p_ms = get(session, f"{parseland_url.rstrip()}/parseland/{quote(html_uuid, safe='')}", timeout)
        parsed = parse_parseland_payload(p_body) if p_status == 200 and not p_error else {}
        parseland_useful = bool(
            p_status == 200
            and not p_error
            and (
                parsed.get("parseland_authors_count", 0) > 0
                or parsed.get("parseland_urls_count", 0) > 0
                or parsed.get("parseland_has_abstract")
            )
        )
        result.update(
            {
                "parseland_status": p_status,
                "parseland_ms": p_ms,
                "parseland_request_error": p_error,
                "parseland_found_useful_data": parseland_useful,
                **parsed,
            }
        )
    else:
        result.update({"taxicab_found_useful_html": False, "parseland_found_useful_data": False})

    valid_pdf_uuids: list[str] = []
    first_pdf_detail: dict[str, Any] = {}
    for index, pdf in enumerate(pdf_records[:5]):
        pdf_uuid = str(pdf.get("id") or "")
        resolved_url = str(pdf.get("resolved_url") or pdf.get("url") or "")
        d_status, d_headers, d_body, d_error, d_ms = get(session, f"{taxicab_url.rstrip()}/taxicab/{quote(pdf_uuid, safe='')}", timeout)
        pdf_magic = d_body.startswith(b"%PDF-")
        if index == 0:
            first_pdf_detail = {
                "pdf_uuid": pdf_uuid,
                "pdf_resolved_url": clean_url(resolved_url),
                "pdf_host": host(resolved_url),
                "pdf_download_status": d_status,
                "pdf_download_ms": d_ms,
                "pdf_download_error": d_error,
                "pdf_content_type": d_headers.get("Content-Type", ""),
                "pdf_size_bytes": len(d_body),
                "first_pdf_magic_ok": pdf_magic,
            }
        if pdf_magic:
            valid_pdf_uuids.append(pdf_uuid)
    result.update(first_pdf_detail)
    result["taxicab_found_valid_pdf"] = bool(valid_pdf_uuids)
    result["valid_pdf_record_count"] = len(valid_pdf_uuids)

    if review_needed:
        result.update({"row_result": "review", "row_reason": "availability label still needs review"})
    elif expected_pdf and result["taxicab_found_valid_pdf"]:
        result.update({"row_result": "pass", "row_reason": "public PDF expected and Taxicab found a real PDF"})
    elif expected_pdf and not result["taxicab_found_valid_pdf"]:
        result.update({"row_result": "fail", "row_reason": "public PDF expected but Taxicab did not find a real PDF"})
    elif not expected_pdf and not result["taxicab_found_valid_pdf"]:
        result.update({"row_result": "pass", "row_reason": "no public PDF expected and Taxicab did not find a PDF"})
    else:
        result.update({"row_result": "fail", "row_reason": "no public PDF expected but Taxicab found a PDF"})
    return result


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, sort_keys=True) if isinstance(value, dict) else value for key, value in row.items()})


def summarize(rows: list[dict[str, Any]], *, batch_number: int, batch_size: int, sidecar: Path, reharvest: bool) -> dict[str, Any]:
    total = len(rows)
    result_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    host_failures: dict[str, int] = {}
    for row in rows:
        result_counts[str(row.get("row_result") or "")] = result_counts.get(str(row.get("row_result") or ""), 0) + 1
        status_counts[str(row.get("pdf_gold_status") or "")] = status_counts.get(str(row.get("pdf_gold_status") or ""), 0) + 1
        if row.get("row_result") == "fail":
            h = str(row.get("pdf_host") or row.get("html_host") or "unknown")
            host_failures[h] = host_failures.get(h, 0) + 1
    pass_count = result_counts.get("pass", 0)
    fail_count = result_counts.get("fail", 0)
    review_count = result_counts.get("review", 0)
    scored_total = pass_count + fail_count
    return {
        "run_id": f"taxicab-e2e-batch-{batch_number:03d}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "sidecar": str(sidecar),
        "batch_number": batch_number,
        "batch_size": batch_size,
        "reharvest": reharvest,
        "total_rows": total,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "review_count": review_count,
        "scored_total": scored_total,
        "accuracy_on_scored_rows": round(pass_count / scored_total, 6) if scored_total else None,
        "result_counts": result_counts,
        "pdf_gold_status_counts": status_counts,
        "expected_public_pdf_rows": sum(1 for row in rows if row.get("expected_pdf")),
        "taxicab_valid_pdf_rows": sum(1 for row in rows if row.get("taxicab_found_valid_pdf")),
        "taxicab_useful_html_rows": sum(1 for row in rows if row.get("taxicab_found_useful_html")),
        "parseland_useful_rows": sum(1 for row in rows if row.get("parseland_found_useful_data")),
        "top_failure_hosts": sorted(host_failures.items(), key=lambda item: (-item[1], item[0]))[:20],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sidecar", type=Path, default=DEFAULT_SIDECAR)
    parser.add_argument("--batch-number", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--out", type=Path, default=Path("batch_e2e_runs"))
    parser.add_argument("--taxicab-url", default=DEFAULT_TAXICAB)
    parser.add_argument("--parseland-url", default=DEFAULT_PARSELAND)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--reharvest", action="store_true", help="POST to Taxicab before checking stored records")
    args = parser.parse_args()

    all_rows = read_sidecar(args.sidecar)
    batch = pick_batch(all_rows, args.batch_number, args.batch_size)
    args.out.mkdir(parents=True, exist_ok=True)
    run_dir = args.out / f"batch-{args.batch_number:03d}"
    run_dir.mkdir(parents=True, exist_ok=True)
    batch_csv = run_dir / "batch-input.csv"
    write_csv(batch_csv, batch)

    checked: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
        futures = [
            executor.submit(
                check_one,
                row,
                taxicab_url=args.taxicab_url,
                parseland_url=args.parseland_url,
                timeout=args.timeout,
                reharvest=args.reharvest,
            )
            for row in batch
        ]
        for idx, future in enumerate(as_completed(futures), start=1):
            row = future.result()
            checked.append(row)
            print(f"{idx}/{len(batch)} {row.get('row_result')} {row.get('DOI')} {row.get('row_reason')}", flush=True)

    checked.sort(key=lambda row: [r.get("DOI") for r in batch].index(row["DOI"]))
    (run_dir / "rows.ndjson").write_text("\n".join(json.dumps(row, sort_keys=True) for row in checked) + "\n", encoding="utf-8")
    write_csv(run_dir / "rows.csv", checked)
    summary = summarize(checked, batch_number=args.batch_number, batch_size=args.batch_size, sidecar=args.sidecar, reharvest=args.reharvest)
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
