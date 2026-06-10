#!/usr/bin/env python3
"""Run the Taxicab V1 retrieval-quality eval."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.eval_harness import (  # noqa: E402
    CATEGORY_TAXICAB_ERROR,
    CATEGORY_TIMEOUT,
    ContentEvidence,
    EvalRow,
    assess_browserbase_html,
    classify_content,
    classify_lookup_payload,
    classify_reharvest_post,
    classify_uuid_download_error,
    default_run_id,
    latest_row_by_doi,
    make_transport_row,
    read_rows_ndjson,
    write_artifacts,
)
from openalex_taxicab.publisher_index import classify_row as classify_publisher  # noqa: E402


DEFAULT_CORPUS = Path("/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/data/merged-FINAL.csv")
DEFAULT_BASE_URL = "http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com"
FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "eval"
SMOKE_DOIS = [
    {"DOI": "10.1002/chin.198035056", "Link": "https://doi.org/10.1002/chin.198035056"},
    {"DOI": "10.1016/j.aftran.2024.100020", "Link": "https://doi.org/10.1016/j.aftran.2024.100020"},
    {"DOI": "10.1371/journal.pone.0192138", "Link": "https://doi.org/10.1371/journal.pone.0192138"},
    {"DOI": "10.3390/ijms24010001", "Link": "https://doi.org/10.3390/ijms24010001"},
    {"DOI": "10.1093/nar/gkaa1106", "Link": "https://doi.org/10.1093/nar/gkaa1106"},
    {"DOI": "10.1038/s41586-020-2649-2", "Link": "https://doi.org/10.1038/s41586-020-2649-2"},
    {"DOI": "10.1126/science.13.336.914", "Link": "https://doi.org/10.1126/science.13.336.914"},
    {"DOI": "10.9999/openalex-taxicab-missing-smoke", "Link": "https://doi.org/10.9999/openalex-taxicab-missing-smoke"},
]


class HttpResult:
    def __init__(
        self,
        *,
        status_code: int | None = None,
        json_data: Any = None,
        content: bytes = b"",
        headers: dict[str, str] | None = None,
        url: str = "",
        error: str = "",
        duration_ms: int | None = None,
    ):
        self.status_code = status_code
        self.json_data = json_data
        self.content = content
        self.headers = headers or {}
        self.url = url
        self.error = error
        self.duration_ms = duration_ms


class TaxicabClient:
    def __init__(self, base_url: str, *, timeout: float, retries: int):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = max(0, retries)
        self.session = requests.Session()

    def _request(self, method: str, url: str, **kwargs: Any) -> HttpResult:
        last_error = ""
        for attempt in range(self.retries + 1):
            start = time.time()
            try:
                response = self.session.request(method, url, timeout=self.timeout, **kwargs)
                duration_ms = int((time.time() - start) * 1000)
                if response.status_code in {502, 503, 504} and attempt < self.retries:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                return HttpResult(
                    status_code=response.status_code,
                    content=response.content,
                    headers=dict(response.headers),
                    url=response.url,
                    duration_ms=duration_ms,
                )
            except requests.Timeout:
                duration_ms = int((time.time() - start) * 1000)
                last_error = "timeout"
                if attempt < self.retries:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                return HttpResult(error=last_error, duration_ms=duration_ms)
            except requests.RequestException as exc:
                duration_ms = int((time.time() - start) * 1000)
                last_error = str(exc)
                if attempt < self.retries:
                    time.sleep(min(2 ** attempt, 8))
                    continue
                return HttpResult(error=last_error, duration_ms=duration_ms)
        return HttpResult(error=last_error or "request failed")

    def lookup_doi(self, doi: str) -> HttpResult:
        result = self._request("GET", f"{self.base_url}/taxicab/doi/{quote(doi, safe='')}")
        if result.status_code == 200:
            try:
                result.json_data = json.loads(result.content.decode("utf-8"))
            except Exception as exc:
                result.error = f"invalid json: {exc}"
        return result

    def download_uuid(self, uuid: str) -> HttpResult:
        return self._request("GET", f"{self.base_url}/taxicab/{quote(uuid, safe='')}")

    def reharvest(self, doi: str, url: str) -> HttpResult:
        payload = {"native_id": doi, "native_id_namespace": "doi", "url": url or f"https://doi.org/{doi}"}
        result = self._request("POST", f"{self.base_url}/taxicab", json=payload)
        if result.content:
            try:
                result.json_data = json.loads(result.content.decode("utf-8"))
            except Exception:
                result.json_data = None
        return result


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return ""


def read_corpus(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            doi = (row.get("DOI") or row.get("doi") or "").strip()
            if doi:
                rows.append(dict(row))
    return rows


def run_dir_for(out: Path, run_id: str) -> Path:
    if out.name == run_id:
        return out
    return out / run_id


def apply_filters(
    rows: list[dict[str, str]],
    *,
    publisher: str | None,
    states: set[str],
    prior_rows: dict[str, EvalRow],
) -> list[dict[str, str]]:
    filtered = rows
    if publisher:
        filtered = [row for row in filtered if classify_publisher(row, allow_network=False) == publisher]
    if states:
        filtered = [row for row in filtered if prior_rows.get((row.get("DOI") or row.get("doi") or "").strip(), None) and prior_rows[(row.get("DOI") or row.get("doi") or "").strip()].category in states]
    return filtered


def classify_live_row(
    row: dict[str, str],
    *,
    client: TaxicabClient,
    run_id: str,
    reharvest: bool,
    with_browserbase: bool,
    evidence_dir: Path,
) -> EvalRow:
    doi = (row.get("DOI") or row.get("doi") or "").strip()
    input_url = (row.get("Link") or row.get("link") or f"https://doi.org/{doi}").strip()
    publisher = classify_publisher(row, allow_network=False)

    if reharvest:
        post = client.reharvest(doi, input_url)
        overlay = classify_reharvest_post(
            run_id=run_id,
            doi=doi,
            status_code=post.status_code,
            payload=post.json_data,
            publisher=publisher,
            input_url=input_url,
            resolved_url=(post.json_data or {}).get("resolved_url", "") if isinstance(post.json_data, dict) else "",
            duration_ms=post.duration_ms,
            error=post.error,
        )
        if overlay is not None:
            return maybe_add_browserbase(overlay, with_browserbase=with_browserbase, evidence_dir=evidence_dir)
        time.sleep(2)

    lookup = client.lookup_doi(doi)
    if lookup.error == "timeout":
        return make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_TIMEOUT,
            publisher=publisher,
            input_url=input_url,
            duration_ms=lookup.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error="doi lookup timed out",
        )
    if lookup.status_code != 200 or lookup.error:
        return make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_TAXICAB_ERROR,
            publisher=publisher,
            input_url=input_url,
            status_code=lookup.status_code,
            duration_ms=lookup.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error=lookup.error or f"doi lookup returned {lookup.status_code}",
        )

    row_result, html_record = classify_lookup_payload(
        run_id=run_id,
        doi=doi,
        lookup_json=lookup.json_data,
        publisher=publisher,
        input_url=input_url,
        duration_ms=lookup.duration_ms,
        mode="reharvest" if reharvest else "read_only",
    )
    if row_result is not None:
        return maybe_add_browserbase(row_result, with_browserbase=with_browserbase, evidence_dir=evidence_dir)

    assert html_record is not None
    uuid = str(html_record.get("id") or "")
    resolved_url = str(html_record.get("resolved_url") or html_record.get("url") or "")
    publisher = classify_publisher(row, allow_network=False, resolved_url=resolved_url)
    download = client.download_uuid(uuid)
    html_count = int(html_record.get("_html_record_count") or 0)
    created_date = str(html_record.get("created_date") or "")
    if download.error == "timeout":
        result = make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_TIMEOUT,
            publisher=publisher,
            input_url=input_url,
            resolved_url=resolved_url,
            uuid=uuid,
            html_record_count=html_count,
            created_date=created_date,
            duration_ms=download.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error="uuid download timed out",
        )
    elif download.status_code != 200:
        result = classify_uuid_download_error(
            run_id=run_id,
            doi=doi,
            status_code=download.status_code,
            publisher=publisher,
            input_url=input_url,
            resolved_url=resolved_url,
            uuid=uuid,
            html_record_count=html_count,
            created_date=created_date,
            duration_ms=download.duration_ms,
            mode="reharvest" if reharvest else "read_only",
            error=download.error,
        )
    else:
        result = classify_content(
            ContentEvidence(
                doi=doi,
                publisher=publisher,
                input_url=input_url,
                resolved_url=resolved_url,
                status_code=download.status_code,
                content_type=download.headers.get("Content-Type", ""),
                body=download.content,
                uuid=uuid,
                html_record_count=html_count,
                created_date=created_date,
                duration_ms=download.duration_ms,
                mode="reharvest" if reharvest else "read_only",
            ),
            run_id=run_id,
        )
    return maybe_add_browserbase(result, with_browserbase=with_browserbase, evidence_dir=evidence_dir)


def maybe_add_browserbase(row: EvalRow, *, with_browserbase: bool, evidence_dir: Path) -> EvalRow:
    if not with_browserbase or row.category == "good_html":
        return row
    evidence = collect_browserbase_evidence(row, evidence_dir=evidence_dir)
    return replace(
        row,
        browserbase_available=bool(evidence.get("available")),
        browserbase_final_url=str(evidence.get("final_url") or ""),
        browserbase_evidence_path=str(evidence.get("evidence_path") or ""),
        browserbase_verdict=str(evidence.get("verdict") or ""),
    )


def collect_browserbase_evidence(row: EvalRow, *, evidence_dir: Path) -> dict[str, Any]:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_base = evidence_dir / hashlib.sha1(row.doi.lower().encode()).hexdigest()
    api_key = os.environ.get("BROWSERBASE_API_KEY")
    if not api_key:
        payload = {"available": False, "verdict": "not_configured", "doi": row.doi}
        out_base.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["evidence_path"] = str(out_base.with_suffix(".json"))
        return payload
    try:
        from browserbase import Browserbase

        bb = Browserbase(api_key=api_key)
        response = bb.fetch_api.create(
            url=f"https://doi.org/{row.doi}",
            format="raw",
            proxies=True,
            allow_redirects=True,
        )
        content = getattr(response, "content", "") or ""
        final_url = getattr(response, "url", "") or row.resolved_url
        out_base.with_suffix(".html").write_text(content, encoding="utf-8", errors="replace")
        verdict = assess_browserbase_html(content, final_url=final_url)
        verdict["doi"] = row.doi
        verdict["evidence_path"] = str(out_base.with_suffix(".html"))
        out_base.with_suffix(".json").write_text(json.dumps(verdict, indent=2), encoding="utf-8")
        return verdict
    except Exception as exc:
        payload = {"available": False, "verdict": "error", "error": str(exc), "doi": row.doi}
        out_base.with_suffix(".json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        payload["evidence_path"] = str(out_base.with_suffix(".json"))
        return payload


def run_fixture_smoke(out_dir: Path, run_id: str) -> int:
    manifest_path = FIXTURE_DIR / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    rows: list[EvalRow] = []
    mismatches: list[str] = []
    for item in manifest["fixtures"]:
        body_path = FIXTURE_DIR / item["file"]
        body = body_path.read_bytes()
        row = classify_content(
            ContentEvidence(
                doi=item.get("doi", f"fixture/{item['file']}"),
                publisher=item.get("publisher", "fixture"),
                input_url=item.get("input_url", ""),
                resolved_url=item.get("resolved_url", ""),
                content_type=item.get("content_type", "text/html"),
                body=body,
                status_code=200,
                mode="fixture",
            ),
            run_id=run_id,
        )
        rows.append(row)
        if row.category != item["expected"]:
            mismatches.append(f"{item['file']}: expected {item['expected']} got {row.category}")
    for item in manifest.get("synthetic_rows", []):
        row = make_transport_row(
            run_id=run_id,
            doi=item["doi"],
            category=item["expected"],
            publisher=item.get("publisher", "fixture"),
            input_url=item.get("input_url", ""),
            status_code=item.get("status_code"),
            mode="fixture",
            error=item.get("error", item["expected"]),
        )
        rows.append(row)
    run_dir = run_dir_for(out_dir, run_id)
    write_artifacts(rows, run_dir, run_id=run_id, mode="fixture", corpus_path=str(manifest_path), git_sha=git_sha())
    if mismatches:
        print("fixture smoke failed:", file=sys.stderr)
        for mismatch in mismatches:
            print(f"  {mismatch}", file=sys.stderr)
        return 1
    represented = {row.category for row in rows}
    print(f"fixture smoke passed: {len(rows)} fixtures, {len(represented)} categories represented")
    print(run_dir)
    return 0


def run_live(args: argparse.Namespace, run_id: str) -> int:
    corpus_path = Path(args.corpus)
    if args.smoke:
        corpus_rows = SMOKE_DOIS
        corpus_sha = "smoke"
        corpus_label = "built-in smoke"
    else:
        corpus_rows = read_corpus(corpus_path)
        corpus_sha = sha1_file(corpus_path)
        corpus_label = str(corpus_path)
    run_dir = run_dir_for(Path(args.out), run_id)
    prior_rows = latest_row_by_doi(read_rows_ndjson(run_dir / "rows.ndjson")) if args.resume or args.states else {}
    states = {s.strip() for s in (args.states or "").split(",") if s.strip()}
    rows_to_run = apply_filters(corpus_rows, publisher=args.publisher, states=states, prior_rows=prior_rows)
    if args.limit:
        rows_to_run = rows_to_run[: args.limit]
    if args.resume:
        rows_to_run = [row for row in rows_to_run if (row.get("DOI") or row.get("doi") or "").strip() not in prior_rows]

    if args.reharvest:
        print("WARNING: --reharvest issues POST /taxicab requests and may spend Zyte credits.", file=sys.stderr)
        workers = min(args.workers, 4)
    else:
        workers = min(args.workers, 16)
    workers = max(1, workers)
    client = TaxicabClient(args.base_url, timeout=args.timeout, retries=args.retries)
    run_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = run_dir / "browserbase"
    rows_path = run_dir / "rows.ndjson"
    completed: list[EvalRow] = list(prior_rows.values()) if (args.resume or args.states) else []

    with open(rows_path, "a", encoding="utf-8") as append_handle:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(
                    classify_live_row,
                    row,
                    client=client,
                    run_id=run_id,
                    reharvest=args.reharvest,
                    with_browserbase=args.with_browserbase,
                    evidence_dir=evidence_dir,
                )
                for row in rows_to_run
            ]
            for idx, future in enumerate(as_completed(futures), start=1):
                row = future.result()
                completed.append(row)
                append_handle.write(json.dumps(row.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
                append_handle.flush()
                if idx % max(1, args.progress_every) == 0:
                    print(f"{idx}/{len(rows_to_run)} {row.category} {row.doi}")

    final_rows = list(latest_row_by_doi(completed).values())
    write_artifacts(
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
    parser.add_argument("--out", default="eval_runs")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--publisher")
    parser.add_argument("--states", help="Comma-separated prior categories to rerun from an existing run")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--run-id")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--fixture-smoke", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--with-browserbase", action="store_true")
    parser.add_argument("--reharvest", action="store_true")
    parser.add_argument("--progress-every", type=int, default=25)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    run_id = args.run_id or default_run_id("taxicab-fixture" if args.fixture_smoke else "taxicab-eval")
    out_dir = Path(args.out)
    if args.fixture_smoke:
        return run_fixture_smoke(out_dir, run_id)
    return run_live(args, run_id)


if __name__ == "__main__":
    raise SystemExit(main())
