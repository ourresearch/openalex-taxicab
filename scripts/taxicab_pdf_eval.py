#!/usr/bin/env python3
"""Run the Taxicab PDF retrieval-quality eval."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.pdf_eval_harness import (  # noqa: E402
    PDF_CATEGORIES,
    PdfEvidence,
    classify_pdf_content,
    default_pdf_run_id,
    make_pdf_transport_row,
    write_pdf_artifacts,
)


DEFAULT_CORPUS = Path("/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/data/merged-FINAL.csv")
DEFAULT_BASE_URL = "http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com"
PDF_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures" / "pdf"


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()
    except Exception:
        return ""


def run_dir_for(out: Path, run_id: str) -> Path:
    if out.name == run_id:
        return out
    return out / run_id


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
    parser.error("live PDF eval is not implemented yet; use --fixture-smoke for this setup slice")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
