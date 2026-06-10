"""Taxicab V1 retrieval-quality classifier and artifact helpers.

This module is intentionally isolated from ``app.py`` and from ``Harvester``.
It must be importable without R2, DynamoDB, Flask, or boto3 credentials.
"""

from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


CATEGORY_GOOD_HTML = "good_html"
CATEGORY_MISSING_HARVEST = "missing_harvest"
CATEGORY_DOWNLOAD_404 = "download_404"
CATEGORY_BOT_BLOCK_403 = "bot_block_403"
CATEGORY_TIMEOUT = "timeout"
CATEGORY_EMPTY_RESPONSE = "empty_response"
CATEGORY_JS_REQUIRED = "js_required"
CATEGORY_ROUTER_ONLY = "router_only"
CATEGORY_PDF_INSTEAD_OF_HTML = "pdf_instead_of_html"
CATEGORY_INVALID_CONTENT = "invalid_content"
CATEGORY_TAXICAB_ERROR = "taxicab_error"

CATEGORIES = (
    CATEGORY_GOOD_HTML,
    CATEGORY_MISSING_HARVEST,
    CATEGORY_DOWNLOAD_404,
    CATEGORY_BOT_BLOCK_403,
    CATEGORY_TIMEOUT,
    CATEGORY_EMPTY_RESPONSE,
    CATEGORY_JS_REQUIRED,
    CATEGORY_ROUTER_ONLY,
    CATEGORY_PDF_INSTEAD_OF_HTML,
    CATEGORY_INVALID_CONTENT,
    CATEGORY_TAXICAB_ERROR,
)

SUPPORT_CANDIDATE_CATEGORIES = {
    CATEGORY_BOT_BLOCK_403,
    CATEGORY_JS_REQUIRED,
    CATEGORY_ROUTER_ONLY,
    CATEGORY_EMPTY_RESPONSE,
    CATEGORY_MISSING_HARVEST,
    CATEGORY_TIMEOUT,
    CATEGORY_DOWNLOAD_404,
}

BOT_BLOCK_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"are you a robot",
        r"please verify",
        r"unusual traffic",
        r"recaptcha",
        r"\bg-recaptcha\b",
        r"\bhcaptcha\b",
        r"captcha",
        r"access denied",
        r"request cannot be processed at this time",
        r"we apologize for the inconvenience",
        r"shieldsquare captcha",
        r"errors\.edgesuite\.net",
        r"akamai",
        r"validate\.perfdrive\.com",
        r"distil_r_captcha",
        r"<title[^>]*>\s*just a moment",
        r"<title[^>]*>\s*checking your browser",
        r"cf-challenge",
        r"challenges\.cloudflare\.com",
        r"<title[^>]*>\s*apa psycnet",
        r"project muse -- verification required",
        r"<div[^>]+class=[\"'][^\"']*frc-captcha",
    )
)

ROUTER_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"<title[^>]*>\s*doi\.org",
        r"<title[^>]*>\s*the doi system",
        r"choose from multiple link options via crossref",
        r"chooser\.crossref\.org",
        r"<title[^>]*>\s*301 moved",
        r"<title[^>]*>\s*302 found",
        r"<meta\s+http-equiv=[\"']?refresh[\"']?\s+content=[\"']?\d",
    )
)

JS_REQUIRED_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"enable javascript",
        r"javascript is disabled",
        r"requires javascript",
        r"please enable js",
        r"<app-root[^>]*>\s*</app-root>",
        r"<ds-app[^>]*>\s*</ds-app>",
        r"<div[^>]+id=[\"'](?:root|app)[\"'][^>]*>\s*</div>",
    )
)

HTML_MARKERS = tuple(
    marker.lower()
    for marker in (
        "<html",
        "<!doctype html",
        "<body",
        "<head",
        "<article",
        "citation_title",
        "citation_author",
        "application/ld+json",
        "og:title",
    )
)


@dataclass(frozen=True)
class ContentEvidence:
    doi: str = ""
    publisher: str = "unknown"
    host: str = ""
    input_url: str = ""
    resolved_url: str = ""
    status_code: int | None = None
    content_type: str = ""
    body: bytes | str = b""
    uuid: str = ""
    html_record_count: int = 0
    created_date: str = ""
    duration_ms: int | None = None
    mode: str = "read_only"
    error: str = ""
    browserbase_available: bool = False
    browserbase_final_url: str = ""
    browserbase_evidence_path: str = ""
    browserbase_verdict: str = ""


