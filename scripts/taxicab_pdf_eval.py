#!/usr/bin/env python3
"""Run the Taxicab PDF retrieval-quality eval."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty
from typing import Any
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.pdf_eval_harness import (  # noqa: E402
    PDF_CATEGORIES,
    PDF_CATEGORY_GOOD_PDF,
    PDF_CATEGORY_NO_PDF_EXPECTED,
    PDF_CATEGORY_TAXICAB_ERROR,
    PDF_CATEGORY_TIMEOUT,
    PdfEvidence,
    classify_pdf_content,
    classify_pdf_lookup_payload,
    classify_pdf_reharvest_post,
    classify_pdf_uuid_download_error,
    default_pdf_run_id,
    host_from_url,
    latest_pdf_row_by_doi,
    make_pdf_transport_row,
    pdf_row_from_dict,
    read_pdf_rows_ndjson,
    write_pdf_artifacts,
)
from openalex_taxicab.publisher_index import classify_row as classify_publisher  # noqa: E402
from scripts.taxicab_eval import TaxicabClient, create_browserbase_session, release_browserbase_session  # noqa: E402


DEFAULT_CORPUS = Path("/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/data/merged-FINAL.csv")
DEFAULT_BASE_URL = "http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com"
PDF_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "pdf"
PDF_SMOKE_DOIS = [
    {"DOI": "10.1126/science.13.336.914", "Link": "https://doi.org/10.1126/science.13.336.914"},
    {"DOI": "10.1016/j.aftran.2024.100020", "Link": "https://doi.org/10.1016/j.aftran.2024.100020"},
    {"DOI": "10.1371/journal.pone.0192138", "Link": "https://doi.org/10.1371/journal.pone.0192138"},
    {"DOI": "10.3390/ijms24010001", "Link": "https://doi.org/10.3390/ijms24010001"},
    {"DOI": "10.9999/openalex-taxicab-pdf-missing-smoke", "Link": "https://doi.org/10.9999/openalex-taxicab-pdf-missing-smoke"},
]


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return ""


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_dir_for(out: Path, run_id: str) -> Path:
    if out.name == run_id:
        return out
    return out / run_id


def normalize_input_row(row: dict[str, Any]) -> dict[str, str]:
    normalized = {str(key): "" if value is None else str(value) for key, value in row.items()}
    doi = (normalized.get("DOI") or normalized.get("doi") or "").strip()
    if doi and "DOI" not in normalized:
        normalized["DOI"] = doi
    input_url = (
        normalized.get("Link")
        or normalized.get("link")
        or normalized.get("url")
        or normalized.get("resolved_url")
        or (f"https://doi.org/{doi}" if doi else "")
    ).strip()
    if input_url:
        normalized["Link"] = input_url
    return normalized


def read_corpus(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for item in reader:
            row = normalize_input_row(item)
            if row.get("DOI") or row.get("doi"):
                rows.append(row)
    return rows


def read_doi_file(path: Path) -> list[dict[str, str]]:
    suffix = path.suffix.lower()
    rows: list[dict[str, str]] = []
    if suffix == ".csv":
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            for item in reader:
                row = normalize_input_row(item)
                if row.get("DOI") or row.get("doi"):
                    rows.append(row)
        return rows
    if suffix in {".jsonl", ".ndjson"}:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    row = normalize_input_row(json.loads(line))
                    if row.get("DOI") or row.get("doi"):
                        rows.append(row)
        return rows
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            doi = line.strip()
            if doi and not doi.startswith("#"):
                rows.append({"DOI": doi, "Link": f"https://doi.org/{doi}"})
    return rows


def row_doi_and_input_url(row: dict[str, str]) -> tuple[str, str]:
    doi = (row.get("DOI") or row.get("doi") or "").strip()
    input_url = (row.get("Link") or row.get("link") or f"https://doi.org/{doi}").strip()
    return doi, input_url


def row_pdf_expected(row: dict[str, str]) -> bool:
    for key in ("pdf_expected", "PDF Expected", "has_pdf", "has_content_pdf"):
        if key not in row:
            continue
        value = str(row.get(key, "")).strip().lower()
        if value in {"0", "false", "no", "n", "none"}:
            return False
        if value in {"1", "true", "yes", "y"}:
            return True
    pdf_url_columns = ("PDF URL", "pdf_url", "pdf", "fulltext_pdf_url")
    if any(key in row for key in pdf_url_columns):
        if any((row.get(key) or "").strip() for key in pdf_url_columns):
            return True
        resolves = str(row.get("Resolves To PDF") or row.get("resolves_to_pdf") or "").strip().lower()
        return resolves in {"1", "true", "yes", "y"}
    return True


def row_pdf_url(row: dict[str, str]) -> str:
    for key in ("PDF URL", "pdf_url", "pdf", "fulltext_pdf_url"):
        value = (row.get(key) or "").strip()
        if value:
            return value
    return ""


def row_title(row: dict[str, str]) -> str:
    return (row.get("title") or row.get("Title") or row.get("display_name") or "").strip()


def row_work_id(row: dict[str, str]) -> str:
    return (row.get("work_id") or row.get("Work ID") or row.get("openalex_id") or "").strip()


def row_publisher(row: dict[str, str], *, resolved_url: str = "") -> str:
    explicit = (row.get("publisher") or row.get("Publisher") or "").strip()
    if explicit:
        return explicit
    return classify_publisher(row, allow_network=False, resolved_url=resolved_url)


def run_fixture_smoke(out_dir: Path, run_id: str) -> int:
    manifest_path = PDF_FIXTURE_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    rows = []
    mismatches = []
    for item in manifest["fixtures"]:
        body = (PDF_FIXTURE_DIR / item["file"]).read_bytes()
        row = classify_pdf_content(
            PdfEvidence(
                doi=item.get("doi", f"fixture/{item['file']}"),
                work_id=item.get("work_id", ""),
                title=item.get("title", ""),
                publisher=item.get("publisher", "fixture"),
                input_url=item.get("input_url", ""),
                candidate_url=item.get("candidate_url", ""),
                candidate_source=item.get("candidate_source", "fixture"),
                resolved_url=item.get("resolved_url", ""),
                content_type=item.get("content_type", ""),
                body=body,
                pdf_expected=item.get("pdf_expected", True),
                status_code=item.get("status_code", 200),
                mode="fixture",
            ),
            run_id=run_id,
        )
        rows.append(row)
        if row.category != item["expected"]:
            mismatches.append(f"{item['file']}: expected {item['expected']} got {row.category}")
    for item in manifest.get("synthetic_rows", []):
        rows.append(
            make_pdf_transport_row(
                run_id=run_id,
                doi=item["doi"],
                work_id=item.get("work_id", ""),
                category=item["expected"],
                publisher=item.get("publisher", "fixture"),
                input_url=item.get("input_url", ""),
                candidate_url=item.get("candidate_url", ""),
                candidate_source=item.get("candidate_source", "fixture"),
                status_code=item.get("status_code"),
                mode="fixture",
                error=item.get("error", item["expected"]),
            )
        )
    run_dir = run_dir_for(out_dir, run_id)
    write_pdf_artifacts(rows, run_dir, run_id=run_id, mode="fixture", corpus_path=str(manifest_path), git_sha=git_sha())
    if mismatches:
        print("pdf fixture smoke failed:", file=sys.stderr)
        for mismatch in mismatches:
            print(f"  {mismatch}", file=sys.stderr)
        return 1
    represented = {row.category for row in rows}
    missing = sorted(set(PDF_CATEGORIES) - represented)
    if missing:
        print(f"pdf fixture smoke failed: missing categories {', '.join(missing)}", file=sys.stderr)
        return 1
    print(f"pdf fixture smoke passed: {len(rows)} fixtures, {len(represented)} categories represented")
    print(run_dir)
    return 0


def classify_live_pdf_row(
    row: dict[str, str],
    *,
    client: TaxicabClient,
    run_id: str,
    reharvest: bool = False,
) -> Any:
    doi, input_url = row_doi_and_input_url(row)
    publisher = row_publisher(row)
    work_id = row_work_id(row)
    expected = row_pdf_expected(row)
    title = row_title(row)
    corpus_pdf_url = row_pdf_url(row)
    reharvest_post_context = ""
    reharvest_post_status_code = None
    reharvest_post_content_type = ""
    reharvest_post_resolved_url = ""

    if not expected:
        return make_pdf_transport_row(
            run_id=run_id,
            doi=doi,
            work_id=work_id,
            category=PDF_CATEGORY_NO_PDF_EXPECTED,
            publisher=publisher,
            input_url=input_url,
            candidate_url=corpus_pdf_url,
            candidate_source="corpus_pdf_url" if corpus_pdf_url else "",
            mode="read_only",
            error="pdf not expected for row",
        )

    if reharvest:
        post_url = corpus_pdf_url or input_url
        post = client.reharvest(doi, post_url)
        overlay = classify_pdf_reharvest_post(
            run_id=run_id,
            doi=doi,
            status_code=post.status_code,
            payload=post.json_data,
            publisher=publisher,
            input_url=input_url,
            candidate_url=post_url,
            candidate_source="corpus_pdf_url" if corpus_pdf_url else "input_url",
            resolved_url=(post.json_data or {}).get("resolved_url", "") if isinstance(post.json_data, dict) else "",
            duration_ms=post.duration_ms,
            error=post.error,
        )
        if overlay is not None:
            return overlay
        if isinstance(post.json_data, dict):
            reharvest_post_resolved_url = str(post.json_data.get("resolved_url") or "")
            reharvest_post_content_type = str(post.json_data.get("content_type") or "")
            post_id = str(post.json_data.get("id") or "")
        else:
            post_id = ""
        reharvest_post_status_code = post.status_code
        pieces = [f"reharvest status {post.status_code}"]
        if post_id:
            pieces.append(f"post id {post_id}")
        if reharvest_post_content_type:
            pieces.append(f"post content_type {reharvest_post_content_type}")
        if reharvest_post_resolved_url:
            pieces.append(f"post resolved_url {reharvest_post_resolved_url}")
        reharvest_post_context = "; ".join(pieces)
        time.sleep(2)

    lookup = client.lookup_doi(doi)
    if lookup.error == "timeout":
        return make_pdf_transport_row(
            run_id=run_id,
            doi=doi,
            work_id=work_id,
            category=PDF_CATEGORY_TIMEOUT,
            publisher=publisher,
            input_url=input_url,
            candidate_url=corpus_pdf_url,
            candidate_source="corpus_pdf_url" if corpus_pdf_url else "",
            duration_ms=lookup.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error="doi lookup timed out",
        )
    if lookup.status_code != 200 or lookup.error:
        return make_pdf_transport_row(
            run_id=run_id,
            doi=doi,
            work_id=work_id,
            category=PDF_CATEGORY_TAXICAB_ERROR,
            publisher=publisher,
            input_url=input_url,
            candidate_url=corpus_pdf_url,
            candidate_source="corpus_pdf_url" if corpus_pdf_url else "",
            status_code=lookup.status_code,
            duration_ms=lookup.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error=lookup.error or f"doi lookup returned {lookup.status_code}",
        )
    transport_row, pdf_record = classify_pdf_lookup_payload(
        run_id=run_id,
        doi=doi,
        work_id=work_id,
        lookup_json=lookup.json_data,
        pdf_expected=expected,
        publisher=publisher,
        input_url=input_url,
        candidate_url=corpus_pdf_url,
        candidate_source="corpus_pdf_url" if corpus_pdf_url else "",
        duration_ms=lookup.duration_ms,
        mode="reharvest" if reharvest else "read_only",
    )
    if transport_row is not None:
        if reharvest and reharvest_post_context:
            validation_errors = list(transport_row.validation_errors)
            validation_errors.append(reharvest_post_context)
            error = "; ".join(part for part in (transport_row.error, reharvest_post_context) if part)
            evidence = "; ".join(part for part in (transport_row.evidence_snippet, reharvest_post_context) if part)
            return replace(
                transport_row,
                host=transport_row.host or host_from_url(reharvest_post_resolved_url or corpus_pdf_url),
                resolved_url=transport_row.resolved_url or reharvest_post_resolved_url,
                status_code=transport_row.status_code if transport_row.status_code is not None else reharvest_post_status_code,
                content_type=transport_row.content_type or reharvest_post_content_type,
                validation_errors=validation_errors,
                evidence_snippet=evidence[:320],
                error=error,
            )
        return transport_row
    assert pdf_record is not None
    uuid = str(pdf_record.get("id") or "")
    resolved_url = str(pdf_record.get("resolved_url") or pdf_record.get("url") or "")
    candidate_url = resolved_url
    candidate_source = "taxicab_pdf_record"
    pdf_count = int(pdf_record.get("_pdf_record_count") or 0)
    publisher = row_publisher(row, resolved_url=resolved_url)
    download = client.download_uuid(uuid)
    if download.error == "timeout":
        return make_pdf_transport_row(
            run_id=run_id,
            doi=doi,
            work_id=work_id,
            category=PDF_CATEGORY_TIMEOUT,
            publisher=publisher,
            input_url=input_url,
            candidate_url=candidate_url,
            candidate_source=candidate_source,
            resolved_url=resolved_url,
            uuid=uuid,
            pdf_record_count=pdf_count,
            duration_ms=download.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error="uuid download timed out",
        )
    if download.status_code != 200:
        return classify_pdf_uuid_download_error(
            run_id=run_id,
            doi=doi,
            work_id=work_id,
            status_code=download.status_code,
            publisher=publisher,
            input_url=input_url,
            candidate_url=candidate_url,
            candidate_source=candidate_source,
            resolved_url=resolved_url,
            uuid=uuid,
            pdf_record_count=pdf_count,
            duration_ms=download.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error=download.error,
        )
    return classify_pdf_content(
        PdfEvidence(
            doi=doi,
            work_id=work_id,
            title=title,
            publisher=publisher,
            input_url=input_url,
            candidate_url=candidate_url,
            candidate_source=candidate_source,
            resolved_url=resolved_url,
            status_code=download.status_code,
            content_type=download.headers.get("Content-Type", ""),
            body=download.content,
            pdf_expected=expected,
            uuid=uuid,
            pdf_record_count=pdf_count,
            duration_ms=download.duration_ms,
            mode="reharvest" if reharvest else "read_only",
        ),
        run_id=run_id,
    )


def maybe_add_pdf_browserbase(
    row: Any,
    *,
    with_browserbase: bool,
    browserbase_mode: str,
    browserbase_timeout: float,
    evidence_dir: Path,
) -> Any:
    if not with_browserbase or row.category == PDF_CATEGORY_GOOD_PDF:
        return row
    evidence = collect_pdf_browserbase_evidence(
        row,
        evidence_dir=evidence_dir,
        mode=browserbase_mode,
        timeout_seconds=browserbase_timeout,
    )
    return replace(
        row,
        browserbase_available=bool(evidence.get("available")),
        browserbase_final_url=str(evidence.get("final_url") or ""),
        browserbase_evidence_path=str(evidence.get("evidence_path") or ""),
        browserbase_verdict=str(evidence.get("verdict") or ""),
    )


def make_pdf_row_watchdog_timeout(
    row: dict[str, str],
    *,
    run_id: str,
    reharvest: bool,
    row_timeout: float,
) -> Any:
    doi, input_url = row_doi_and_input_url(row)
    corpus_pdf_url = row_pdf_url(row)
    return make_pdf_transport_row(
        run_id=run_id,
        doi=doi,
        work_id=row_work_id(row),
        category=PDF_CATEGORY_TIMEOUT,
        publisher=row_publisher(row),
        input_url=input_url,
        candidate_url=corpus_pdf_url,
        candidate_source="corpus_pdf_url" if corpus_pdf_url else "",
        mode="reharvest" if reharvest else "read_only",
        error=f"row exceeded {row_timeout:g}s wall-clock timeout",
    )


def classify_live_pdf_row_worker(output_queue: Queue, token: int, row: dict[str, str], **kwargs: Any) -> None:
    try:
        client = TaxicabClient(kwargs["base_url"], timeout=kwargs["timeout"], retries=kwargs["retries"])
        result = classify_live_pdf_row(row, client=client, run_id=kwargs["run_id"], reharvest=kwargs["reharvest"])
        result = maybe_add_pdf_browserbase(
            result,
            with_browserbase=kwargs["with_browserbase"],
            browserbase_mode=kwargs["browserbase_mode"],
            browserbase_timeout=kwargs["browserbase_timeout"],
            evidence_dir=Path(kwargs["evidence_dir"]),
        )
    except Exception as exc:
        doi, input_url = row_doi_and_input_url(row)
        corpus_pdf_url = row_pdf_url(row)
        result = make_pdf_transport_row(
            run_id=kwargs["run_id"],
            doi=doi,
            work_id=row_work_id(row),
            category=PDF_CATEGORY_TAXICAB_ERROR,
            publisher=row_publisher(row),
            input_url=input_url,
            candidate_url=corpus_pdf_url,
            candidate_source="corpus_pdf_url" if corpus_pdf_url else "",
            mode="reharvest" if kwargs["reharvest"] else "read_only",
            error=f"worker exception: {exc}",
        )
    output_queue.put((token, result.to_dict()))


def append_completed_pdf_row(
    handle: Any,
    completed: list[Any],
    row: Any,
    *,
    idx: int,
    total: int,
    progress_every: int,
) -> None:
    completed.append(row)
    handle.write(json.dumps(row.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    handle.flush()
    if idx % max(1, progress_every) == 0:
        print(f"{idx}/{total} {row.category} {row.doi}")


def run_pdf_rows_with_process_watchdog(
    rows_to_run: list[dict[str, str]],
    *,
    args: argparse.Namespace,
    run_id: str,
    evidence_dir: Path,
    workers: int,
    append_handle: Any,
    completed: list[Any],
) -> None:
    output_queue: Queue = Queue()
    pending = list(enumerate(rows_to_run))
    active: dict[int, tuple[Process, dict[str, str], float]] = {}
    finished_tokens: set[int] = set()
    written = 0
    poll_seconds = 0.2

    def start_next() -> None:
        token, input_row = pending.pop(0)
        process = Process(
            target=classify_live_pdf_row_worker,
            args=(output_queue, token, input_row),
            kwargs={
                "base_url": args.base_url,
                "timeout": args.timeout,
                "retries": args.retries,
                "run_id": run_id,
                "reharvest": args.reharvest,
                "with_browserbase": args.with_browserbase,
                "browserbase_mode": args.browserbase_mode,
                "browserbase_timeout": args.browserbase_timeout,
                "evidence_dir": str(evidence_dir),
            },
        )
        process.start()
        active[token] = (process, input_row, time.monotonic())

    while pending or active:
        while pending and len(active) < workers:
            start_next()

        while True:
            try:
                token, row_data = output_queue.get(timeout=poll_seconds)
            except Empty:
                break
            if token in finished_tokens:
                continue
            process_info = active.pop(token, None)
            if process_info is not None:
                process_info[0].join(timeout=1)
            finished_tokens.add(token)
            written += 1
            append_completed_pdf_row(
                append_handle,
                completed,
                pdf_row_from_dict(row_data),
                idx=written,
                total=len(rows_to_run),
                progress_every=args.progress_every,
            )

        now = time.monotonic()
        for token, (process, input_row, started_at) in list(active.items()):
            if now - started_at <= args.row_timeout:
                continue
            process.terminate()
            process.join(timeout=5)
            if process.is_alive():
                process.kill()
                process.join(timeout=5)
            active.pop(token, None)
            finished_tokens.add(token)
            written += 1
            append_completed_pdf_row(
                append_handle,
                completed,
                make_pdf_row_watchdog_timeout(
                    input_row,
                    run_id=run_id,
                    reharvest=args.reharvest,
                    row_timeout=args.row_timeout,
                ),
                idx=written,
                total=len(rows_to_run),
                progress_every=args.progress_every,
            )


def collect_pdf_browserbase_evidence(
    row: Any,
    *,
    evidence_dir: Path,
    mode: str = "session",
    timeout_seconds: float = 60,
) -> dict[str, Any]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_base = evidence_dir / hashlib.sha1(row.doi.lower().encode()).hexdigest()
    target_url = row.candidate_url or row.resolved_url or row.input_url or f"https://doi.org/{row.doi}"
    api_key = os.environ.get("BROWSERBASE_API_KEY")
    if not api_key:
        payload = {
            "available": False,
            "verdict": "not_configured",
            "doi": row.doi,
            "target_url": target_url,
            "mode": mode,
        }
        out_base.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["evidence_path"] = str(out_base.with_suffix(".json"))
        return payload
    if mode != "session":
        payload = {
            "available": False,
            "verdict": "unsupported_mode",
            "doi": row.doi,
            "target_url": target_url,
            "mode": mode,
            "error": "PDF Browserbase evidence currently supports session mode only",
        }
        out_base.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["evidence_path"] = str(out_base.with_suffix(".json"))
        return payload
    return collect_pdf_browserbase_session_evidence(
        row,
        evidence_dir=evidence_dir,
        out_base=out_base,
        target_url=target_url,
        api_key=api_key,
        timeout_seconds=timeout_seconds,
    )


def classify_browserbase_pdf_bytes(
    row: Any,
    *,
    body: bytes,
    content_type: str,
    final_url: str,
    status_code: int | None = 200,
) -> str:
    classified = classify_pdf_content(
        PdfEvidence(
            doi=getattr(row, "doi", ""),
            work_id=getattr(row, "work_id", ""),
            title=getattr(row, "title", ""),
            publisher=getattr(row, "publisher", ""),
            host=getattr(row, "host", "") or host_from_url(final_url),
            input_url=getattr(row, "input_url", ""),
            candidate_url=getattr(row, "candidate_url", "") or final_url,
            candidate_source="browserbase_session",
            resolved_url=final_url,
            status_code=status_code,
            content_type=content_type,
            body=body,
            pdf_expected=True,
            duration_ms=0,
            mode="browserbase_session",
        ),
        run_id=getattr(row, "run_id", "") or "browserbase-session",
    )
    return classified.category


def browserbase_download_payload(
    row: Any,
    *,
    download: Any,
    out_base: Path,
    target_url: str,
    final_url: str,
    status_code: int | None,
    session_id: str,
) -> dict[str, Any]:
    download_path = out_base.with_suffix(".download")
    download.save_as(str(download_path))
    body = download_path.read_bytes()
    download_url = getattr(download, "url", "") or final_url
    content_type = "application/pdf" if body.startswith(b"%PDF-") else ""
    category = classify_browserbase_pdf_bytes(
        row,
        body=body,
        content_type=content_type,
        final_url=download_url,
        status_code=status_code,
    )
    is_good_pdf = category == PDF_CATEGORY_GOOD_PDF
    evidence_path = download_path
    if is_good_pdf:
        evidence_path = out_base.with_suffix(".pdf")
        download_path.replace(evidence_path)
    payload = {
        "available": bool(is_good_pdf),
        "verdict": "good_pdf_download_candidate" if is_good_pdf else f"download_{category}",
        "doi": row.doi,
        "target_url": target_url,
        "final_url": final_url,
        "mode": "session",
        "session_id": session_id,
        "status_code": status_code,
        "content_type": content_type,
        "size_bytes": len(body),
        "is_pdf": bool(body.startswith(b"%PDF-")),
        "download_detected": True,
        "evidence_path": str(evidence_path),
    }
    return payload


def collect_pdf_browserbase_session_evidence(
    row: Any,
    *,
    evidence_dir: Path,
    out_base: Path,
    target_url: str,
    api_key: str,
    timeout_seconds: float,
) -> dict[str, Any]:
    session_id = ""
    try:
        from playwright.sync_api import sync_playwright

        session = create_browserbase_session(api_key=api_key, doi=row.doi, timeout_seconds=timeout_seconds)
        session_id = session["id"]
        connect_url = session["connect_url"]

        final_url = target_url
        status_code = None
        content_type = ""
        body = b""
        title = ""
        screenshot_path = Path("")
        with sync_playwright() as playwright:
            browser = playwright.chromium.connect_over_cdp(connect_url, timeout=int(timeout_seconds * 1000))
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            downloads: list[Any] = []
            page.on("download", lambda download: downloads.append(download))
            response = page.goto(target_url, wait_until="domcontentloaded", timeout=int(timeout_seconds * 1000))
            try:
                page.wait_for_load_state("networkidle", timeout=min(10000, int(timeout_seconds * 1000)))
            except Exception:
                pass
            page.wait_for_timeout(3000)
            final_url = page.url
            try:
                title = page.title()
            except Exception:
                title = ""
            if response is not None:
                status_code = response.status
                content_type = response.headers.get("content-type", "")
                try:
                    body = response.body()
                except Exception:
                    body = b""
            if not body:
                try:
                    html = page.content()
                except Exception:
                    html = ""
                body = html.encode("utf-8", errors="replace")
            screenshot_path = out_base.with_suffix(".png")
            try:
                page.screenshot(path=str(screenshot_path), full_page=True, timeout=10000)
            except Exception:
                screenshot_path = Path("")
            if downloads:
                payload = browserbase_download_payload(
                    row,
                    download=downloads[-1],
                    out_base=out_base,
                    target_url=target_url,
                    final_url=final_url,
                    status_code=status_code,
                    session_id=session_id,
                )
                if screenshot_path:
                    payload["screenshot_path"] = str(screenshot_path)
                out_base.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
                browser.close()
                return payload
            browser.close()

        is_pdf = body.startswith(b"%PDF-") or "application/pdf" in content_type.lower()
        if is_pdf:
            evidence_path = out_base.with_suffix(".pdf")
            evidence_path.write_bytes(body)
            verdict = "good_pdf_candidate"
        else:
            evidence_path = out_base.with_suffix(".html")
            evidence_path.write_text(body.decode("utf-8", errors="replace"), encoding="utf-8")
            verdict = "html_not_pdf"
        payload = {
            "available": bool(is_pdf),
            "verdict": verdict,
            "doi": row.doi,
            "target_url": target_url,
            "final_url": final_url,
            "mode": "session",
            "session_id": session_id,
            "status_code": status_code,
            "content_type": content_type,
            "size_bytes": len(body),
            "is_pdf": bool(is_pdf),
            "title": title,
            "evidence_path": str(evidence_path),
        }
        if screenshot_path:
            payload["screenshot_path"] = str(screenshot_path)
        out_base.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
    except Exception as exc:
        payload = {
            "available": False,
            "verdict": "error",
            "error": str(exc),
            "doi": row.doi,
            "target_url": target_url,
            "mode": "session",
            "session_id": session_id,
        }
        out_base.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["evidence_path"] = str(out_base.with_suffix(".json"))
        return payload
    finally:
        if session_id:
            try:
                release_browserbase_session(api_key=api_key, session_id=session_id)
            except Exception:
                pass


def run_live(args: argparse.Namespace, run_id: str) -> int:
    if args.smoke:
        corpus_rows = PDF_SMOKE_DOIS
        corpus_label = "built-in pdf smoke"
        corpus_sha = "smoke"
    elif args.doi_file:
        doi_file = Path(args.doi_file)
        corpus_rows = read_doi_file(doi_file)
        corpus_label = str(doi_file)
        corpus_sha = sha1_file(doi_file)
    else:
        corpus_path = Path(args.corpus)
        corpus_rows = read_corpus(corpus_path)
        corpus_label = str(corpus_path)
        corpus_sha = sha1_file(corpus_path)
    if args.publisher:
        corpus_rows = [row for row in corpus_rows if row_publisher(row) == args.publisher]
    if args.limit:
        corpus_rows = corpus_rows[: args.limit]

    run_dir = run_dir_for(Path(args.out), run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    prior_rows = latest_pdf_row_by_doi(read_pdf_rows_ndjson(run_dir / "rows.ndjson")) if args.resume else {}
    rows_to_run = [row for row in corpus_rows if (row.get("DOI") or row.get("doi") or "").strip() not in prior_rows]
    completed = list(prior_rows.values())
    rows_path = run_dir / "rows.ndjson"
    workers = max(1, min(args.workers, 16))
    if args.reharvest:
        workers = min(workers, 4)
        print("WARNING: --reharvest issues POST /taxicab requests and may spend Zyte credits.", file=sys.stderr)
    if args.with_browserbase:
        workers = min(workers, 2)
    evidence_dir = run_dir / "browserbase"
    thread_local = threading.local()

    def get_client() -> TaxicabClient:
        client = getattr(thread_local, "client", None)
        if client is None:
            client = TaxicabClient(args.base_url, timeout=args.timeout, retries=args.retries)
            thread_local.client = client
        return client

    def classify_with_thread_client(row: dict[str, str]) -> Any:
        result = classify_live_pdf_row(row, client=get_client(), run_id=run_id, reharvest=args.reharvest)
        return maybe_add_pdf_browserbase(
            result,
            with_browserbase=args.with_browserbase,
            browserbase_mode=args.browserbase_mode,
            browserbase_timeout=args.browserbase_timeout,
            evidence_dir=evidence_dir,
        )

    with open(rows_path, "a", encoding="utf-8") as handle:
        if args.row_timeout and args.row_timeout > 0:
            run_pdf_rows_with_process_watchdog(
                rows_to_run,
                args=args,
                run_id=run_id,
                evidence_dir=evidence_dir,
                workers=workers,
                append_handle=handle,
                completed=completed,
            )
        elif workers == 1:
            for idx, row in enumerate(rows_to_run, start=1):
                result = classify_live_pdf_row(row, client=get_client(), run_id=run_id, reharvest=args.reharvest)
                result = maybe_add_pdf_browserbase(
                    result,
                    with_browserbase=args.with_browserbase,
                    browserbase_mode=args.browserbase_mode,
                    browserbase_timeout=args.browserbase_timeout,
                    evidence_dir=evidence_dir,
                )
                completed.append(result)
                handle.write(json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
                handle.flush()
                if idx % max(1, args.progress_every) == 0:
                    print(f"{idx}/{len(rows_to_run)} {result.category} {result.doi}")
        else:
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = [executor.submit(classify_with_thread_client, row) for row in rows_to_run]
                for idx, future in enumerate(as_completed(futures), start=1):
                    result = future.result()
                    completed.append(result)
                    handle.write(json.dumps(result.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
                    handle.flush()
                    if idx % max(1, args.progress_every) == 0:
                        print(f"{idx}/{len(rows_to_run)} {result.category} {result.doi}")

    final_rows = list(latest_pdf_row_by_doi(completed).values())
    write_pdf_artifacts(
        final_rows,
        run_dir,
        run_id=run_id,
        base_url=args.base_url,
        mode="reharvest" if args.reharvest else "read_only",
        corpus_path=corpus_label,
        corpus_sha1=corpus_sha,
        git_sha=git_sha(),
    )
    print(f"wrote {len(final_rows)} rows to {run_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--out", default="pdf_eval_runs")
    parser.add_argument("--doi-file", help="CSV, NDJSON, or text DOI/candidate queue")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--publisher")
    parser.add_argument("--states")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=60)
    parser.add_argument("--row-timeout", type=float, default=0, help="Optional wall-clock timeout per row; uses killable child processes when set")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--run-id")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--fixture-smoke", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--with-browserbase", action="store_true")
    parser.add_argument("--browserbase-mode", choices=["fetch", "session"], default="session")
    parser.add_argument("--browserbase-timeout", type=float, default=60)
    parser.add_argument("--reharvest", action="store_true")
    parser.add_argument("--progress-every", type=int, default=25)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_id = args.run_id or default_pdf_run_id("taxicab-pdf-fixture" if args.fixture_smoke else "taxicab-pdf")
    if args.fixture_smoke:
        return run_fixture_smoke(Path(args.out), run_id)
    return run_live(args, run_id)


if __name__ == "__main__":
    raise SystemExit(main())
