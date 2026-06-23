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
    PUBLIC_TRUE_FAILURE_FIELDS,
    REVIEW_PACK_FIELDS,
    REVIEW_QUEUE_FIELDS,
    build_review_pack,
    build_public_true_failure_queue,
    build_review_queue,
    generate_availability_rows,
    normalize_doi,
    read_csv_rows,
    read_evidence_rows,
    read_eval_rows,
    read_sidecar,
    summarize_availability_sidecar,
    summarize_public_true_failures,
    summarize_review_pack,
    summarize_review_queue,
    write_csv_rows,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", help="Source corpus CSV, such as human-goldie.csv or merged-FINAL.csv")
    parser.add_argument("--out", help="Draft sidecar CSV to write")
    parser.add_argument("--review-queue", help="Human review queue CSV to write")
    parser.add_argument(
        "--review-pack-from-queue",
        help="Existing review queue CSV to sample for --review-pack-out without regenerating sidecars",
    )
    parser.add_argument("--eval-rows", help="Optional latest Taxicab PDF rows.ndjson to join by DOI")
    parser.add_argument(
        "--evidence-rows",
        action="append",
        default=[],
        help="Optional provider/gold evidence rows.ndjson or CSV; may be passed more than once",
    )
    parser.add_argument("--seed-sidecar", help="Optional reviewed/seed sidecar to copy labels by DOI")
    parser.add_argument("--summary-json", help="Optional availability summary JSON output")
    parser.add_argument("--review-summary-json", help="Optional aggregate-only REVIEW queue summary JSON output")
    parser.add_argument("--review-pack-out", help="Optional bounded human-review pack CSV to write")
    parser.add_argument("--review-pack-summary-json", help="Optional aggregate-only review-pack summary JSON output")
    parser.add_argument("--review-pack-size", type=int, default=250, help="Maximum rows in --review-pack-out")
    parser.add_argument("--review-pack-per-host", type=int, default=5, help="Maximum rows sampled per host in review pack")
    parser.add_argument(
        "--public-true-failures-out",
        help="Optional CSV work queue of public-denominator TRUE rows that are not latest good_pdf",
    )
    parser.add_argument(
        "--public-true-failures-summary-json",
        help="Optional JSON summary for --public-true-failures-out",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.review_pack_from_queue:
        if not (args.review_pack_out or args.review_pack_summary_json):
            raise SystemExit("--review-pack-from-queue requires --review-pack-out or --review-pack-summary-json")
        review_rows = read_csv_rows(Path(args.review_pack_from_queue))
        review_pack = build_review_pack(
            review_rows,
            max_rows=args.review_pack_size,
            per_host=args.review_pack_per_host,
        )
        review_pack_summary = summarize_review_pack(review_pack)
        review_pack_summary.update(
            {
                "review_queue": str(args.review_pack_from_queue),
                "review_queue_total": len(review_rows),
                "review_pack_size": len(review_pack),
                "review_pack_per_host": args.review_pack_per_host,
            }
        )
        summary = {"review_pack_summary": review_pack_summary, "review_pack_total": len(review_pack)}
        if args.review_pack_out:
            write_csv_rows(Path(args.review_pack_out), review_pack, REVIEW_PACK_FIELDS)
            summary["review_pack_out"] = str(args.review_pack_out)
            review_pack_summary["review_pack_out"] = str(args.review_pack_out)
        if args.review_pack_summary_json:
            Path(args.review_pack_summary_json).write_text(
                json.dumps(review_pack_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            summary["review_pack_summary_json"] = str(args.review_pack_summary_json)
        if args.summary_json:
            Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0

    if not args.input or not args.out or not args.review_queue:
        raise SystemExit("--input, --out, and --review-queue are required unless --review-pack-from-queue is used")
    if (args.public_true_failures_out or args.public_true_failures_summary_json) and not args.eval_rows:
        raise SystemExit("--eval-rows is required when exporting public TRUE failures")
    input_path = Path(args.input)
    out_path = Path(args.out)
    review_path = Path(args.review_queue)
    corpus_rows = read_csv_rows(input_path)
    eval_rows = read_eval_rows(Path(args.eval_rows)) if args.eval_rows else {}
    evidence_rows = read_evidence_rows(Path(path) for path in args.evidence_rows)
    seed_rows = read_sidecar(Path(args.seed_sidecar)) if args.seed_sidecar else {}
    source_by_doi = {
        normalize_doi(row.get("DOI") or row.get("doi")): row
        for row in corpus_rows
        if normalize_doi(row.get("DOI") or row.get("doi"))
    }
    labels = generate_availability_rows(
        corpus_rows,
        eval_rows_by_doi=eval_rows,
        evidence_rows_by_doi=evidence_rows,
        seed_by_doi=seed_rows,
    )
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
            "evidence_rows": [str(path) for path in args.evidence_rows],
            "evidence_rows_joined": len(evidence_rows),
            "review_queue_total": len(review_rows),
        }
    )
    review_summary = summarize_review_queue(review_rows)
    summary["review_queue_summary"] = review_summary
    if args.review_summary_json:
        Path(args.review_summary_json).write_text(
            json.dumps(review_summary, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        summary["review_summary_json"] = str(args.review_summary_json)
    if args.review_pack_out or args.review_pack_summary_json:
        review_pack = build_review_pack(
            review_rows,
            max_rows=args.review_pack_size,
            per_host=args.review_pack_per_host,
        )
        review_pack_summary = summarize_review_pack(review_pack)
        review_pack_summary.update(
            {
                "review_queue_total": len(review_rows),
                "review_pack_size": len(review_pack),
                "review_pack_per_host": args.review_pack_per_host,
            }
        )
        summary["review_pack_total"] = len(review_pack)
        summary["review_pack_summary"] = review_pack_summary
        if args.review_pack_out:
            write_csv_rows(Path(args.review_pack_out), review_pack, REVIEW_PACK_FIELDS)
            summary["review_pack_out"] = str(args.review_pack_out)
            review_pack_summary["review_pack_out"] = str(args.review_pack_out)
        if args.review_pack_summary_json:
            Path(args.review_pack_summary_json).write_text(
                json.dumps(review_pack_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            summary["review_pack_summary_json"] = str(args.review_pack_summary_json)
    if args.public_true_failures_out or args.public_true_failures_summary_json:
        public_true_failures = build_public_true_failure_queue(
            labels,
            eval_rows_by_doi=eval_rows,
            source_rows_by_doi=source_by_doi,
        )
        public_true_summary = summarize_public_true_failures(public_true_failures)
        public_true_summary.update(
            {
                "input": str(input_path),
                "eval_rows": str(args.eval_rows or ""),
                "availability_sidecar": str(out_path),
            }
        )
        summary["public_true_failure_total"] = public_true_summary["total"]
        if args.public_true_failures_out:
            write_csv_rows(Path(args.public_true_failures_out), public_true_failures, PUBLIC_TRUE_FAILURE_FIELDS)
            summary["public_true_failures_out"] = str(args.public_true_failures_out)
            public_true_summary["public_true_failures_out"] = str(args.public_true_failures_out)
        if args.public_true_failures_summary_json:
            Path(args.public_true_failures_summary_json).write_text(
                json.dumps(public_true_summary, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            summary["public_true_failures_summary_json"] = str(args.public_true_failures_summary_json)
    if args.summary_json:
        Path(args.summary_json).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
