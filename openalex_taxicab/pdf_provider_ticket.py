"""Private Zyte support packet builder for PDF residual lanes.

The generated packet is intended for an ignored local directory. It may contain
DOI-level examples, but it redacts signed/challenge query material and never
includes response bodies or secrets.
"""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from openalex_taxicab.pdf_eval_harness import PdfEvalRow, read_pdf_rows_ndjson
from openalex_taxicab.residual_clusters import (
    NON_RESIDUAL_CATEGORIES,
    path_pattern,
    redact_text,
    redact_url,
    residual_host,
    residual_pattern_url,
)


@dataclass(frozen=True)
class ProviderLane:
    category: str
    publisher: str
    host: str
    candidate_source: str
    path_pattern: str
    rows: tuple[PdfEvalRow, ...]

    @property
    def count(self) -> int:
        return len(self.rows)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def group_provider_lanes(rows: Iterable[PdfEvalRow]) -> list[ProviderLane]:
    grouped: dict[tuple[str, str, str, str, str], list[PdfEvalRow]] = defaultdict(list)
    for row in rows:
        if row.category in NON_RESIDUAL_CATEGORIES:
            continue
        host = residual_host(row)
        source = (row.candidate_source or "unknown").strip() or "unknown"
        pattern = path_pattern(residual_pattern_url(row), fallback_host=host)
        key = (row.category, row.publisher or "unknown", host, source, pattern)
        grouped[key].append(row)

    lanes = [
        ProviderLane(
            category=category,
            publisher=publisher,
            host=host,
            candidate_source=source,
            path_pattern=pattern,
            rows=tuple(items),
        )
        for (category, publisher, host, source, pattern), items in grouped.items()
    ]
    return sorted(lanes, key=lambda lane: (lane.count, lane.category, lane.publisher, lane.host), reverse=True)


def row_example(row: PdfEvalRow) -> dict[str, object]:
    return {
        "doi": row.doi,
        "work_id": row.work_id,
        "category": row.category,
        "publisher": row.publisher or "unknown",
        "host": residual_host(row),
        "candidate_source": row.candidate_source,
        "candidate_url": redact_url(row.candidate_url),
        "resolved_url": redact_url(row.resolved_url),
        "status_code": row.status_code,
        "content_type": row.content_type,
        "size_bytes": row.size_bytes,
        "page_count": row.page_count,
        "validation_errors": list(row.validation_errors or []),
        "evidence_snippet": redact_text((row.evidence_snippet or "")[:240]),
    }


def build_ticket_payload(
    rows: Iterable[PdfEvalRow],
    *,
    run_id: str,
    top_lanes: int = 25,
    samples_per_lane: int = 3,
) -> dict[str, object]:
    lanes = group_provider_lanes(rows)
    selected = lanes[:top_lanes]
    expected_rows = [row for lane in lanes for row in lane.rows]
    return {
        "run_id": run_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "private": True,
        "warning": (
            "Do not commit or publish this packet. It can contain DOI-level examples. "
            "Signed/challenge query material is redacted; response bodies and secrets are omitted."
        ),
        "non_good_expected_rows": len(expected_rows),
        "lane_count": len(lanes),
        "top_lanes": [
            {
                "rank": rank,
                "category": lane.category,
                "publisher": lane.publisher,
                "host": lane.host,
                "candidate_source": lane.candidate_source,
                "path_pattern": lane.path_pattern,
                "rows": lane.count,
                "samples": [row_example(row) for row in lane.rows[:samples_per_lane]],
            }
            for rank, lane in enumerate(selected, start=1)
        ],
    }


