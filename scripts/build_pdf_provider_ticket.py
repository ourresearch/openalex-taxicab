#!/usr/bin/env python3
"""Build a private ignored-local Zyte ticket packet for PDF residual lanes."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.pdf_provider_ticket import write_provider_ticket  # noqa: E402


DEFAULT_ROWS = REPO_ROOT / "pdf_eval_runs" / "pdf-full10k-after-osti-plos-ee9001b" / "rows.ndjson"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", default=str(DEFAULT_ROWS), help="Full PDF eval rows.ndjson")
    parser.add_argument("--out", default=str(REPO_ROOT / "pdf_eval_runs"), help="Ignored local output root")
    parser.add_argument("--run-id", default="", help="Output run id")
    parser.add_argument("--top-lanes", type=int, default=25, help="Provider lanes to include")
    parser.add_argument("--samples-per-lane", type=int, default=3, help="DOI examples per lane")
    args = parser.parse_args(argv)

    paths = write_provider_ticket(
        Path(args.rows),
        Path(args.out),
        run_id=args.run_id,
        top_lanes=args.top_lanes,
        samples_per_lane=args.samples_per_lane,
    )
    print(paths["run_dir"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