@dataclass(frozen=True)
class EvalRow:
    run_id: str
    doi: str
    category: str
    publisher: str
    host: str
    input_url: str
    resolved_url: str
    status_code: int | None
    content_type: str
    size_bytes: int
    title: str
    evidence_snippet: str
    support_candidate: bool
    uuid: str
    html_record_count: int
    created_date: str
    duration_ms: int | None
    mode: str
    error: str
    browserbase_available: bool = False
    browserbase_final_url: str = ""
    browserbase_evidence_path: str = ""
    browserbase_verdict: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def default_run_id(prefix: str = "taxicab-eval") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}"


def ensure_bytes(content: bytes | str | None) -> bytes:
    if content is None:
        return b""
    if isinstance(content, bytes):
        return content
    return str(content).encode("utf-8", errors="replace")


def decode_head(content: bytes | str | None, max_bytes: int = 16 * 1024) -> str:
    return ensure_bytes(content)[:max_bytes].decode("utf-8", errors="replace")


def normalize_content_type(content_type: str | None) -> str:
    return (content_type or "").split(";", 1)[0].strip().lower()


def host_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    return host[4:] if host.startswith("www.") else host


def extract_title(text: str) -> str:
    match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
    if not match:
        return ""
    return re.sub(r"\s+", " ", html.unescape(match.group(1))).strip()[:240]


