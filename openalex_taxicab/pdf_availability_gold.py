"""PDF availability gold-label helpers.

The PDF retrieval eval needs two denominators:

* raw guessed PDF candidates from the corpus/eval harness
* reviewed availability labels for public-retrievable and all-known PDFs

This module is intentionally pure stdlib. It does not browse, call Taxicab, or
mutate source CSVs.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


STATUS_OPEN_FULL_TEXT_PDF = "open_full_text_pdf_available"
STATUS_PAYWALLED_OR_LOGIN = "paywalled_or_login_pdf_available"
STATUS_NO_FULL_TEXT_PDF = "no_full_text_pdf_found"
STATUS_HTML_FULL_TEXT_ONLY = "html_full_text_only"
STATUS_SUPPLEMENT_OR_PREVIEW = "supplement_or_preview_only"
STATUS_BROKEN_PDF_LINK = "broken_pdf_link"
STATUS_BROKEN_OR_BAD_DOI = "broken_or_bad_doi"
STATUS_NON_ARTICLE_OUT_OF_SCOPE = "non_article_or_out_of_scope"
STATUS_UNCLEAR_REVIEW = "unclear_needs_review"

PDF_GOLD_STATUSES = (
    STATUS_OPEN_FULL_TEXT_PDF,
    STATUS_PAYWALLED_OR_LOGIN,
    STATUS_NO_FULL_TEXT_PDF,
    STATUS_HTML_FULL_TEXT_ONLY,
    STATUS_SUPPLEMENT_OR_PREVIEW,
    STATUS_BROKEN_PDF_LINK,
    STATUS_BROKEN_OR_BAD_DOI,
    STATUS_NON_ARTICLE_OUT_OF_SCOPE,
    STATUS_UNCLEAR_REVIEW,
)

ACCESS_NONE = "none"
ACCESS_PAYWALL = "paywall"
ACCESS_INSTITUTION_LOGIN = "institution_login"
ACCESS_BOT_CHECK = "bot_check"
ACCESS_JS_REQUIRED = "js_required"
ACCESS_PURCHASE_PAGE = "purchase_page"
ACCESS_BROKEN_LINK = "broken_link"
ACCESS_UNKNOWN = "unknown"

DENOM_TRUE = "TRUE"
DENOM_FALSE = "FALSE"
DENOM_REVIEW = "REVIEW"

PDF_AVAILABILITY_FIELDS = (
    "DOI",
    "pdf_gold_status",
    "pdf_gold_url",
    "pdf_gold_access_type",
    "pdf_gold_include_in_public_denominator",
    "pdf_gold_include_in_all_known_pdf_denominator",
    "pdf_gold_confidence",
    "pdf_gold_evidence",
    "pdf_gold_review_needed",
    "pdf_gold_review_reason",
    "pdf_gold_source",
    "pdf_gold_checked_at",
)

PUBLIC_TRUE_FAILURE_FIELDS = (
    "rank",
    "DOI",
    "latest_taxicab_category",
    "publisher",
    "host",
    "pdf_gold_status",
    "pdf_gold_confidence",
    "pdf_gold_url",
    "candidate_url",
    "resolved_url",
    "status_code",
    "content_type",
    "size_bytes",
    "page_count",
    "text_chars",
    "validation_errors",
    "error",
    "evidence_snippet",
    "next_action",
)

PAYWALL_RE = re.compile(
    r"\b("
    r"paywall|subscription|subscribe|purchase|buy now|get access|institution(?:al)? login|"
    r"log in(?: to your institution)?|login required|sign in|rent this article|purchase access"
    r")\b",
    re.IGNORECASE,
)
NO_PDF_RE = re.compile(
    r"\b(no pdf|pdf not (?:available|found)|no full[- ]text pdf|html[- ]only|landing page only)\b",
    re.IGNORECASE,
)
SUPPLEMENT_RE = re.compile(
    r"\b(supplement|supplementary|preview|first page|front matter|table of contents|cover page)\b",
    re.IGNORECASE,
)
NON_ARTICLE_RE = re.compile(
    r"\b(obituary|front matter|journal page|book review|editorial board|masthead|index|erratum only|correction only)\b",
    re.IGNORECASE,
)
BROKEN_RE = re.compile(r"\b(broken|404|not found|bad doi|invalid doi|dead link|malformed)\b", re.IGNORECASE)
JS_RE = re.compile(r"\b(enable javascript|javascript required|js redirect|window\.location)\b", re.IGNORECASE)


@dataclass(frozen=True)
class PdfAvailabilityLabel:
    DOI: str
    pdf_gold_status: str
    pdf_gold_url: str
    pdf_gold_access_type: str
    pdf_gold_include_in_public_denominator: str
    pdf_gold_include_in_all_known_pdf_denominator: str
    pdf_gold_confidence: str
    pdf_gold_evidence: str
    pdf_gold_review_needed: str
    pdf_gold_review_reason: str
    pdf_gold_source: str
    pdf_gold_checked_at: str

    def to_dict(self) -> dict[str, str]:
        return {field: str(asdict(self).get(field, "")) for field in PDF_AVAILABILITY_FIELDS}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_doi(value: str | None) -> str:
    doi = (value or "").strip().lower()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi)
    return doi.strip()


def truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "approved"}


def falsey(value: Any) -> bool:
    return str(value or "").strip().lower() in {"0", "false", "no", "n", "none", "rejected"}


def row_pdf_url(row: dict[str, Any]) -> str:
    for key in ("PDF URL", "pdf_url", "pdf", "fulltext_pdf_url", "candidate_url", "pdf_gold_url"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def _host_from_value(value: str) -> str:
    value = str(value or "").strip()
    if not value:
        return ""
    first = value.split()[0].strip().strip(",;")
    parsed = urlparse(first)
    host = parsed.netloc.lower()
    if not host and "://" not in first and "." in first and "/" not in first:
        host = first.lower()
    return host[4:] if host.startswith("www.") else host


def row_host(row: dict[str, Any]) -> str:
    for key in ("host", "resolved_url", "candidate_url", "PDF URL", "Link", "resolved_links"):
        host = _host_from_value(str(row.get(key) or ""))
        if host:
            return host
    return ""


def merged_text(row: dict[str, Any]) -> str:
    keys = (
        "Notes",
        "notes",
        "Status",
        "status",
        "pdf_gold_evidence",
        "error",
        "evidence_snippet",
        "validation_errors",
        "browserbase_verdict",
    )
    return " ".join(str(row.get(key) or "") for key in keys)


def make_label(
    *,
    doi: str,
    status: str,
    url: str,
    access_type: str,
    public: str,
    all_known: str,
    confidence: float,
    evidence: str,
    review_needed: bool,
    review_reason: str = "",
    source: str,
    checked_at: str,
) -> PdfAvailabilityLabel:
    if status not in PDF_GOLD_STATUSES:
        raise ValueError(f"unknown pdf gold status: {status}")
    confidence_text = f"{max(0.0, min(1.0, confidence)):.2f}"
    return PdfAvailabilityLabel(
        DOI=doi,
        pdf_gold_status=status,
        pdf_gold_url=url,
        pdf_gold_access_type=access_type,
        pdf_gold_include_in_public_denominator=public,
        pdf_gold_include_in_all_known_pdf_denominator=all_known,
        pdf_gold_confidence=confidence_text,
        pdf_gold_evidence=re.sub(r"\s+", " ", evidence).strip()[:500],
        pdf_gold_review_needed="TRUE" if review_needed else "FALSE",
        pdf_gold_review_reason=re.sub(r"\s+", " ", review_reason).strip()[:240],
        pdf_gold_source=source,
        pdf_gold_checked_at=checked_at,
    )


def label_pdf_availability(
    row: dict[str, Any],
    *,
    eval_row: dict[str, Any] | None = None,
    seed_label: dict[str, Any] | None = None,
    checked_at: str | None = None,
) -> PdfAvailabilityLabel:
    """Return a deterministic first-pass availability label for one DOI."""
    checked = checked_at or utc_now()
    doi = normalize_doi(row.get("DOI") or row.get("doi") or (eval_row or {}).get("doi"))
    if seed_label:
        data = {field: str(seed_label.get(field, "")) for field in PDF_AVAILABILITY_FIELDS}
        data["DOI"] = doi or normalize_doi(data.get("DOI"))
        data["pdf_gold_source"] = "seed_sidecar"
        data["pdf_gold_checked_at"] = checked
        return PdfAvailabilityLabel(**data)

    eval_row = eval_row or {}
    category = str(eval_row.get("category") or "").strip()
    url = row_pdf_url(eval_row) or row_pdf_url(row)
    source_text = merged_text(row)
    text = source_text + " " + merged_text(eval_row)
    has_bot = truthy(row.get("Has Bot Check") or row.get("has_bot_check")) or category == "bot_block_403"
    resolves_pdf = truthy(row.get("Resolves To PDF") or row.get("resolves_to_pdf"))
    broken_doi = truthy(row.get("broken_doi"))
    no_english = truthy(row.get("no english") or row.get("no_english"))
    source_bits = []
    if category:
        source_bits.append(f"latest_taxicab_category={category}")
    if url:
        source_bits.append("pdf_url_present")
    if resolves_pdf:
        source_bits.append("resolves_to_pdf=true")
    source = "automation"

    if category == "good_pdf":
        return make_label(
            doi=doi,
            status=STATUS_OPEN_FULL_TEXT_PDF,
            url=url,
            access_type=ACCESS_NONE,
            public=DENOM_TRUE,
            all_known=DENOM_TRUE,
            confidence=0.98,
            evidence="; ".join(source_bits + ["Taxicab validated good_pdf bytes/pages"]),
            review_needed=False,
            source=source,
            checked_at=checked,
        )

    if broken_doi or BROKEN_RE.search(text) and "doi" in text.lower():
        return make_label(
            doi=doi,
            status=STATUS_BROKEN_OR_BAD_DOI if broken_doi else STATUS_BROKEN_PDF_LINK,
            url=url,
            access_type=ACCESS_BROKEN_LINK,
            public=DENOM_FALSE,
            all_known=DENOM_FALSE,
            confidence=0.90,
            evidence="; ".join(source_bits + ["broken DOI/link evidence"]),
            review_needed=False,
            source=source,
            checked_at=checked,
        )

    if NON_ARTICLE_RE.search(text) or no_english:
        reason = "non-article evidence" if not no_english else "no english flagged in source"
        return make_label(
            doi=doi,
            status=STATUS_NON_ARTICLE_OUT_OF_SCOPE,
            url=url,
            access_type=ACCESS_NONE,
            public=DENOM_FALSE,
            all_known=DENOM_FALSE,
            confidence=0.82,
            evidence="; ".join(source_bits + [reason]),
            review_needed=False,
            source=source,
            checked_at=checked,
        )

    if SUPPLEMENT_RE.search(text) or category == "supplement_or_preview_pdf":
        return make_label(
            doi=doi,
            status=STATUS_SUPPLEMENT_OR_PREVIEW,
            url=url,
            access_type=ACCESS_NONE,
            public=DENOM_FALSE,
            all_known=DENOM_FALSE,
            confidence=0.86,
            evidence="; ".join(source_bits + ["supplement/preview evidence"]),
            review_needed=False,
            source=source,
            checked_at=checked,
        )

    if PAYWALL_RE.search(text) or category == "interstitial_or_paywall":
        access = ACCESS_INSTITUTION_LOGIN if re.search(r"institution|login|sign in", text, re.I) else ACCESS_PAYWALL
        if re.search(r"buy now|purchase|rent", text, re.I):
            access = ACCESS_PURCHASE_PAGE
        return make_label(
            doi=doi,
            status=STATUS_PAYWALLED_OR_LOGIN,
            url=url,
            access_type=access,
            public=DENOM_FALSE,
            all_known=DENOM_TRUE,
            confidence=0.82 if url else 0.66,
            evidence="; ".join(source_bits + ["paywall/login/purchase evidence"]),
            review_needed=not bool(url),
            review_reason="" if url else "paywall evidence but no concrete PDF URL",
            source=source,
            checked_at=checked,
        )

    if has_bot:
        return make_label(
            doi=doi,
            status=STATUS_UNCLEAR_REVIEW,
            url=url,
            access_type=ACCESS_BOT_CHECK,
            public=DENOM_REVIEW,
            all_known=DENOM_REVIEW,
            confidence=0.50,
            evidence="; ".join(source_bits + ["bot check hides PDF availability"]),
            review_needed=True,
            review_reason="bot check hides whether a real full-text PDF is public",
            source=source,
            checked_at=checked,
        )

    if JS_RE.search(text) or category == "js_redirect_unresolved":
        return make_label(
            doi=doi,
            status=STATUS_UNCLEAR_REVIEW,
            url=url,
            access_type=ACCESS_JS_REQUIRED,
            public=DENOM_REVIEW,
            all_known=DENOM_REVIEW,
            confidence=0.55,
            evidence="; ".join(source_bits + ["JavaScript redirect/rendering hides PDF availability"]),
            review_needed=True,
            review_reason="JS flow needs browser/gold evidence before denominator decision",
            source=source,
            checked_at=checked,
        )

    if category in {"corrupt_or_truncated_pdf", "encrypted_or_unreadable_pdf", "wrong_pdf_content"}:
        return make_label(
            doi=doi,
            status=STATUS_OPEN_FULL_TEXT_PDF,
            url=url,
            access_type=ACCESS_NONE,
            public=DENOM_TRUE,
            all_known=DENOM_TRUE,
            confidence=0.74,
            evidence="; ".join(source_bits + ["Taxicab received PDF-like content but validation failed"]),
            review_needed=False,
            source=source,
            checked_at=checked,
        )

    if resolves_pdf and url:
        return make_label(
            doi=doi,
            status=STATUS_OPEN_FULL_TEXT_PDF,
            url=url,
            access_type=ACCESS_NONE,
            public=DENOM_TRUE,
            all_known=DENOM_TRUE,
            confidence=0.94,
            evidence="; ".join(source_bits + ["source says URL resolves to PDF"]),
            review_needed=False,
            source=source,
            checked_at=checked,
        )

    if NO_PDF_RE.search(source_text):
        status = STATUS_HTML_FULL_TEXT_ONLY if re.search(r"html", source_text, re.I) else STATUS_NO_FULL_TEXT_PDF
        return make_label(
            doi=doi,
            status=status,
            url=url,
            access_type=ACCESS_NONE,
            public=DENOM_FALSE,
            all_known=DENOM_FALSE,
            confidence=0.84,
            evidence="; ".join(source_bits + ["no full-text PDF evidence"]),
            review_needed=False,
            source=source,
            checked_at=checked,
        )

    if category in {"missing_pdf_harvest", "html_instead_of_pdf", "download_404", "empty_response"}:
        return make_label(
            doi=doi,
            status=STATUS_UNCLEAR_REVIEW,
            url=url,
            access_type=ACCESS_UNKNOWN,
            public=DENOM_REVIEW,
            all_known=DENOM_REVIEW,
            confidence=0.42,
            evidence="; ".join(source_bits + ["Taxicab raw eval expected a PDF but did not recover one"]),
            review_needed=True,
            review_reason="raw expected PDF miss needs gold availability review before denominator exclusion",
            source=source,
            checked_at=checked,
        )

    if url:
        return make_label(
            doi=doi,
            status=STATUS_UNCLEAR_REVIEW,
            url=url,
            access_type=ACCESS_UNKNOWN,
            public=DENOM_REVIEW,
            all_known=DENOM_REVIEW,
            confidence=0.45,
            evidence="; ".join(source_bits + ["PDF URL exists but availability is unverified"]),
            review_needed=True,
            review_reason="PDF URL exists but automation could not prove public/full-text availability",
            source=source,
            checked_at=checked,
        )

    if category and category != "no_pdf_expected":
        return make_label(
            doi=doi,
            status=STATUS_UNCLEAR_REVIEW,
            url="",
            access_type=ACCESS_UNKNOWN,
            public=DENOM_REVIEW,
            all_known=DENOM_REVIEW,
            confidence=0.40,
            evidence="; ".join(source_bits + ["Taxicab category needs availability review"]),
            review_needed=True,
            review_reason="Taxicab category is not enough evidence to exclude from PDF denominator",
            source=source,
            checked_at=checked,
        )

    return make_label(
        doi=doi,
        status=STATUS_NO_FULL_TEXT_PDF,
        url="",
        access_type=ACCESS_NONE,
        public=DENOM_FALSE,
        all_known=DENOM_FALSE,
        confidence=0.72 if category == "no_pdf_expected" else 0.60,
        evidence="; ".join(source_bits + ["no PDF URL or positive PDF evidence"]),
        review_needed=False,
        source=source,
        checked_at=checked,
    )


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def csv_cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value)
    return re.sub(r"[\x00-\x1f\x7f]+", " ", text).strip()


def write_csv_rows(path: Path, rows: Iterable[dict[str, Any]], fieldnames: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_cell(row.get(field, "")) for field in writer.fieldnames})


def read_sidecar(path: Path) -> dict[str, dict[str, str]]:
    rows = read_csv_rows(path)
    return {normalize_doi(row.get("DOI")): row for row in rows if normalize_doi(row.get("DOI"))}


def read_eval_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not path or not path.exists():
        return rows
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            doi = normalize_doi(row.get("doi") or row.get("DOI"))
            if doi:
                rows[doi] = row
    return rows


def generate_availability_rows(
    corpus_rows: Iterable[dict[str, Any]],
    *,
    eval_rows_by_doi: dict[str, dict[str, Any]] | None = None,
    seed_by_doi: dict[str, dict[str, Any]] | None = None,
    checked_at: str | None = None,
) -> list[PdfAvailabilityLabel]:
    eval_rows_by_doi = eval_rows_by_doi or {}
    seed_by_doi = seed_by_doi or {}
    checked = checked_at or utc_now()
    labels: list[PdfAvailabilityLabel] = []
    for row in corpus_rows:
        doi = normalize_doi(row.get("DOI") or row.get("doi"))
        if not doi:
            continue
        labels.append(
            label_pdf_availability(
                row,
                eval_row=eval_rows_by_doi.get(doi),
                seed_label=seed_by_doi.get(doi),
                checked_at=checked,
            )
        )
    return labels


def review_priority(label: PdfAvailabilityLabel, host_counts: Counter[str], host: str) -> tuple[int, int, str]:
    public = label.pdf_gold_include_in_public_denominator
    status = label.pdf_gold_status
    score = 0
    if public == DENOM_REVIEW:
        score += 1000
    if status in {STATUS_UNCLEAR_REVIEW, STATUS_PAYWALLED_OR_LOGIN}:
        score += 300
    if label.pdf_gold_url:
        score += 100
    score += min(200, host_counts.get(host, 0))
    return (-score, -host_counts.get(host, 0), label.DOI)


def build_review_queue(
    labels: Iterable[PdfAvailabilityLabel],
    *,
    source_rows_by_doi: dict[str, dict[str, Any]] | None = None,
    eval_rows_by_doi: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    source_rows_by_doi = source_rows_by_doi or {}
    eval_rows_by_doi = eval_rows_by_doi or {}
    label_list = list(labels)
    host_by_doi: dict[str, str] = {}
    for label in label_list:
        source = source_rows_by_doi.get(normalize_doi(label.DOI), {})
        eval_row = eval_rows_by_doi.get(normalize_doi(label.DOI), {})
        host_by_doi[normalize_doi(label.DOI)] = row_host(eval_row) or row_host(source)
    host_counts = Counter(host for host in host_by_doi.values() if host)
    rows: list[dict[str, Any]] = []
    for label in label_list:
        doi = normalize_doi(label.DOI)
        if label.pdf_gold_review_needed != "TRUE" and label.pdf_gold_include_in_public_denominator != DENOM_REVIEW:
            continue
        source = source_rows_by_doi.get(doi, {})
        eval_row = eval_rows_by_doi.get(doi, {})
        host = host_by_doi.get(doi, "")
        row = label.to_dict()
        row.update(
            {
                "pdf_gold_priority_host_count": host_counts.get(host, 0),
                "pdf_gold_host": host,
                "latest_taxicab_category": eval_row.get("category", ""),
                "Link": source.get("Link", ""),
                "PDF URL": source.get("PDF URL", ""),
                "Notes": source.get("Notes", ""),
            }
        )
        rows.append(row)
    rows.sort(
        key=lambda row: review_priority(
            PdfAvailabilityLabel(**{field: row.get(field, "") for field in PDF_AVAILABILITY_FIELDS}),
            host_counts,
            str(row.get("pdf_gold_host") or ""),
        )
    )
    return rows


def _label_dict(label: PdfAvailabilityLabel | dict[str, Any]) -> dict[str, str]:
    if isinstance(label, PdfAvailabilityLabel):
        return label.to_dict()
    return {field: str(label.get(field, "")) for field in PDF_AVAILABILITY_FIELDS}


def _validation_errors_text(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    return str(value or "")


def _public_true_failure_action(category: str) -> str:
    if category == "corrupt_or_truncated_pdf":
        return "Mechanic-PDF: inspect validator/provider bytes; Envoy-Zyte if provider returns malformed PDF bytes"
    if category == "encrypted_or_unreadable_pdf":
        return "Mechanic-PDF: inspect encryption/readability policy before changing retrieval"
    if category == "missing_pdf_harvest":
        return "Lens-PDF + Envoy-Zyte: collect evidence for public PDF URL before route or provider change"
    if category in {"html_instead_of_pdf", "js_redirect_unresolved", "interstitial_or_paywall", "bot_block_403"}:
        return "Lens-PDF: browser/gold evidence; Envoy-Zyte: support packet if browser proves recoverability"
    if category == "missing_eval_row":
        return "Meter-PDF: rerun latest eval or inspect DOI join before retrieval work"
    return "Quarry-PDF: inspect cluster and choose evidence-first Mechanic or Envoy path"


def build_public_true_failure_queue(
    labels: Iterable[PdfAvailabilityLabel | dict[str, Any]],
    *,
    eval_rows_by_doi: dict[str, dict[str, Any]] | None = None,
    source_rows_by_doi: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return public-denominator TRUE rows that are not latest ``good_pdf``.

    This is the Gate 5 work queue: it excludes paywalled/FALSE rows and REVIEW
    rows, then keeps only rows where the latest Taxicab PDF verdict still needs
    work. It does not browse or mutate Taxicab storage.
    """
    eval_rows_by_doi = eval_rows_by_doi or {}
    source_rows_by_doi = source_rows_by_doi or {}
    rows: list[dict[str, Any]] = []
    for label in labels:
        label_row = _label_dict(label)
        if label_row.get("pdf_gold_include_in_public_denominator", "").strip().upper() != DENOM_TRUE:
            continue
        doi = normalize_doi(label_row.get("DOI"))
        eval_row = eval_rows_by_doi.get(doi, {})
        category = str(eval_row.get("category") or "missing_eval_row")
        if category == "good_pdf":
            continue
        source = source_rows_by_doi.get(doi, {})
        host = row_host(eval_row) or row_host(source) or row_host(label_row)
        publisher = str(eval_row.get("publisher") or source.get("Publisher") or source.get("publisher") or "unknown")
        rows.append(
            {
                "rank": 0,
                "DOI": doi,
                "latest_taxicab_category": category,
                "publisher": publisher,
                "host": host,
                "pdf_gold_status": label_row.get("pdf_gold_status", ""),
                "pdf_gold_confidence": label_row.get("pdf_gold_confidence", ""),
                "pdf_gold_url": label_row.get("pdf_gold_url", ""),
                "candidate_url": eval_row.get("candidate_url", "") or source.get("PDF URL", ""),
                "resolved_url": eval_row.get("resolved_url", ""),
                "status_code": eval_row.get("status_code", ""),
                "content_type": eval_row.get("content_type", ""),
                "size_bytes": eval_row.get("size_bytes", ""),
                "page_count": eval_row.get("page_count", ""),
                "text_chars": eval_row.get("text_chars", ""),
                "validation_errors": _validation_errors_text(eval_row.get("validation_errors", "")),
                "error": eval_row.get("error", ""),
                "evidence_snippet": eval_row.get("evidence_snippet", ""),
                "next_action": _public_true_failure_action(category),
            }
        )
    host_counts = Counter(str(row.get("host") or "unknown") for row in rows)
    category_counts = Counter(str(row.get("latest_taxicab_category") or "unknown") for row in rows)
    rows.sort(
        key=lambda row: (
            -host_counts.get(str(row.get("host") or "unknown"), 0),
            str(row.get("host") or ""),
            -category_counts.get(str(row.get("latest_taxicab_category") or "unknown"), 0),
            str(row.get("latest_taxicab_category") or ""),
            str(row.get("DOI") or ""),
        )
    )
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows


