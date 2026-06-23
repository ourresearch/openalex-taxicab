#!/usr/bin/env python3
"""Generate PDF availability sidecars for Taxicab PDF eval denominators."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.pdf_availability_gold import (  # noqa: E402
    PDF_AVAILABILITY_FIELDS,
    build_review_queue,
    generate_availability_rows,
    normalize_doi,
    read_csv_rows,
    read_eval_rows,
    read_sidecar,
    summarize_availability_sidecar,
    write_csv_rows,
)


REVIEW_QUEUE_FIELDS = (
    *PDF_AVAILABILITY_FIELDS,
    "pdf_gold_priority_host_count",
    "pdf_gold_host",
    "latest_taxicab_category",
    "Link",
    "PDF URL",
    "Notes",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Source corpus CSV, such as human-goldie.csv or merged-FINAL.csv")
    parser.add_argument("--out", required=True, help="Draft sidecar CSV to write")
    parser.add_argument("--review-queue", required=True, help="Human review queue CSV to write")
    parser.add_argument("--eval-rows", help="Optional latest Taxicab PDF rows.ndjson to join by DOI")
    parser.add_argument("--seed-sidecar", help="Optional reviewed/seed sidecar to copy labels by DOI")
    parser.add_argument("--summary-json", help="Optional availability summary JSON output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    input_path = Path(args.input)
    out_path = Path(args.out)
    review_path = Path(args.review_queue)
    corpus_rows = read_csv_rows(input_path)
    eval_rows = read_eval_rows(Path(args.eval_rows)) if args.eval_rows else {}
    seed_rows = read_sidecar(Path(args.seed_sidecar)) if args.seed_sidecar else {}
    source_by_doi = {
        normalize_doi(row.get("DOI") or row.get("doi")): row
        for row in corpus_rows
        if normalize_doi(row.get("DOI") or row.get("doi"))
    }
    labels = generate_availability_rows(corpus_rows, eval_rows_by_doi=eval_rows, seed_by_doi=seed_rows)
    sidecar_rows = [label.to_dict() for label in labels]
    review_rows = build_review_queue(labels, source_rows_by_doi=source_by_doi, eval_rows_by_doi=eval_rows)
    write_csv_rows(out_path, sidecar_rows, PDF_AVAILABILITY_FIELDS)
    write_csv_rows(review_path, review_rows, REVIEW_QUEUE_FIELDS)
    summary = summarize_availability_sidecar(labels)
    summary.update(
        {
            "input": str(input_path),
            "out": str(out_path),
            "review_queue": str(review_path),
            "eval_rows": str(args.eval_rows or ""),
            "seed_sidecar": str(args.seed_sidecar or ""),
            "review_queue_total": len(review_rows),
        }
    )
    if args.summary_json:
        Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