def visible_text(text: str) -> str:
    cleaned = re.sub(r"(?is)<script.*?</script>", " ", text)
    cleaned = re.sub(r"(?is)<style.*?</style>", " ", cleaned)
    cleaned = re.sub(r"(?is)<noscript.*?</noscript>", " ", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def first_matching_pattern(text: str, patterns: Iterable[re.Pattern]) -> str:
    for pattern in patterns:
        if pattern.search(text):
            return pattern.pattern
    return ""


def html_like(text: str, content_type: str) -> bool:
    lower = text.lower()
    if "html" in content_type:
        return True
    return any(marker in lower for marker in HTML_MARKERS)


def evidence_snippet(text: str, max_chars: int = 320) -> str:
    visible = visible_text(text) or re.sub(r"\s+", " ", text).strip()
    return visible[:max_chars]


def classify_content(evidence: ContentEvidence, *, run_id: str = "") -> EvalRow:
    body = ensure_bytes(evidence.body)
    size = len(body)
    text = decode_head(body)
    lower_content_type = normalize_content_type(evidence.content_type)
    title = extract_title(text)
    visible = visible_text(text)
    host = evidence.host or host_from_url(evidence.resolved_url) or host_from_url(evidence.input_url)
    category = CATEGORY_GOOD_HTML
    error = evidence.error

    if lower_content_type == "application/pdf" or body.startswith(b"%PDF-"):
        category = CATEGORY_PDF_INSTEAD_OF_HTML
    elif not body or not text.strip():
        category = CATEGORY_EMPTY_RESPONSE
    elif lower_content_type and "html" not in lower_content_type and not html_like(text, lower_content_type):
        category = CATEGORY_INVALID_CONTENT
    else:
        bot_pattern = first_matching_pattern(text, BOT_BLOCK_PATTERNS)
        router_pattern = first_matching_pattern(text, ROUTER_PATTERNS)
        js_pattern = first_matching_pattern(text, JS_REQUIRED_PATTERNS)
        script_heavy_shell = (
            size < 4096
            and len(visible) < 200
            and "<script" in text.lower()
            and not any(marker in text.lower() for marker in ("citation_title", "citation_author", "<article"))
        )
        if bot_pattern:
            category = CATEGORY_BOT_BLOCK_403
            error = error or f"matched bot pattern: {bot_pattern}"
        elif router_pattern:
            category = CATEGORY_ROUTER_ONLY
            error = error or f"matched router pattern: {router_pattern}"
        elif js_pattern or script_heavy_shell:
            category = CATEGORY_JS_REQUIRED
            error = error or (f"matched js pattern: {js_pattern}" if js_pattern else "script-heavy shell")
        elif len(visible) < 200 and size < 1024:
            category = CATEGORY_EMPTY_RESPONSE
        elif not html_like(text, lower_content_type):
            category = CATEGORY_INVALID_CONTENT

    return EvalRow(
        run_id=run_id,
        doi=evidence.doi,
        category=category,
        publisher=evidence.publisher or "unknown",
        host=host,
        input_url=evidence.input_url,
        resolved_url=evidence.resolved_url,
        status_code=evidence.status_code,
        content_type=lower_content_type or evidence.content_type,
        size_bytes=size,
        title=title,
        evidence_snippet=evidence_snippet(text),
        support_candidate=category in SUPPORT_CANDIDATE_CATEGORIES,
        uuid=evidence.uuid,
        html_record_count=evidence.html_record_count,
        created_date=evidence.created_date,
        duration_ms=evidence.duration_ms,
        mode=evidence.mode,
        error=error,
        browserbase_available=evidence.browserbase_available,
        browserbase_final_url=evidence.browserbase_final_url,
        browserbase_evidence_path=evidence.browserbase_evidence_path,
        browserbase_verdict=evidence.browserbase_verdict,
    )


def make_transport_row(
    *,
    run_id: str,
    doi: str,
    category: str,
    publisher: str = "unknown",
    host: str = "",
    input_url: str = "",
    resolved_url: str = "",
    status_code: int | None = None,
    content_type: str = "",
    uuid: str = "",
    html_record_count: int = 0,
    created_date: str = "",
    duration_ms: int | None = None,
    mode: str = "read_only",
    error: str = "",
) -> EvalRow:
    return EvalRow(
        run_id=run_id,
        doi=doi,
        category=category,
        publisher=publisher or "unknown",
        host=host,
        input_url=input_url,
        resolved_url=resolved_url,
        status_code=status_code,
        content_type=content_type,
        size_bytes=0,
        title="",
        evidence_snippet=error[:320],
        support_candidate=category in SUPPORT_CANDIDATE_CATEGORIES,
        uuid=uuid,
        html_record_count=html_record_count,
        created_date=created_date,
        duration_ms=duration_ms,
        mode=mode,
        error=error,
    )


def parse_created_date(value: str | None) -> datetime:
    if not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def select_html_record(lookup_json: dict[str, Any]) -> tuple[dict[str, Any] | None, int]:
    html_records = lookup_json.get("html") if isinstance(lookup_json, dict) else None
    if not isinstance(html_records, list):
        return None, 0
    records = [record for record in html_records if isinstance(record, dict)]
    if not records:
        return None, 0
    chosen = max(records, key=lambda r: (parse_created_date(r.get("created_date")), str(r.get("id") or "")))
    return chosen, len(records)


def classify_lookup_payload(
    *,
    run_id: str,
    doi: str,
    lookup_json: Any,
    publisher: str = "unknown",
    input_url: str = "",
    duration_ms: int | None = None,
    mode: str = "read_only",
) -> tuple[EvalRow | None, dict[str, Any] | None]:
    if not isinstance(lookup_json, dict):
        return (
            make_transport_row(
                run_id=run_id,
                doi=doi,
                category=CATEGORY_TAXICAB_ERROR,
                publisher=publisher,
                input_url=input_url,
                duration_ms=duration_ms,
                mode=mode,
                error="lookup response is not a JSON object",
            ),
            None,
        )
    html_record, html_count = select_html_record(lookup_json)
    pdf_records = lookup_json.get("pdf") if isinstance(lookup_json.get("pdf"), list) else []
    grobid_records = lookup_json.get("grobid") if isinstance(lookup_json.get("grobid"), list) else []
    if html_record is None:
        category = CATEGORY_PDF_INSTEAD_OF_HTML if pdf_records else CATEGORY_MISSING_HARVEST
        return (
            make_transport_row(
                run_id=run_id,
                doi=doi,
                category=category,
                publisher=publisher,
                input_url=input_url,
                html_record_count=0,
                duration_ms=duration_ms,
                mode=mode,
                error="no html records" if not pdf_records else "pdf records present but html absent",
            ),
            None,
        )
    if not html_record.get("id"):
        return (
            make_transport_row(
                run_id=run_id,
                doi=doi,
                category=CATEGORY_TAXICAB_ERROR,
                publisher=publisher,
                input_url=input_url,
                html_record_count=html_count,
                created_date=str(html_record.get("created_date") or ""),
                duration_ms=duration_ms,
                mode=mode,
                error="html record missing id",
            ),
            None,
        )
    if not grobid_records:
        # Grobid absence is not a retrieval failure, but touching the value here
        # keeps this function explicit about the API shape it expects.
        pass
    return None, html_record | {"_html_record_count": html_count}


def classify_uuid_download_error(
    *,
    run_id: str,
    doi: str,
    status_code: int | None,
    publisher: str = "unknown",
    input_url: str = "",
    resolved_url: str = "",
    uuid: str = "",
    html_record_count: int = 0,
    created_date: str = "",
    duration_ms: int | None = None,
    mode: str = "read_only",
    error: str = "",
) -> EvalRow:
    category = CATEGORY_DOWNLOAD_404 if status_code == 404 else CATEGORY_TAXICAB_ERROR
    return make_transport_row(
        run_id=run_id,
        doi=doi,
        category=category,
        publisher=publisher,
        host=host_from_url(resolved_url),
        input_url=input_url,
        resolved_url=resolved_url,
        status_code=status_code,
        uuid=uuid,
        html_record_count=html_record_count,
        created_date=created_date,
        duration_ms=duration_ms,
        mode=mode,
        error=error or f"uuid download failed with status {status_code}",
    )


def classify_reharvest_post(
    *,
    run_id: str,
    doi: str,
    status_code: int | None,
    payload: Any = None,
    publisher: str = "unknown",
    input_url: str = "",
    resolved_url: str = "",
    duration_ms: int | None = None,
    error: str = "",
) -> EvalRow | None:
    if status_code is None:
        return make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_TIMEOUT,
            publisher=publisher,
            input_url=input_url,
            resolved_url=resolved_url,
            duration_ms=duration_ms,
            mode="reharvest",
            error=error or "reharvest timed out",
        )
    if isinstance(payload, dict) and payload.get("is_soft_block"):
        return make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_BOT_BLOCK_403,
            publisher=publisher,
            input_url=input_url,
            resolved_url=str(payload.get("resolved_url") or resolved_url),
            status_code=status_code,
            content_type=str(payload.get("content_type") or ""),
            duration_ms=duration_ms,
            mode="reharvest",
            error="reharvest returned is_soft_block=true",
        )
    if status_code in (403, 429):
        return make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_BOT_BLOCK_403,
            publisher=publisher,
            input_url=input_url,
            resolved_url=resolved_url,
            status_code=status_code,
            duration_ms=duration_ms,
            mode="reharvest",
            error=error or f"reharvest returned status {status_code}",
        )
    if status_code == 400:
        return make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_INVALID_CONTENT,
            publisher=publisher,
            input_url=input_url,
            resolved_url=resolved_url,
            status_code=status_code,
            duration_ms=duration_ms,
            mode="reharvest",
            error=error or "reharvest returned invalid content",
        )
    if status_code >= 500:
        return make_transport_row(
            run_id=run_id,
            doi=doi,
            category=CATEGORY_TAXICAB_ERROR,
            publisher=publisher,
            input_url=input_url,
            resolved_url=resolved_url,
            status_code=status_code,
            duration_ms=duration_ms,
            mode="reharvest",
            error=error or f"reharvest returned status {status_code}",
        )
    return None