def summarize_public_true_failures(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    row_list = list(rows)
    category_counts = Counter(str(row.get("latest_taxicab_category") or "unknown") for row in row_list)
    host_counts = Counter(str(row.get("host") or "unknown") for row in row_list)
    publisher_counts = Counter(str(row.get("publisher") or "unknown") for row in row_list)
    host_category_counts: dict[str, Counter[str]] = {}
    for row in row_list:
        host = str(row.get("host") or "unknown")
        host_category_counts.setdefault(host, Counter())[str(row.get("latest_taxicab_category") or "unknown")] += 1
    top_hosts = []
    for host, count in host_counts.most_common(25):
        dominant_category = host_category_counts.get(host, Counter()).most_common(1)
        top_hosts.append(
            {
                "host": host,
                "rows": count,
                "dominant_category": dominant_category[0][0] if dominant_category else "unknown",
            }
        )
    return {
        "total": len(row_list),
        "category_counts": dict(sorted(category_counts.items())),
        "host_counts": dict(sorted(host_counts.items(), key=lambda item: (-item[1], item[0]))),
        "publisher_counts": dict(sorted(publisher_counts.items(), key=lambda item: (-item[1], item[0]))),
        "top_hosts": top_hosts,
    }


def summarize_availability_sidecar(labels: Iterable[PdfAvailabilityLabel]) -> dict[str, Any]:
    label_list = list(labels)
    status_counts = Counter(label.pdf_gold_status for label in label_list)
    public_counts = Counter(label.pdf_gold_include_in_public_denominator for label in label_list)
    all_counts = Counter(label.pdf_gold_include_in_all_known_pdf_denominator for label in label_list)
    return {
        "total": len(label_list),
        "status_counts": dict(sorted(status_counts.items())),
        "public_denominator_counts": dict(sorted(public_counts.items())),
        "all_known_pdf_denominator_counts": dict(sorted(all_counts.items())),
        "review_needed_total": sum(1 for label in label_list if label.pdf_gold_review_needed == "TRUE"),
    }


__all__ = [
    "DENOM_FALSE",
    "DENOM_REVIEW",
    "DENOM_TRUE",
    "PDF_AVAILABILITY_FIELDS",
    "PDF_GOLD_STATUSES",
    "PUBLIC_TRUE_FAILURE_FIELDS",
    "PdfAvailabilityLabel",
    "build_review_queue",
    "build_public_true_failure_queue",
    "generate_availability_rows",
    "label_pdf_availability",
    "normalize_doi",
    "read_csv_rows",
    "read_eval_rows",
    "read_sidecar",
    "summarize_availability_sidecar",
    "summarize_public_true_failures",
    "write_csv_rows",
]
