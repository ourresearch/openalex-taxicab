"""PDF retrieval-quality classifier and artifact helpers.

This module is intentionally pure: no Flask app import, no boto3/R2 clients,
and no network access. The live runner can build transport around these
classification primitives.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


PDF_CATEGORY_GOOD_PDF = "good_pdf"
PDF_CATEGORY_NO_PDF_EXPECTED = "no_pdf_expected"
PDF_CATEGORY_MISSING_PDF_HARVEST = "missing_pdf_harvest"
PDF_CATEGORY_DOWNLOAD_404 = "download_404"
PDF_CATEGORY_BOT_BLOCK_403 = "bot_block_403"
PDF_CATEGORY_TIMEOUT = "timeout"
PDF_CATEGORY_HTML_INSTEAD_OF_PDF = "html_instead_of_pdf"
PDF_CATEGORY_JS_REDIRECT_UNRESOLVED = "js_redirect_unresolved"
PDF_CATEGORY_INTERSTITIAL_OR_PAYWALL = "interstitial_or_paywall"
PDF_CATEGORY_EMPTY_RESPONSE = "empty_response"
PDF_CATEGORY_CORRUPT_OR_TRUNCATED_PDF = "corrupt_or_truncated_pdf"
PDF_CATEGORY_WRONG_PDF_CONTENT = "wrong_pdf_content"
PDF_CATEGORY_SUPPLEMENT_OR_PREVIEW_PDF = "supplement_or_preview_pdf"
PDF_CATEGORY_ENCRYPTED_OR_UNREADABLE_PDF = "encrypted_or_unreadable_pdf"
PDF_CATEGORY_TAXICAB_ERROR = "taxicab_error"

PDF_CATEGORIES = (
    PDF_CATEGORY_GOOD_PDF,
    PDF_CATEGORY_NO_PDF_EXPECTED,
    PDF_CATEGORY_MISSING_PDF_HARVEST,
    PDF_CATEGORY_DOWNLOAD_404,
    PDF_CATEGORY_BOT_BLOCK_403,
    PDF_CATEGORY_TIMEOUT,
    PDF_CATEGORY_HTML_INSTEAD_OF_PDF,
    PDF_CATEGORY_JS_REDIRECT_UNRESOLVED,
    PDF_CATEGORY_INTERSTITIAL_OR_PAYWALL,
    PDF_CATEGORY_EMPTY_RESPONSE,
    PDF_CATEGORY_CORRUPT_OR_TRUNCATED_PDF,
    PDF_CATEGORY_WRONG_PDF_CONTENT,
    PDF_CATEGORY_SUPPLEMENT_OR_PREVIEW_PDF,
    PDF_CATEGORY_ENCRYPTED_OR_UNREADABLE_PDF,
    PDF_CATEGORY_TAXICAB_ERROR,
)

PDF_SUPPORT_CANDIDATE_CATEGORIES = {
    PDF_CATEGORY_MISSING_PDF_HARVEST,
    PDF_CATEGORY_DOWNLOAD_404,
    PDF_CATEGORY_BOT_BLOCK_403,
    PDF_CATEGORY_TIMEOUT,
    PDF_CATEGORY_HTML_INSTEAD_OF_PDF,
    PDF_CATEGORY_JS_REDIRECT_UNRESOLVED,
    PDF_CATEGORY_INTERSTITIAL_OR_PAYWALL,
    PDF_CATEGORY_EMPTY_RESPONSE,
    PDF_CATEGORY_CORRUPT_OR_TRUNCATED_PDF,
}

BOT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"are you a robot",
        r"captcha",
        r"access denied",
        r"cf-challenge",
        r"challenges\.cloudflare\.com",
        r"errors\.edgesuite\.net",
        r"shieldsquare",
        r"akamai bot manager",
        r"validate\.perfdrive\.com",
    )
)

JS_REDIRECT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"window\.location",
        r"location\.href",
        r"document\.location",
        r"<script[^>]*>\s*(?:window\.)?location",
        r"enable javascript",
        r"javascript is required",
    )
)

INTERSTITIAL_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\bsign in\b",
        r"\blogin\b",
        r"\bsubscribe\b",
        r"\bpurchase access\b",
        r"\bpaywall\b",
        r"\bterms and conditions\b",
        r"\bcontinue to article\b",
        r"\bdownload will begin\b",
    )
)

SUPPLEMENT_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"supplementary (?:appendix|material|materials|data|file)",
        r"\bsupplement\b",
        r"\bpreview\b",
        r"\bcover page\b",
        r"\btable of contents\b",
        r"\bfront matter\b",
    )
)

HTML_MARKERS = ("<html", "<!doctype html", "<body", "<head", "<script")


@dataclass(frozen=True)
class PdfEvidence:
    doi: str = ""
    work_id: str = ""
    title: str = ""
    publisher: str = "unknown"
    host: str = ""
    input_url: str = ""
    candidate_url: str = ""
    candidate_source: str = ""
    resolved_url: str = ""
    status_code: int | None = None
    content_type: str = ""
    body: bytes | str = b""
    pdf_expected: bool = True
    uuid: str = ""
    pdf_record_count: int = 0
    duration_ms: int | None = None
    mode: str = "fixture"
    error: str = ""
    browserbase_available: bool = False
    browserbase_final_url: str = ""
    browserbase_evidence_path: str = ""
    browserbase_verdict: str = ""


@dataclass(frozen=True)
class PdfEvalRow:
    run_id: str
    work_id: str
    doi: str
    category: str
    publisher: str
    host: str
    input_url: str
    candidate_url: str
    candidate_source: str
    resolved_url: str
    status_code: int | None
    content_type: str
    size_bytes: int
    sha256: str
    pdf_magic: bool
    page_count: int
    text_chars: int
    title_overlap: float
    doi_match: bool
    validation_errors: list[str]
    evidence_snippet: str
    support_candidate: bool
    uuid: str
    pdf_record_count: int
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


def default_pdf_run_id(prefix: str = "taxicab-pdf") -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{prefix}-{stamp}"


def ensure_bytes(content: bytes | str | None) -> bytes:
    if content is None:
        return b""
    if isinstance(content, bytes):
        return content
    return str(content).encode("utf-8", errors="replace")


def decode_latin1(content: bytes, max_bytes: int = 256 * 1024) -> str:
    return content[:max_bytes].decode("latin-1", errors="replace")


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


def normalize_for_match(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def meaningful_title_tokens(title: str) -> set[str]:
    stop = {
        "the",
        "and",
        "for",
        "with",
        "from",
        "this",
        "that",
        "into",
        "using",
        "study",
        "article",
    }
    return {token for token in re.findall(r"[a-z0-9]{4,}", title.lower()) if token not in stop}


def title_overlap(title: str, text: str) -> float:
    tokens = meaningful_title_tokens(title)
    if not tokens:
        return 0.0
    normalized_text = text.lower()
    matched = sum(1 for token in tokens if token in normalized_text)
    return round(matched / len(tokens), 4)


def count_pdf_pages(text: str) -> int:
    # Matches page objects, not the parent /Pages node.
    return len(re.findall(r"/Type\s*/Page\b(?!s)", text))


def html_like(text: str, content_type: str) -> bool:
    lower = text.lower()
    return "html" in content_type or any(marker in lower for marker in HTML_MARKERS)


def first_pattern(text: str, patterns: Iterable[re.Pattern]) -> str:
    for pattern in patterns:
        if pattern.search(text):
            return pattern.pattern
    return ""


def visible_html_text(text: str) -> str:
    cleaned = re.sub(r"(?is)<script.*?</script>", " ", text)
    cleaned = re.sub(r"(?is)<style.*?</style>", " ", cleaned)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def pdf_text_smoke(decoded_pdf: str) -> str:
    # This is not a full PDF text extractor. It intentionally gives the
    # validator cheap signal for DOI/title/supplement fixtures and metadata.
    strings = re.findall(r"\(([^()]{0,400})\)", decoded_pdf)
    joined = " ".join(strings) if strings else decoded_pdf
    joined = joined.replace("\\(", "(").replace("\\)", ")")
    return re.sub(r"\s+", " ", joined).strip()


def has_pdf_eof_marker(body: bytes) -> bool:
    # Text scanning intentionally decodes only the head of large PDFs. EOF
    # validation must use the complete byte payload or valid large PDFs are
    # misclassified as truncated.
    return b"%%EOF" in body


def evidence_snippet(text: str, max_chars: int = 320) -> str:
    return re.sub(r"\s+", " ", text).strip()[:max_chars]


def classify_pdf_content(evidence: PdfEvidence, *, run_id: str = "") -> PdfEvalRow:
    body = ensure_bytes(evidence.body)
    size = len(body)
    sha256 = hashlib.sha256(body).hexdigest() if body else ""
    content_type = normalize_content_type(evidence.content_type)
    host = evidence.host or host_from_url(evidence.resolved_url) or host_from_url(evidence.candidate_url)
    pdf_magic = body.startswith(b"%PDF-")
    decoded = decode_latin1(body)
    text_smoke = ""
    page_count = 0
    overlap = 0.0
    doi_match = False
    validation_errors: list[str] = []
    error = evidence.error
    category = PDF_CATEGORY_GOOD_PDF

    if not evidence.pdf_expected:
        category = PDF_CATEGORY_NO_PDF_EXPECTED
        validation_errors.append("pdf not expected")
    elif evidence.status_code in (403, 429):
        category = PDF_CATEGORY_BOT_BLOCK_403
        validation_errors.append(f"blocked status {evidence.status_code}")
    elif evidence.status_code == 404:
        category = PDF_CATEGORY_DOWNLOAD_404
        validation_errors.append("download returned 404")
    elif not body or not decoded.strip():
        category = PDF_CATEGORY_EMPTY_RESPONSE
        validation_errors.append("empty response")
    elif html_like(decoded, content_type) and not pdf_magic:
        visible = visible_html_text(decoded)
        bot_pattern = first_pattern(decoded, BOT_PATTERNS)
        js_pattern = first_pattern(decoded, JS_REDIRECT_PATTERNS)
        interstitial_pattern = first_pattern(decoded, INTERSTITIAL_PATTERNS)
        if bot_pattern:
            category = PDF_CATEGORY_BOT_BLOCK_403
            validation_errors.append(f"matched bot pattern: {bot_pattern}")
        elif js_pattern:
            category = PDF_CATEGORY_JS_REDIRECT_UNRESOLVED
            validation_errors.append(f"matched js redirect pattern: {js_pattern}")
        elif interstitial_pattern:
            category = PDF_CATEGORY_INTERSTITIAL_OR_PAYWALL
            validation_errors.append(f"matched interstitial pattern: {interstitial_pattern}")
        else:
            category = PDF_CATEGORY_HTML_INSTEAD_OF_PDF
            validation_errors.append("html returned instead of pdf")
        text_smoke = visible
    elif not pdf_magic:
        category = PDF_CATEGORY_CORRUPT_OR_TRUNCATED_PDF
        validation_errors.append("missing %PDF- magic bytes")
    else:
        page_count = count_pdf_pages(decoded)
        text_smoke = pdf_text_smoke(decoded)
        overlap = title_overlap(evidence.title, text_smoke)
        normalized_doi = normalize_for_match(evidence.doi)
        doi_match = bool(normalized_doi and normalized_doi in normalize_for_match(text_smoke))
        if "/Encrypt" in decoded:
            category = PDF_CATEGORY_ENCRYPTED_OR_UNREADABLE_PDF
            validation_errors.append("pdf appears encrypted")
        elif not has_pdf_eof_marker(body):
            category = PDF_CATEGORY_CORRUPT_OR_TRUNCATED_PDF
            validation_errors.append("missing eof marker")
        elif page_count <= 0:
            category = PDF_CATEGORY_CORRUPT_OR_TRUNCATED_PDF
            validation_errors.append("no page objects found")
        else:
            supplement_pattern = first_pattern(text_smoke, SUPPLEMENT_PATTERNS)
            if supplement_pattern:
                category = PDF_CATEGORY_SUPPLEMENT_OR_PREVIEW_PDF
                validation_errors.append(f"matched supplement/preview pattern: {supplement_pattern}")
            elif (evidence.doi or evidence.title) and text_smoke:
                if evidence.doi and not doi_match and evidence.title and overlap < 0.2:
                    category = PDF_CATEGORY_WRONG_PDF_CONTENT
                    validation_errors.append("doi and title evidence do not match expected work")

    if validation_errors and not error:
        error = "; ".join(validation_errors)

    return PdfEvalRow(
        run_id=run_id,
        work_id=evidence.work_id,
        doi=evidence.doi,
        category=category,
        publisher=evidence.publisher or "unknown",
        host=host,
        input_url=evidence.input_url,
        candidate_url=evidence.candidate_url,
        candidate_source=evidence.candidate_source,
        resolved_url=evidence.resolved_url,
        status_code=evidence.status_code,
        content_type=content_type or evidence.content_type,
        size_bytes=size,
        sha256=sha256,
        pdf_magic=pdf_magic,
        page_count=page_count,
        text_chars=len(text_smoke),
        title_overlap=overlap,
        doi_match=doi_match,
        validation_errors=validation_errors,
        evidence_snippet=evidence_snippet(text_smoke or decoded),
        support_candidate=category in PDF_SUPPORT_CANDIDATE_CATEGORIES,
        uuid=evidence.uuid,
        pdf_record_count=evidence.pdf_record_count,
        duration_ms=evidence.duration_ms,
        mode=evidence.mode,
        error=error,
        browserbase_available=evidence.browserbase_available,
        browserbase_final_url=evidence.browserbase_final_url,
        browserbase_evidence_path=evidence.browserbase_evidence_path,
        browserbase_verdict=evidence.browserbase_verdict,
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


def select_pdf_record(lookup_json: dict[str, Any]) -> tuple[dict[str, Any] | None, int]:
    pdf_records = lookup_json.get("pdf") if isinstance(lookup_json, dict) else None
    if not isinstance(pdf_records, list):
        return None, 0
    records = [record for record in pdf_records if isinstance(record, dict)]
    if not records:
        return None, 0
    chosen = max(records, key=lambda r: (parse_created_date(r.get("created_date")), str(r.get("id") or "")))
    return chosen, len(records)


def classify_pdf_lookup_payload(
    *,
    run_id: str,
    doi: str,
    lookup_json: Any,
    pdf_expected: bool = True,
    work_id: str = "",
    publisher: str = "unknown",
    input_url: str = "",
    duration_ms: int | None = None,
    mode: str = "read_only",
) -> tuple[PdfEvalRow | None, dict[str, Any] | None]:
    if not pdf_expected:
        return (
            make_pdf_transport_row(
                run_id=run_id,
                doi=doi,
                work_id=work_id,
                category=PDF_CATEGORY_NO_PDF_EXPECTED,
                publisher=publisher,
                input_url=input_url,
                duration_ms=duration_ms,
                mode=mode,
                error="pdf not expected for row",
            ),
            None,
        )
    if not isinstance(lookup_json, dict):
        return (
            make_pdf_transport_row(
                run_id=run_id,
                doi=doi,
                work_id=work_id,
                category=PDF_CATEGORY_TAXICAB_ERROR,
                publisher=publisher,
                input_url=input_url,
                duration_ms=duration_ms,
                mode=mode,
                error="lookup response is not a JSON object",
            ),
            None,
        )
    pdf_record, pdf_count = select_pdf_record(lookup_json)
    if pdf_record is None:
        return (
            make_pdf_transport_row(
                run_id=run_id,
                doi=doi,
                work_id=work_id,
                category=PDF_CATEGORY_MISSING_PDF_HARVEST,
                publisher=publisher,
                input_url=input_url,
                pdf_record_count=0,
                duration_ms=duration_ms,
                mode=mode,
                error="no pdf records",
            ),
            None,
        )
    if not pdf_record.get("id"):
        return (
            make_pdf_transport_row(
                run_id=run_id,
                doi=doi,
                work_id=work_id,
                category=PDF_CATEGORY_TAXICAB_ERROR,
                publisher=publisher,
                input_url=input_url,
                pdf_record_count=pdf_count,
                duration_ms=duration_ms,
                mode=mode,
                error="pdf record missing id",
            ),
            None,
        )
    return None, pdf_record | {"_pdf_record_count": pdf_count}


def classify_pdf_uuid_download_error(
    *,
    run_id: str,
    doi: str,
    status_code: int | None,
    work_id: str = "",
    publisher: str = "unknown",
    input_url: str = "",
    candidate_url: str = "",
    candidate_source: str = "",
    resolved_url: str = "",
    uuid: str = "",
    pdf_record_count: int = 0,
    duration_ms: int | None = None,
    mode: str = "read_only",
    error: str = "",
) -> PdfEvalRow:
    if status_code == 404:
        category = PDF_CATEGORY_DOWNLOAD_404
    elif status_code in (403, 429):
        category = PDF_CATEGORY_BOT_BLOCK_403
    else:
        category = PDF_CATEGORY_TAXICAB_ERROR
    return make_pdf_transport_row(
        run_id=run_id,
        doi=doi,
        work_id=work_id,
        category=category,
        publisher=publisher,
        host=host_from_url(resolved_url or candidate_url),
        input_url=input_url,
        candidate_url=candidate_url,
        candidate_source=candidate_source,
        resolved_url=resolved_url,
        status_code=status_code,
        uuid=uuid,
        pdf_record_count=pdf_record_count,
        duration_ms=duration_ms,
        mode=mode,
        error=error or f"uuid download failed with status {status_code}",
    )


def make_pdf_transport_row(
    *,
    run_id: str,
    doi: str,
    category: str,
    work_id: str = "",
    publisher: str = "unknown",
    host: str = "",
    input_url: str = "",
    candidate_url: str = "",
    candidate_source: str = "",
    resolved_url: str = "",
    status_code: int | None = None,
    content_type: str = "",
    uuid: str = "",
    pdf_record_count: int = 0,
    duration_ms: int | None = None,
    mode: str = "read_only",
    error: str = "",
) -> PdfEvalRow:
    return PdfEvalRow(
        run_id=run_id,
        work_id=work_id,
        doi=doi,
        category=category,
        publisher=publisher or "unknown",
        host=host,
        input_url=input_url,
        candidate_url=candidate_url,
        candidate_source=candidate_source,
        resolved_url=resolved_url,
        status_code=status_code,
        content_type=content_type,
        size_bytes=0,
        sha256="",
        pdf_magic=False,
        page_count=0,
        text_chars=0,
        title_overlap=0.0,
        doi_match=False,
        validation_errors=[error] if error else [],
        evidence_snippet=error[:320],
        support_candidate=category in PDF_SUPPORT_CANDIDATE_CATEGORIES,
        uuid=uuid,
        pdf_record_count=pdf_record_count,
        duration_ms=duration_ms,
        mode=mode,
        error=error,
    )


def pdf_row_from_dict(data: dict[str, Any]) -> PdfEvalRow:
    allowed = {field: data.get(field) for field in PdfEvalRow.__dataclass_fields__}
    return PdfEvalRow(**allowed)


def read_pdf_rows_ndjson(path: Path) -> list[PdfEvalRow]:
    rows: list[PdfEvalRow] = []
    if not path.exists():
        return rows
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(pdf_row_from_dict(json.loads(line)))
    return rows


def latest_pdf_row_by_doi(rows: Iterable[PdfEvalRow]) -> dict[str, PdfEvalRow]:
    by_doi: dict[str, PdfEvalRow] = {}
    for row in rows:
        by_doi[row.doi] = row
    return by_doi


def summarize_pdf_rows(
    rows: Iterable[PdfEvalRow],
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
    pdf_expected_total = total - category_counts.get(PDF_CATEGORY_NO_PDF_EXPECTED, 0)
    good = category_counts.get(PDF_CATEGORY_GOOD_PDF, 0)
    non_good_expected = max(0, pdf_expected_total - good)
    publisher_matrix: dict[str, Counter] = defaultdict(Counter)
    host_matrix: dict[str, Counter] = defaultdict(Counter)
    for row in row_list:
        publisher_matrix[row.publisher or "unknown"][row.category] += 1
        host_matrix[row.host or "unknown"][row.category] += 1
    return {
        "run_id": run_id,
        "timestamp_utc": utc_now(),
        "base_url": base_url,
        "mode": mode,
        "corpus_path": corpus_path,
        "corpus_sha1": corpus_sha1,
        "git_sha": git_sha,
        "total": total,
        "pdf_expected_total": pdf_expected_total,
        "good_pdf": good,
        "non_good_expected": non_good_expected,
        "good_pdf_rate": round(good / pdf_expected_total, 6) if pdf_expected_total else 0,
        "target_good_pdf_rate": 0.95,
        "stretch_good_pdf_rate": 0.98,
        "gap_to_95_rows": max(0, int((0.95 * pdf_expected_total + 0.999999) // 1) - good)
        if pdf_expected_total
        else 0,
        "category_counts": {category: category_counts.get(category, 0) for category in PDF_CATEGORIES},
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


def build_pdf_hardness(rows: Iterable[PdfEvalRow], *, max_examples_per_category: int = 25) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {
        category: [] for category in PDF_CATEGORIES if category != PDF_CATEGORY_GOOD_PDF
    }
    for row in rows:
        if row.category == PDF_CATEGORY_GOOD_PDF:
            continue
        examples = grouped.setdefault(row.category, [])
        if len(examples) >= max_examples_per_category:
            continue
        examples.append(
            {
                "doi": row.doi,
                "work_id": row.work_id,
                "publisher": row.publisher,
                "host": row.host,
                "candidate_source": row.candidate_source,
                "candidate_url": row.candidate_url,
                "resolved_url": row.resolved_url,
                "uuid": row.uuid,
                "page_count": row.page_count,
                "size_bytes": row.size_bytes,
                "validation_errors": row.validation_errors,
                "evidence_snippet": row.evidence_snippet,
                "support_candidate": row.support_candidate,
                "error": row.error,
            }
        )
    return {"generated_at_utc": utc_now(), "categories": grouped}


def render_pdf_html_report(summary: dict[str, Any], hardness: dict[str, Any]) -> str:
    total = summary.get("total", 0)
    expected = summary.get("pdf_expected_total", 0)
    good = summary.get("good_pdf", 0)
    rate = summary.get("good_pdf_rate", 0) * 100
    gap = summary.get("gap_to_95_rows", 0)
    categories = summary.get("category_counts", {})

    category_rows = "\n".join(
        f"<tr><td><code>{html.escape(category)}</code></td><td>{count}</td></tr>"
        for category, count in sorted(categories.items(), key=lambda item: (-item[1], item[0]))
    )
    example_rows = []
    for category, examples in hardness.get("categories", {}).items():
        for example in examples[:5]:
            example_rows.append(
                "<tr>"
                f"<td><code>{html.escape(category)}</code></td>"
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
<title>Taxicab PDF Retrieval Quality Report</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;margin:32px;color:#111827}}
table{{border-collapse:collapse;width:100%;font-size:14px;margin:12px 0 28px}}
th,td{{border-bottom:1px solid #e5e7eb;padding:8px;text-align:left;vertical-align:top}}
th{{background:#f1f5f9}}code{{font-size:12px}}.metric{{display:inline-block;margin:8px 24px 16px 0}}.metric strong{{display:block;font-size:26px}}
</style>
</head>
<body>
<h1>Taxicab PDF Retrieval Quality Report</h1>
<p><strong>BLUF:</strong> Taxicab resolves {good}/{expected} expected full-text PDFs to valid <code>good_pdf</code> ({rate:.2f}%). The gap to 95% is {gap} rows.</p>
<p>Total rows in context: {total}. The denominator for the target is <code>pdf_expected_total</code>, not all rows.</p>
<div class="metric"><span>pdf_expected_total</span><strong>{expected}</strong></div>
<div class="metric"><span>good_pdf</span><strong>{good}</strong></div>
<div class="metric"><span>good_pdf_rate</span><strong>{rate:.2f}%</strong></div>
<div class="metric"><span>gap_to_95_rows</span><strong>{gap}</strong></div>
<h2>Category Counts</h2>
<table><thead><tr><th>Category</th><th>Rows</th></tr></thead><tbody>{category_rows}</tbody></table>
<h2>Hardness Examples</h2>
<table><thead><tr><th>Category</th><th>Publisher</th><th>Host</th><th>DOI</th><th>Evidence</th></tr></thead><tbody>{''.join(example_rows)}</tbody></table>
</body>
</html>
"""