def assess_browserbase_html(html_text: str | None, final_url: str = "") -> dict[str, Any]:
    text = html_text or ""
    evidence = ContentEvidence(
        resolved_url=final_url,
        body=text,
        content_type="text/html",
        mode="browserbase",
    )
    row = classify_content(evidence, run_id="browserbase-assess")
    available = row.category == CATEGORY_GOOD_HTML
    return {
        "available": available,
        "final_url": final_url,
        "verdict": "good_html" if available else row.category,
        "size_bytes": len(text.encode("utf-8", errors="replace")),
        "title": row.title,
        "evidence_snippet": row.evidence_snippet,
    }


def row_from_dict(data: dict[str, Any]) -> EvalRow:
    allowed = {field: data.get(field) for field in EvalRow.__dataclass_fields__}
    return EvalRow(**allowed)


def read_rows_ndjson(path: Path) -> list[EvalRow]:
    rows: list[EvalRow] = []
    if not path.exists():
        return rows
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(row_from_dict(json.loads(line)))
    return rows


def latest_row_by_doi(rows: Iterable[EvalRow]) -> dict[str, EvalRow]:
    by_doi: dict[str, EvalRow] = {}
    for row in rows:
        by_doi[row.doi] = row
    return by_doi


def summarize_rows(
    rows: Iterable[EvalRow],
    *,
    run_id: str,
    base_url: str = "",
    mode: str = "read_only",
    corpus_path: str = "",
    corpus_sha1: str = "",
    git_sha: str = "",
) -> dict[str, Any]:
    row_list = list(rows)
    total = len(row_list)
    category_counts = Counter(row.category for row in row_list)
    counted = sum(category_counts.values())
    if counted != total:
        raise ValueError(f"category count invariant failed: {counted} != {total}")
    publisher_matrix: dict[str, Counter] = defaultdict(Counter)
    host_matrix: dict[str, Counter] = defaultdict(Counter)
    for row in row_list:
        publisher_matrix[row.publisher or "unknown"][row.category] += 1
        host_matrix[row.host or "unknown"][row.category] += 1
    good = category_counts.get(CATEGORY_GOOD_HTML, 0)
    non_good = total - good
    return {
        "run_id": run_id,
        "timestamp_utc": utc_now(),
        "base_url": base_url,
        "mode": mode,
        "corpus_path": corpus_path,
        "corpus_sha1": corpus_sha1,
        "git_sha": git_sha,
        "total": total,
        "good_html": good,
        "non_good": non_good,
        "good_html_rate": round(good / total, 6) if total else 0,
        "target_good_html_rate": 0.95,
        "gap_to_95_rows": max(0, int((0.95 * total + 0.999999) // 1) - good) if total else 0,
        "category_counts": {category: category_counts.get(category, 0) for category in CATEGORIES},
        "publisher_category_matrix": {
            publisher: dict(counts)
            for publisher, counts in sorted(
                publisher_matrix.items(),
                key=lambda item: (-sum(item[1].values()), item[0]),
            )
        },
        "host_category_matrix": {
            host: dict(counts)
            for host, counts in sorted(host_matrix.items(), key=lambda item: (-sum(item[1].values()), item[0]))[:100]
        },
    }


def build_hardness(rows: Iterable[EvalRow], *, max_examples_per_category: int = 25) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {category: [] for category in CATEGORIES if category != CATEGORY_GOOD_HTML}
    for row in rows:
        if row.category == CATEGORY_GOOD_HTML:
            continue
        examples = grouped.setdefault(row.category, [])
        if len(examples) >= max_examples_per_category:
            continue
        examples.append(
            {
                "doi": row.doi,
                "publisher": row.publisher,
                "host": row.host,
                "resolved_url": row.resolved_url,
                "uuid": row.uuid,
                "title": row.title,
                "evidence_snippet": row.evidence_snippet,
                "support_candidate": row.support_candidate,
                "error": row.error,
            }
        )
    return {
        "generated_at_utc": utc_now(),
        "categories": grouped,
    }


def render_html_report(summary: dict[str, Any], hardness: dict[str, Any]) -> str:
    total = summary.get("total", 0)
    good = summary.get("good_html", 0)
    rate = summary.get("good_html_rate", 0) * 100
    gap = summary.get("gap_to_95_rows", 0)
    categories = summary.get("category_counts", {})
    publisher_matrix = summary.get("publisher_category_matrix", {})
    host_matrix = summary.get("host_category_matrix", {})

    def table_rows(mapping: dict[str, int]) -> str:
        return "\n".join(
            f"<tr><td>{html.escape(k)}</td><td>{v}</td></tr>"
            for k, v in sorted(mapping.items(), key=lambda item: (-item[1], item[0]))
        )

    publisher_rows = []
    for publisher, counts in list(publisher_matrix.items())[:25]:
        non_good = sum(v for k, v in counts.items() if k != CATEGORY_GOOD_HTML)
        publisher_rows.append(
            "<tr>"
            f"<td>{html.escape(publisher)}</td>"
            f"<td>{sum(counts.values())}</td>"
            f"<td>{counts.get(CATEGORY_GOOD_HTML, 0)}</td>"
            f"<td>{non_good}</td>"
            f"<td>{html.escape(json.dumps(counts, sort_keys=True))}</td>"
            "</tr>"
        )
    host_rows = []
    for host, counts in list(host_matrix.items())[:25]:
        non_good = sum(v for k, v in counts.items() if k != CATEGORY_GOOD_HTML)
        host_rows.append(
            "<tr>"
            f"<td>{html.escape(host)}</td>"
            f"<td>{sum(counts.values())}</td>"
            f"<td>{counts.get(CATEGORY_GOOD_HTML, 0)}</td>"
            f"<td>{non_good}</td>"
            f"<td>{html.escape(json.dumps(counts, sort_keys=True))}</td>"
            "</tr>"
        )
    example_rows = []
    for category, examples in hardness.get("categories", {}).items():
        for example in examples[:5]:
            example_rows.append(
                "<tr>"
                f"<td>{html.escape(category)}</td>"
                f"<td>{html.escape(example.get('publisher') or '')}</td>"
                f"<td>{html.escape(example.get('host') or '')}</td>"
                f"<td>{html.escape(example.get('doi') or '')}</td>"
                f"<td>{html.escape(example.get('evidence_snippet') or '')}</td>"
                "</tr>"
            )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Taxicab Retrieval Quality Report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #1d1d1f; }}
    h1, h2 {{ margin-bottom: 8px; }}
    .metric {{ display: inline-block; margin: 8px 24px 16px 0; }}
    .metric strong {{ display: block; font-size: 26px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f6f7f8; }}
    .muted {{ color: #666; }}
    code {{ background: #f6f7f8; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Taxicab Retrieval Quality Report</h1>
  <p><strong>BLUF:</strong> Taxicab read-only baseline resolves {good}/{total} DOI landing pages to usable HTML ({rate:.2f}%). The current gap to 95% is {gap} rows.</p>
  <p class="muted">Run <code>{html.escape(str(summary.get("run_id", "")))}</code> · mode <code>{html.escape(str(summary.get("mode", "")))}</code> · base URL <code>{html.escape(str(summary.get("base_url", "")))}</code></p>
  <div class="metric"><span>Total</span><strong>{total}</strong></div>
  <div class="metric"><span>good_html</span><strong>{good}</strong></div>
  <div class="metric"><span>non_good</span><strong>{summary.get("non_good", 0)}</strong></div>
  <div class="metric"><span>good_html_rate</span><strong>{rate:.2f}%</strong></div>
  <h2>Category Counts</h2>
  <table><thead><tr><th>Category</th><th>Rows</th></tr></thead><tbody>{table_rows(categories)}</tbody></table>
  <h2>Publisher Clusters</h2>
  <table><thead><tr><th>Publisher</th><th>Total</th><th>Good</th><th>Non-good</th><th>Counts</th></tr></thead><tbody>{''.join(publisher_rows)}</tbody></table>
  <h2>Host Clusters</h2>
  <table><thead><tr><th>Host</th><th>Total</th><th>Good</th><th>Non-good</th><th>Counts</th></tr></thead><tbody>{''.join(host_rows)}</tbody></table>
  <h2>Hardness Examples</h2>
  <table><thead><tr><th>Category</th><th>Publisher</th><th>Host</th><th>DOI</th><th>Evidence</th></tr></thead><tbody>{''.join(example_rows)}</tbody></table>
</body>
</html>
"""


def write_artifacts(
    rows: Iterable[EvalRow],
    run_dir: Path,
    *,
    run_id: str,
    base_url: str = "",
    mode: str = "read_only",
    corpus_path: str = "",
    corpus_sha1: str = "",
    git_sha: str = "",
) -> dict[str, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    row_list = list(rows)
    rows_path = run_dir / "rows.ndjson"
    with open(rows_path, "w", encoding="utf-8") as handle:
        for row in row_list:
            handle.write(json.dumps(row.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
    summary = summarize_rows(
        row_list,
        run_id=run_id,
        base_url=base_url,
        mode=mode,
        corpus_path=corpus_path,
        corpus_sha1=corpus_sha1,
        git_sha=git_sha,
    )
    hardness = build_hardness(row_list)
    summary_path = run_dir / "summary.json"
    hardness_path = run_dir / "hardness.json"
    report_path = run_dir / "report.html"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    hardness_path.write_text(json.dumps(hardness, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    report_path.write_text(render_html_report(summary, hardness), encoding="utf-8")
    (run_dir / "browserbase").mkdir(exist_ok=True)
    (run_dir / "zyte-support").mkdir(exist_ok=True)
    return {
        "rows": rows_path,
        "summary": summary_path,
        "hardness": hardness_path,
        "report": report_path,
    }


__all__ = [
    "CATEGORIES",
    "SUPPORT_CANDIDATE_CATEGORIES",
    "ContentEvidence",
    "EvalRow",
    "assess_browserbase_html",
    "build_hardness",
    "classify_content",
    "classify_lookup_payload",
    "classify_reharvest_post",
    "classify_uuid_download_error",
    "default_run_id",
    "host_from_url",
    "latest_row_by_doi",
    "make_transport_row",
    "read_rows_ndjson",
    "render_html_report",
    "select_html_record",
    "summarize_rows",
    "write_artifacts",
]
