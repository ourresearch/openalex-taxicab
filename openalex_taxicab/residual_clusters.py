"""Cluster Taxicab eval residuals into actionable work queues."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from openalex_taxicab.eval_harness import CATEGORY_GOOD_HTML, EvalRow, row_from_dict
from openalex_taxicab.pdf_eval_harness import PdfEvalRow, host_from_url, pdf_row_from_dict


NON_RESIDUAL_CATEGORIES = {
    CATEGORY_GOOD_HTML,
    "good_pdf",
    "no_pdf_expected",
}

RECOVERABILITY_WEIGHTS = {
    "router_only": 0.55,
    "empty_response": 0.55,
    "js_required": 0.60,
    "missing_harvest": 0.35,
    "missing_pdf_harvest": 0.12,
    "bot_block_403": 0.50,
    "pdf_instead_of_html": 0.05,
    "html_instead_of_pdf": 0.40,
    "js_redirect_unresolved": 0.45,
    "interstitial_or_paywall": 0.25,
    "download_404": 0.35,
    "timeout": 0.35,
    "invalid_content": 0.10,
    "corrupt_or_truncated_pdf": 0.20,
    "wrong_pdf_content": 0.15,
    "supplement_or_preview_pdf": 0.05,
    "encrypted_or_unreadable_pdf": 0.08,
    "taxicab_error": 0.10,
}

HOST_OVERRIDES = {
    ("router_only", "mdpi.com"): 0.80,
    ("pdf_instead_of_html", "unknown"): 0.03,
}

BROWSERBASE_CATEGORIES = {
    "router_only",
    "empty_response",
    "js_required",
    "bot_block_403",
    "pdf_instead_of_html",
    "html_instead_of_pdf",
    "js_redirect_unresolved",
    "interstitial_or_paywall",
}

ZYTE_SUPPORT_CATEGORIES = {
    "router_only",
    "empty_response",
    "js_required",
    "bot_block_403",
    "timeout",
    "html_instead_of_pdf",
    "js_redirect_unresolved",
    "interstitial_or_paywall",
    "corrupt_or_truncated_pdf",
}

SENSITIVE_QUERY_PREFIXES = ("X-Amz-",)
SENSITIVE_QUERY_KEYS = {"bm-verify"}


@dataclass(frozen=True)
class ResidualCluster:
    category: str
    publisher: str
    host: str
    count: int
    support_candidates: int
    estimated_recoverable_rows: float
    recommended_agent: str
    recommended_action: str
    evidence_strength: str
    sample_rows: tuple[dict[str, str], ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "publisher": self.publisher,
            "host": self.host,
            "count": self.count,
            "support_candidates": self.support_candidates,
            "estimated_recoverable_rows": round(self.estimated_recoverable_rows, 2),
            "recommended_agent": self.recommended_agent,
            "recommended_action": self.recommended_action,
            "evidence_strength": self.evidence_strength,
            "sample_rows": list(self.sample_rows),
        }


ResidualRow = EvalRow | PdfEvalRow


def cluster_rows(rows: Iterable[ResidualRow], *, sample_size: int = 5) -> list[ResidualCluster]:
    grouped: dict[tuple[str, str, str], list[ResidualRow]] = defaultdict(list)
    for row in rows:
        if row.category in NON_RESIDUAL_CATEGORIES:
            continue
        key = (row.category, row.publisher or "unknown", residual_host(row))
        grouped[key].append(row)

    clusters = [
        _build_cluster(category, publisher, host, items, sample_size=sample_size)
        for (category, publisher, host), items in grouped.items()
    ]
    return sorted(
        clusters,
        key=lambda cluster: (
            cluster.estimated_recoverable_rows,
            cluster.count,
            cluster.category,
            cluster.publisher,
            cluster.host,
        ),
        reverse=True,
    )


def _build_cluster(
    category: str,
    publisher: str,
    host: str,
    rows: list[ResidualRow],
    *,
    sample_size: int,
) -> ResidualCluster:
    weight = HOST_OVERRIDES.get((category, host), RECOVERABILITY_WEIGHTS.get(category, 0.10))
    support_candidates = sum(1 for row in rows if row.support_candidate)
    return ResidualCluster(
        category=category,
        publisher=publisher,
        host=host,
        count=len(rows),
        support_candidates=support_candidates,
        estimated_recoverable_rows=len(rows) * weight,
        recommended_agent=recommended_agent(category, publisher, host),
        recommended_action=recommended_action(category, publisher, host),
        evidence_strength=evidence_strength(category, publisher, host),
        sample_rows=tuple(sample_row(row) for row in rows[:sample_size]),
    )


def residual_host(row: ResidualRow) -> str:
    host = (getattr(row, "host", "") or "").strip()
    if host and host != "unknown":
        return host
    if row.category == "missing_pdf_harvest":
        for url in (
            getattr(row, "candidate_url", "") or "",
            getattr(row, "resolved_url", "") or "",
            getattr(row, "input_url", "") or "",
        ):
            candidate_host = host_from_url(url)
            if candidate_host:
                return candidate_host
    return host or "unknown"


def recommended_agent(category: str, publisher: str, host: str) -> str:
    if category == "router_only" and host == "mdpi.com":
        return "Lens + Envoy"
    if category == "missing_harvest":
        return "Meter + Sentinel"
    if category == "missing_pdf_harvest":
        return "Quarry + Meter"
    if category == "pdf_instead_of_html":
        return "Quarry + Lens"
    if category in {"html_instead_of_pdf", "js_redirect_unresolved", "interstitial_or_paywall"}:
        return "Lens + Envoy"
    if category in {"corrupt_or_truncated_pdf", "encrypted_or_unreadable_pdf"}:
        return "Sentinel + Envoy"
    if category == "bot_block_403":
        return "Lens + Envoy"
    if category in {"empty_response", "js_required"}:
        return "Quarry + Lens"
    return "Meter + Mechanic"


def recommended_action(category: str, publisher: str, host: str) -> str:
    if category == "router_only" and host == "mdpi.com":
        return "Browserbase evidence on fixed DOI sample, then Zyte support packet for bm-verify shells"
    if category == "router_only":
        return "Browserbase sample and resolver/router inspection before any Taxicab routing change"
    if category == "empty_response":
        return "Browserbase sample plus Taxicab content inspection for empty shell or PDF-viewer failure"
    if category == "js_required":
        return "Browserbase sample and Zyte rendering support packet when real browser resolves article"
    if category == "missing_harvest":
        return "Bounded reharvest/read-only verification; accept public lift only through full 10K gate"
    if category == "missing_pdf_harvest":
        return "Cluster by publisher/source URL, run no-storage provider probes, and reharvest only bounded recoverable samples"
    if category == "bot_block_403":
        return "Browserbase comparison and Zyte support packet with representative DOI evidence"
    if category == "pdf_instead_of_html":
        return "Split true PDF-only records from recoverable article landing pages before patching"
    if category == "html_instead_of_pdf":
        return "Compare browser/Zyte bodies and identify whether HTML is a paywall, viewer shell, or resolvable PDF redirect"
    if category == "js_redirect_unresolved":
        return "Use Browserbase gold samples and Zyte support packets for JS redirect chains that should resolve to PDF bytes"
    if category == "interstitial_or_paywall":
        return "Separate unavoidable access walls from recoverable interstitial redirects before route changes"
    if category == "corrupt_or_truncated_pdf":
        return "Validate bytes/page objects across Zyte strategies and escalate reproducible truncation to Zyte"
    if category == "encrypted_or_unreadable_pdf":
        return "Confirm whether PDFs are truly encrypted/legacy or validator-limited before changing retrieval"
    return "Inspect representative rows and classify owner before patching"


def evidence_strength(category: str, publisher: str, host: str) -> str:
    if category == "router_only" and host == "mdpi.com":
        return "high: 119-row host cluster plus 0/5 Zyte reharvest recovery and browser-indexed article evidence"
    if category == "missing_harvest":
        return "medium: prior guarded samples recovered 33/70 and full gate accepted +35 rows"
    if category == "missing_pdf_harvest":
        return "medium-low: current major-publisher probes are mostly zero, so require fresh subcluster evidence"
    if category == "pdf_instead_of_html":
        return "medium-low: 20-row reharvest recovered 1/20, so split before scaling"
    if category in {"html_instead_of_pdf", "js_redirect_unresolved", "interstitial_or_paywall"}:
        return "medium: browser/Zyte comparison can distinguish route bugs from provider limits"
    if category in {"corrupt_or_truncated_pdf", "encrypted_or_unreadable_pdf"}:
        return "medium-low: needs byte-level validation before treating as retrieval failure"
    if category in {"empty_response", "js_required", "bot_block_403"}:
        return "medium: clustered full-baseline residuals need browser comparison"
    return "low: needs row-level inspection"


def sample_row(row: ResidualRow) -> dict[str, str]:
    return {
        "doi": row.doi,
        "publisher": row.publisher,
        "host": residual_host(row),
        "candidate_url": redact_url(getattr(row, "candidate_url", "") or ""),
        "candidate_source": getattr(row, "candidate_source", "") or "",
        "resolved_url": redact_url(row.resolved_url),
        "title": getattr(row, "title", ""),
        "evidence_snippet": redact_text(row.evidence_snippet[:240]),
        "uuid": row.uuid,
    }


def redact_url(url: str) -> str:
    if not url:
        return ""
    parts = urlsplit(url)
    query_pairs = []
    redacted = False
    for key, value in parse_qsl(parts.query, keep_blank_values=True):
        if key in SENSITIVE_QUERY_KEYS or any(key.startswith(prefix) for prefix in SENSITIVE_QUERY_PREFIXES):
            redacted = True
            continue
        query_pairs.append((key, value))
    query = urlencode(query_pairs, doseq=True)
    if redacted and not query:
        query = "redacted=1"
    elif redacted:
        query = f"{query}&redacted=1"
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, parts.fragment))


def redact_text(text: str) -> str:
    text = re.sub(r"(bm-verify=)[A-Za-z0-9_-]+", r"\1REDACTED", text)
    text = re.sub(r"(X-Amz-[A-Za-z-]+=)[A-Za-z0-9%._~+/=-]+", r"\1REDACTED", text)
    return text


def browserbase_candidates(clusters: Iterable[ResidualCluster], *, limit: int = 100) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for cluster in clusters:
        if cluster.category not in BROWSERBASE_CATEGORIES:
            continue
        for row in cluster.sample_rows:
            candidates.append(
                {
                    "doi": row["doi"],
                    "category": cluster.category,
                    "publisher": cluster.publisher,
                    "host": cluster.host,
                    "recommended_agent": "Lens",
                    "resolved_url": row["resolved_url"],
                }
            )
            if len(candidates) >= limit:
                return candidates
    return candidates


def zyte_support_candidates(clusters: Iterable[ResidualCluster], *, limit: int = 100) -> list[dict[str, str]]:
    candidates: list[dict[str, str]] = []
    for cluster in clusters:
        if cluster.category not in ZYTE_SUPPORT_CATEGORIES:
            continue
        for row in cluster.sample_rows:
            candidates.append(
                {
                    "doi": row["doi"],
                    "category": cluster.category,
                    "publisher": cluster.publisher,
                    "host": cluster.host,
                    "recommended_agent": "Envoy",
                    "resolved_url": row["resolved_url"],
                }
            )
            if len(candidates) >= limit:
                return candidates
    return candidates


def write_cluster_artifacts(
    rows_path: Path,
    out_dir: Path,
    *,
    run_id: str = "",
    sample_size: int = 5,
    top_n: int = 50,
) -> dict[str, Path]:
    rows = read_residual_rows_ndjson(rows_path)
    clusters = cluster_rows(rows, sample_size=sample_size)
    out_dir.mkdir(parents=True, exist_ok=True)

    cluster_path = out_dir / "residual-clusters.json"
    cluster_csv_path = out_dir / "residual-clusters.csv"
    browserbase_path = out_dir / "browserbase-candidates.csv"
    zyte_path = out_dir / "zyte-support-candidates.csv"

    payload = {
        "run_id": run_id,
        "rows_path": str(rows_path),
        "non_good_rows": sum(cluster.count for cluster in clusters),
        "cluster_count": len(clusters),
        "sample_size": sample_size,
        "top_clusters": [cluster.to_dict() for cluster in clusters[:top_n]],
    }
    cluster_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    with cluster_csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "rank",
                "category",
                "publisher",
                "host",
                "count",
                "estimated_recoverable_rows",
                "support_candidates",
                "recommended_agent",
                "recommended_action",
                "evidence_strength",
            ]
        )
        for rank, cluster in enumerate(clusters[:top_n], start=1):
            writer.writerow(
                [
                    rank,
                    cluster.category,
                    cluster.publisher,
                    cluster.host,
                    cluster.count,
                    f"{cluster.estimated_recoverable_rows:.2f}",
                    cluster.support_candidates,
                    cluster.recommended_agent,
                    cluster.recommended_action,
                    cluster.evidence_strength,
                ]
            )

    _write_candidate_csv(browserbase_path, browserbase_candidates(clusters))
    _write_candidate_csv(zyte_path, zyte_support_candidates(clusters))

    return {
        "clusters_json": cluster_path,
        "clusters_csv": cluster_csv_path,
        "browserbase_candidates": browserbase_path,
        "zyte_support_candidates": zyte_path,
    }


def _write_candidate_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fieldnames = ["doi", "category", "publisher", "host", "recommended_agent", "resolved_url"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_residual_rows_ndjson(path: Path) -> list[ResidualRow]:
    rows: list[ResidualRow] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            data = json.loads(line)
            if "candidate_url" in data or "pdf_record_count" in data or "pdf_magic" in data:
                rows.append(pdf_row_from_dict(data))
            else:
                rows.append(row_from_dict(data))
    return rows


__all__ = [
    "ResidualCluster",
    "browserbase_candidates",
    "cluster_rows",
    "recommended_action",
    "recommended_agent",
    "redact_text",
    "redact_url",
    "residual_host",
    "read_residual_rows_ndjson",
    "write_cluster_artifacts",
    "zyte_support_candidates",
]