def render_markdown(payload: dict[str, object]) -> str:
    lanes = payload.get("top_lanes") or []
    lines = [
        "# Private Taxicab PDF Zyte Provider Ticket",
        "",
        "**Private, ignored-local artifact. Do not commit or publish.**",
        "",
        "## Context",
        "",
        "Taxicab PDF Phase 2 is blocked on provider PDF-byte retrieval lanes. "
        "Zyte is the production core; Browserbase is evidence/gold only. The ask "
        "is for supported Zyte API recipes that return complete article PDF bytes "
        "for accessible full-text routes, not HTML shells, JS redirects, bot pages, "
        "empty responses, corrupt/truncated PDFs, supplements, or previews.",
        "",
        "## Safety",
        "",
        "- This packet omits raw response bodies, cookies, keys, authorization material, Browserbase sessions, and challenge tokens.",
        "- Candidate/resolved URLs have signed and challenge query parameters redacted.",
        "- Keep this file under ignored `pdf_eval_runs/`; publish only aggregate summaries to oxjobs.",
        "",
        "## Snapshot",
        "",
        f"- Run ID: `{payload.get('run_id', '')}`",
        f"- Non-good expected rows represented: `{payload.get('non_good_expected_rows', 0)}`",
        f"- Residual lane count: `{payload.get('lane_count', 0)}`",
        "",
        "## Request",
        "",
        "For each lane below, please provide a Zyte request recipe that can be tested with:",
        "",
        "```bash",
        "python3 scripts/provider_pdf_probe.py \\",
        "  --recipe-file <ignored-recipe.json> \\",
        "  --strategies <recipe_name> \\",
        "  --publisher <publisher> \\",
        "  --host <host> \\",
        "  --limit <n>",
        "```",
        "",
        "The recipe is promotable only after no-storage probe success, already-good preservation, targeted eval, and full-gate no-regression proof.",
        "",
        "## Top Lanes",
        "",
    ]
    for lane in lanes:
        assert isinstance(lane, dict)
        lines.extend(
            [
                f"### {lane.get('rank')}. {lane.get('publisher')} / {lane.get('host')} / `{lane.get('category')}`",
                "",
                f"- Rows: `{lane.get('rows')}`",
                f"- Candidate source: `{lane.get('candidate_source')}`",
                f"- Path pattern: `{lane.get('path_pattern')}`",
                "- Needed Zyte outcome: response body starts with `%PDF-`, validates as complete PDF pages, and matches the requested work.",
                "",
                "| DOI | Candidate URL | Status | Content-Type | Bytes | Page Count | Validation | Evidence |",
                "|---|---|---:|---|---:|---:|---|---|",
            ]
        )
        samples = lane.get("samples") or []
        for sample in samples:
            assert isinstance(sample, dict)
            validation = "; ".join(str(item) for item in sample.get("validation_errors") or [])
            lines.append(
                "| "
                f"`{sample.get('doi', '')}` | "
                f"`{sample.get('candidate_url', '') or sample.get('resolved_url', '')}` | "
                f"{sample.get('status_code') or ''} | "
                f"{sample.get('content_type') or ''} | "
                f"{sample.get('size_bytes') or 0} | "
                f"{sample.get('page_count') or 0} | "
                f"{validation} | "
                f"{str(sample.get('evidence_snippet') or '').replace('|', '/')} |"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_provider_ticket(
    rows_path: Path,
    out_dir: Path,
    *,
    run_id: str = "",
    top_lanes: int = 25,
    samples_per_lane: int = 3,
) -> dict[str, Path]:
    run_id = run_id or f"zyte-provider-ticket-{utc_stamp()}"
    payload = build_ticket_payload(
        read_pdf_rows_ndjson(rows_path),
        run_id=run_id,
        top_lanes=top_lanes,
        samples_per_lane=samples_per_lane,
    )
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = run_dir / "manifest.json"
    packet_path = run_dir / "zyte-provider-ticket.md"
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    packet_path.write_text(render_markdown(payload), encoding="utf-8")
    return {"run_dir": run_dir, "manifest": manifest_path, "packet": packet_path}


__all__ = [
    "ProviderLane",
    "build_ticket_payload",
    "group_provider_lanes",
    "render_markdown",
    "row_example",
    "write_provider_ticket",
]
