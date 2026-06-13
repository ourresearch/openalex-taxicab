#!/usr/bin/env python3
"""Run the Taxicab PDF retrieval-quality eval."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import quote

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.pdf_eval_harness import (  # noqa: E402
    PDF_CATEGORIES,
    PDF_CATEGORY_NO_PDF_EXPECTED,
    PDF_CATEGORY_TAXICAB_ERROR,
    PDF_CATEGORY_TIMEOUT,
    PdfEvidence,
    classify_pdf_content,
    classify_pdf_lookup_payload,
    classify_pdf_uuid_download_error,
    default_pdf_run_id,
    latest_pdf_row_by_doi,
    make_pdf_transport_row,
    read_pdf_rows_ndjson,
    write_pdf_artifacts,
)
from openalex_taxicab.publisher_index import classify_row as classify_publisher  # noqa: E402
from scripts.taxicab_eval import TaxicabClient  # noqa: E402


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
) -> Any:
    doi, input_url = row_doi_and_input_url(row)
    publisher = row_publisher(row)
    work_id = row_work_id(row)
    expected = row_pdf_expected(row)
    title = row_title(row)
    corpus_pdf_url = row_pdf_url(row)

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
    )
    if transport_row is not None:
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
            mode="read_only",
        ),
        run_id=run_id,
    )


def run_live(args: argparse.Namespace, run_id: str) -> int:
    if args.reharvest:
        raise SystemExit("--reharvest PDF mode is not implemented yet")
    if args.with_browserbase:
        raise SystemExit("--with-browserbase PDF mode is not implemented yet")
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
    thread_local = threading.local()

    def get_client() -> TaxicabClient:
        client = getattr(thread_local, "client", None)
        if client is None:
            client = TaxicabClient(args.base_url, timeout=args.timeout, retries=args.retries)
            thread_local.client = client
        return client

    def classify_with_thread_client(row: dict[str, str]) -> Any:
        return classify_live_pdf_row(row, client=get_client(), run_id=run_id)

    with open(rows_path, "a", encoding="utf-8") as handle:
        if workers == 1:
            for idx, row in enumerate(rows_to_run, start=1):
                result = classify_live_pdf_row(row, client=get_client(), run_id=run_id)
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
        mode="read_only",
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
