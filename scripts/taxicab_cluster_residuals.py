#!/usr/bin/env python3
"""Cluster Taxicab eval residuals into next-action work queues."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from openalex_taxicab.residual_clusters import write_cluster_artifacts  # noqa: E402


DEFAULT_ROWS = REPO_ROOT / "eval_runs" / "full10k-missing-reharvest-readonly-fa12038" / "rows.ndjson"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS, help="Taxicab eval rows.ndjson path")
    parser.add_argument("--out", type=Path, required=True, help="Output directory for cluster artifacts")
    parser.add_argument("--run-id", default="", help="Run id to record in residual-clusters.json")
    parser.add_argument("--sample-size", type=int, default=5, help="Representative rows per cluster")
    parser.add_argument("--top-n", type=int, default=50, help="Number of clusters to write")
    args = parser.parse_args(argv)

    if not args.rows.exists():
        parser.error(f"rows file does not exist: {args.rows}")

    paths = write_cluster_artifacts(
        args.rows,
        args.out,
        run_id=args.run_id,
        sample_size=args.sample_size,
        top_n=args.top_n,
    )
    for label, path in paths.items():
        print(f"{label}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