def write_pdf_artifacts(
    rows: Iterable[PdfEvalRow],
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
    summary = summarize_pdf_rows(
        row_list,
        run_id=run_id,
        base_url=base_url,
        mode=mode,
        corpus_path=corpus_path,
        corpus_sha1=corpus_sha1,
        git_sha=git_sha,
    )
    hardness = build_pdf_hardness(row_list)
    summary_path = run_dir / "summary.json"
    hardness_path = run_dir / "hardness.json"
    report_path = run_dir / "report.html"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    hardness_path.write_text(json.dumps(hardness, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    report_path.write_text(render_pdf_html_report(summary, hardness), encoding="utf-8")
    (run_dir / "browserbase").mkdir(exist_ok=True)
    (run_dir / "zyte-support").mkdir(exist_ok=True)
    return {
        "rows": rows_path,
        "summary": summary_path,
        "hardness": hardness_path,
        "report": report_path,
    }


__all__ = [
    "PDF_CATEGORIES",
    "PDF_SUPPORT_CANDIDATE_CATEGORIES",
    "PdfEvidence",
    "PdfEvalRow",
    "build_pdf_hardness",
    "classify_pdf_content",
    "classify_pdf_lookup_payload",
    "classify_pdf_uuid_download_error",
    "default_pdf_run_id",
    "latest_pdf_row_by_doi",
    "make_pdf_transport_row",
    "read_pdf_rows_ndjson",
    "render_pdf_html_report",
    "select_pdf_record",
    "summarize_pdf_rows",
    "write_pdf_artifacts",
]
