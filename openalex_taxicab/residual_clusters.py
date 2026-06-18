"""Cluster Taxicab eval residuals into actionable work queues."""

from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qsl, unquote, urlencode, urlsplit, urlunsplit

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
PATH_DYNAMIC_EXTENSIONS = {".pdf", ".html", ".htm", ".xml", ".aspx", ".ashx"}

PRIOR_ROUTE_CANDIDATE_PATTERNS = ()

PRIOR_PROVIDER_HOSTS = {
    "aacr.figshare.com",
    "academic.oup.com",
    "api.taylorfrancis.com",
    "actahort.org",
    "airitilibrary.com",
    "ajconline.org",
    "ajo.com",
    "americanjournalofsurgery.com",
    "ams.org",
    "aip.scitation.org",
    "arc.aiaa.org",
    "ascelibrary.org",
    "asmedigitalcollection.asme.org",
    "ascopubs.org",
    "ahajournals.org",
    "asa.scitation.org",
    "atsjournals.org",
    "auajournals.org",
    "ajog.org",
    "aimsciences.org",
    "brepolsonline.net",
    "brill.com",
    "bmj.com",
    "biorxiv.org",
    "bioone.org",
    "cairn.info",
    "cambridge.org",
    "cell.com",
    "cdnsciencepub.com",
    "cghjournal.org",
    "cccc.uochb.cas.cz",
    "chestnet.org",
    "clinicalmicrobiologyandinfection.com",
    "cochranelibrary.com",
    "compass.astm.org",
    "connect.springerpub.com",
    "content.ampp.org",
    "content.iospress.com",
    "content.iospress.com:443",
    "diabetesjournals.org",
    "digital-library.theiet.org",
    "direct.mit.edu",
    "dl.acm.org",
    "dl.begellhouse.com",
    "downloads.hindawi.com",
    "ejso.com",
    "ecologica.cn",
    "elgaronline.com",
    "emerald.com",
    "essoar.org",
    "eurekaselect.com",
    "degruyterbrill.com",
    "goldjournal.net",
    "hindawi.com",
    "hpbonline.org",
    "icevirtuallibrary.com",
    "igi-global.com",
    "indianjournals.com",
    "ingentaconnect.com",
    "inlibra.com",
    "iopscience.iop.org",
    "iwaponline.com",
    "jacc.org",
    "jacionline.org",
    "jamanetwork.com",
    "jbc.org",
    "jcvaonline.com",
    "jmcc-online.com",
    "journalijar.com",
    "journals.uchicago.edu",
    "journals.aai.org",
    "journals.healio.com",
    "journals.humankinetics.com",
    "journals.jps.jp",
    "journals.lww.com",
    "journals.sagepub.com",
    "journals.ametsoc.org",
    "journals.asm.org",
    "jvi.asm.org",
    "journals.physiology.org",
    "jpharmsci.org",
    "jpet.aspetjournals.org",
    "jpedsurg.org",
    "jstage.jst.go.jp",
    "jstor.org",
    "karger.com",
    "koreascience.or.kr:80",
    "library.iated.org",
    "liebertpub.com",
    "link.springer.com",
    "link.aps.org",
    "maps.mla.org",
    "mattech-journal.org",
    "meetingorganizer.copernicus.org",
    "microbiologyresearch.org",
    "nature.com",
    "neurology.org",
    "nomos-elibrary.de",
    "opg.optica.org",
    "onlinelibrary.wiley.com",
    "online.ucpress.edu",
    "onepetro.org",
    "papers.ssrn.com",
    "pediatrics.aappublications.org",
    "persee.fr",
    "pdcnet.org",
    "pdf.sciencedirectassets.com",
    "peterlang.com",
    "pm-research.com",
    "pubs.acs.org",
    "pubs.rsna.org",
    "pubs.asha.org",
    "pubs.aip.org",
    "pubs.rsc.org",
    "pubs.geoscienceworld.org",
    "publications.aaahq.org",
    "publications.aap.org",
    "pubs.nctm.org",
    "read.dukeupress.edu",
    "royalsocietypublishing.org",
    "rupress.org",
    "sciencedirect.com",
    "scholarlypublishingcollective.org",
    "scientific.net",
    "shs.cairn.info",
    "sk.sagepub.com",
    "spiedigitallibrary.org",
    "storage.prod.researchhub.com",
    "sssjournal.com",
    "tandfonline.com",
    "tesr.journals.ekb.eg",
    "techscience.com",
    "techno-press.org",
    "thegreenjournal.com",
    "thejns.org",
    "thelancet.com",
    "theses.fr",
    "thieme-connect.de",
    "transcript-verlag.de",
    "triggered.clockss.orghttps:",
    "turkishstudies.net",
    "vestnik.krsu.kg",
    "vestnik-rosnou.ru",
    "vr-elibrary.de",
    "virtusinterpress.org",
    "www.ajconline.org",
    "www.ajo.com",
    "www.americanjournalofsurgery.com",
    "www.bmj.com",
    "www.cambridge.org",
    "www.cairn.info",
    "www.clinicalmicrobiologyandinfection.com",
    "www.cochranelibrary.com",
    "www.concrete.org",
    "www.dl.begellhouse.com",
    "www.degruyterbrill.com",
    "www.ejso.com",
    "www.essoar.org",
    "www.eurekaselect.com",
    "www.goldjournal.net",
    "www.indianjournals.com",
    "www.inlibra.com",
    "www.jbc.org",
    "www.jcvaonline.com",
    "www.jstor.org",
    "www.karger.com",
    "www.kci.go.kr",
    "www.journals.uchicago.edu",
    "www.nature.com",
    "www.neurology.org",
    "www.nomos-elibrary.de",
    "www.pdcnet.org",
    "www.persee.fr",
    "www.sciencedirect.com",
    "www.scientific.net",
    "www.tandfonline.com",
    "www.thelancet.com",
    "www.thieme-connect.de",
    "www.transcript-verlag.de",
    "www.vr-elibrary.de",
    "wmpllc.org",
    "wulixb.iphy.ac.cn",
    "worldscientific.com",
}

PRIOR_GOLD_HOSTS = {
    "drive.google.com",
}

PRIOR_DOI_RESOLVER_PUBLISHERS = {
    "aaas",
    "aps",
    "elsevier",
    "lippincott",
    "oxford",
    "springer",
    "wiley",
}

PRIOR_UNKNOWN_DOI_RESOLVER_PATTERNS = {
    "doi.org:/:doi/:id",
    "doi.org:/:doi/:num",
    "doi.org:/:doi/bcsj.35.289",
    "doi.org:/:doi/mat-1811-56",
}

PRIOR_BRANCH_ONLY_PATTERNS = {
    ("html_instead_of_pdf", "peerj.com", "peerj.com:/articles/:file.pdf"),
}


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


@dataclass(frozen=True)
class ResidualSubcluster:
    category: str
    publisher: str
    host: str
    candidate_source: str
    path_pattern: str
    count: int
    support_candidates: int
    estimated_recoverable_rows: float
    recommended_agent: str
    recommended_action: str
    evidence_strength: str
    prior_evidence_status: str
    priority_band: str
    next_probe_decision: str

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "publisher": self.publisher,
            "host": self.host,
            "candidate_source": self.candidate_source,
            "path_pattern": self.path_pattern,
            "count": self.count,
            "support_candidates": self.support_candidates,
            "estimated_recoverable_rows": round(self.estimated_recoverable_rows, 2),
            "recommended_agent": self.recommended_agent,
            "recommended_action": self.recommended_action,
            "evidence_strength": self.evidence_strength,
            "prior_evidence_status": self.prior_evidence_status,
            "priority_band": self.priority_band,
            "next_probe_decision": self.next_probe_decision,
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


def subcluster_rows_by_path(rows: Iterable[ResidualRow]) -> list[ResidualSubcluster]:
    grouped: dict[tuple[str, str, str, str, str], list[ResidualRow]] = defaultdict(list)
    for row in rows:
        if row.category in NON_RESIDUAL_CATEGORIES:
            continue
        url = residual_pattern_url(row)
        host = residual_host(row)
        source = (getattr(row, "candidate_source", "") or "unknown").strip() or "unknown"
        key = (
            row.category,
            row.publisher or "unknown",
            host,
            source,
            path_pattern(url, fallback_host=host),
        )
        grouped[key].append(row)

    subclusters = [
        _build_subcluster(category, publisher, host, source, pattern, items)
        for (category, publisher, host, source, pattern), items in grouped.items()
    ]
    return sorted(
        subclusters,
        key=lambda subcluster: (
            subcluster.estimated_recoverable_rows,
            subcluster.count,
            subcluster.category,
            subcluster.publisher,
            subcluster.host,
            subcluster.path_pattern,
        ),
        reverse=True,
    )


def _build_subcluster(
    category: str,
    publisher: str,
    host: str,
    candidate_source: str,
    pattern: str,
    rows: list[ResidualRow],
) -> ResidualSubcluster:
    weight = HOST_OVERRIDES.get((category, host), RECOVERABILITY_WEIGHTS.get(category, 0.10))
    support_candidates = sum(1 for row in rows if row.support_candidate)
    prior_status, priority_band, next_decision = subcluster_priority(category, publisher, host, pattern)
    return ResidualSubcluster(
        category=category,
        publisher=publisher,
        host=host,
        candidate_source=candidate_source,
        path_pattern=pattern,
        count=len(rows),
        support_candidates=support_candidates,
        estimated_recoverable_rows=len(rows) * weight,
        recommended_agent=recommended_agent(category, publisher, host),
        recommended_action=subcluster_recommended_action(category, publisher, host, pattern),
        evidence_strength=evidence_strength(category, publisher, host),
        prior_evidence_status=prior_status,
        priority_band=priority_band,
        next_probe_decision=next_decision,
    )


def subcluster_priority(category: str, publisher: str, host: str, pattern: str) -> tuple[str, str, str]:
    for pattern_prefix, status in PRIOR_ROUTE_CANDIDATE_PATTERNS:
        if pattern.startswith(pattern_prefix):
            return (
                status,
                "confirm_existing_branch_candidate",
                "Do not start a duplicate provider probe; use targeted read-only/full gates to confirm the existing branch route candidate before any main push.",
            )

    normalized_host = host.lower()
    normalized_publisher = publisher.lower()

    if (category, _strip_www(normalized_host), pattern) in PRIOR_BRANCH_ONLY_PATTERNS:
        return (
            "prior_branch_only_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing branch-only evidence and require targeted/full-gate proof before any route promotion.",
        )

    if category == "missing_pdf_harvest" and _host_has_prior_gold_evidence(normalized_host):
        return (
            "prior_gold_or_manual_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing gold/manual evidence; only rerun if testing a new provider-advised or manually verified recipe.",
        )

    if category == "missing_pdf_harvest" and _host_has_prior_provider_evidence(normalized_host):
        return (
            "prior_negative_or_support_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing provider/Zyte packet evidence or wait for provider guidance before route code; only rerun if testing a new provider-advised recipe.",
        )

    if category == "missing_pdf_harvest" and publisher.lower() == "elsevier":
        return (
            "prior_negative_or_support_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing Elsevier/ScienceDirect provider evidence or wait for provider guidance before route code; only rerun if testing a new provider-advised recipe.",
        )

    if pattern.startswith("doi.org:") and normalized_publisher in PRIOR_DOI_RESOLVER_PUBLISHERS:
        return (
            "prior_negative_or_support_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing publisher-specific DOI.org provider/gold evidence or wait for provider guidance before route code; only rerun if testing a new provider-advised recipe.",
        )

    if (
        pattern in PRIOR_UNKNOWN_DOI_RESOLVER_PATTERNS
        and category in {"html_instead_of_pdf", "js_redirect_unresolved", "bot_block_403"}
        and normalized_publisher == "unknown"
    ):
        return (
            "prior_negative_or_support_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing unknown DOI.org gold evidence before route code; only rerun if testing a new provider-advised or manually verified recipe.",
        )

    if category == "missing_pdf_harvest" and pattern.startswith("doi.org:"):
        return (
            "doi_resolver_pdf_route_needs_gold",
            "browserbase_or_zyte_gold_first",
            "Resolve the DOI route with Browserbase/Zyte evidence before treating it as a provider-specific PDF route.",
        )

    if (
        category in {"html_instead_of_pdf", "js_redirect_unresolved", "interstitial_or_paywall", "bot_block_403"}
        and _host_has_prior_provider_evidence(normalized_host)
    ):
        return (
            "prior_negative_or_support_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing provider/Zyte packet evidence or wait for provider guidance before route code; only rerun if testing a new provider-advised recipe.",
        )

    if (
        category
        in {
            "corrupt_or_truncated_pdf",
            "encrypted_or_unreadable_pdf",
            "supplement_or_preview_pdf",
            "wrong_pdf_content",
        }
        and _host_has_prior_provider_evidence(normalized_host)
    ):
        return (
            "prior_negative_or_support_evidence",
            "provider_lane_do_not_duplicate",
            "Use existing provider/Zyte packet or validator evidence; only rerun if testing a new provider-advised recipe or a stricter validator hypothesis.",
        )

    if category in {"html_instead_of_pdf", "js_redirect_unresolved", "interstitial_or_paywall", "bot_block_403"}:
        return (
            "needs_browser_or_provider_comparison",
            "browserbase_or_zyte_gold_first",
            "Collect Browserbase gold evidence or a Zyte support reproduction before changing Taxicab routing.",
        )

    if category in {"corrupt_or_truncated_pdf", "encrypted_or_unreadable_pdf"}:
        return (
            "needs_byte_validator_confirmation",
            "validator_or_provider_lane",
            "Compare byte-level PDF strategies and page/text validation before route code.",
        )

    if category == "missing_pdf_harvest":
        return (
            "fresh_probe_candidate",
            "probe_next",
            "Run a bounded no-storage provider probe first; reharvest only if no-storage evidence shows valid PDF recovery.",
        )

    return (
        "untriaged_residual",
        "inspect_first",
        "Inspect representative rows before assigning route, provider, or validator ownership.",
    )


def _host_has_prior_provider_evidence(host: str) -> bool:
    return _host_matches_known_set(host, PRIOR_PROVIDER_HOSTS)


def _host_has_prior_gold_evidence(host: str) -> bool:
    return _host_matches_known_set(host, PRIOR_GOLD_HOSTS)


def _host_matches_known_set(host: str, known_hosts: set[str]) -> bool:
    normalized = _strip_www(host.lower())
    for known_host in known_hosts:
        known = _strip_www(known_host.lower())
        if normalized == known or normalized.endswith(f".{known}"):
            return True
    return False


def _strip_www(host: str) -> str:
    return host[4:] if host.startswith("www.") else host


def residual_pattern_url(row: ResidualRow) -> str:
    for url in (
        getattr(row, "candidate_url", "") or "",
        getattr(row, "resolved_url", "") or "",
        getattr(row, "input_url", "") or "",
    ):
        if url:
            return url
    return ""


def path_pattern(url: str, *, fallback_host: str = "unknown", max_segments: int = 6) -> str:
    if not url:
        return f"{fallback_host or 'unknown'}:/unknown"
    parts = urlsplit(url)
    host = parts.netloc.lower() or (fallback_host or "unknown")
    raw_segments = [segment for segment in parts.path.split("/") if segment]
    if not raw_segments:
        return f"{host}:/"
    segments = [_normalize_path_segment(segment) for segment in raw_segments[:max_segments]]
    if len(raw_segments) > max_segments:
        segments.append("...")
    return f"{host}:/" + "/".join(segments)


def subcluster_recommended_action(category: str, publisher: str, host: str, pattern: str) -> str:
    base = recommended_action(category, publisher, host)
    if category == "missing_pdf_harvest":
        return f"{base}; prioritize a no-storage probe or bounded queue for path pattern `{pattern}`"
    if category in {"corrupt_or_truncated_pdf", "encrypted_or_unreadable_pdf"}:
        return f"{base}; compare PDF-byte strategies for path pattern `{pattern}` before route code"
    return f"{base}; sample path pattern `{pattern}` before broad host-level changes"


def _normalize_path_segment(segment: str) -> str:
    decoded = unquote(segment).lower()
    if not decoded:
        return ":empty"
    extension = _dynamic_extension(decoded)
    if decoded.startswith("10.") or re.search(r"(^|[^0-9])10\.\d{4,9}($|[^0-9])", decoded):
        return _with_extension(":doi", decoded)
    if re.fullmatch(r"\d+", decoded):
        return ":n" if len(decoded) < 4 else ":num"
    if re.fullmatch(r"[0-9a-f]{8,}", decoded):
        return _with_extension(":hex", decoded)
    if re.fullmatch(r"[a-z0-9_-]{18,}", decoded) and any(char.isdigit() for char in decoded):
        return _with_extension(":id", decoded)
    if re.search(r"\d{4,}", decoded) and len(decoded) >= 12:
        return _with_extension(":id", decoded)
    if extension == ".pdf":
        return ":file.pdf"
    return re.sub(r"\s+", "-", decoded)


def _with_extension(token: str, segment: str) -> str:
    extension = _dynamic_extension(segment)
    if extension:
        return f"{token}{extension}"
    return token


def _dynamic_extension(segment: str) -> str:
    match = re.search(r"(\.[a-z0-9]{1,6})$", segment)
    if match and match.group(1) in PATH_DYNAMIC_EXTENSIONS:
        return match.group(1)
    return ""


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
    subcluster_path = out_dir / "residual-subclusters.json"
    subcluster_csv_path = out_dir / "residual-subclusters.csv"

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
    subclusters = subcluster_rows_by_path(rows)
    _write_subcluster_artifacts(subcluster_path, subcluster_csv_path, subclusters, run_id=run_id, top_n=top_n)

    return {
        "clusters_json": cluster_path,
        "clusters_csv": cluster_csv_path,
        "subclusters_json": subcluster_path,
        "subclusters_csv": subcluster_csv_path,
        "browserbase_candidates": browserbase_path,
        "zyte_support_candidates": zyte_path,
    }


def _write_subcluster_artifacts(
    json_path: Path,
    csv_path: Path,
    subclusters: list[ResidualSubcluster],
    *,
    run_id: str,
    top_n: int,
) -> None:
    payload = {
        "run_id": run_id,
        "subcluster_count": len(subclusters),
        "top_subclusters": [subcluster.to_dict() for subcluster in subclusters[:top_n]],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(
            [
                "rank",
                "category",
                "publisher",
                "host",
                "candidate_source",
                "path_pattern",
                "count",
                "estimated_recoverable_rows",
                "support_candidates",
                "recommended_agent",
                "recommended_action",
                "evidence_strength",
                "prior_evidence_status",
                "priority_band",
                "next_probe_decision",
            ]
        )
        for rank, subcluster in enumerate(subclusters[:top_n], start=1):
            writer.writerow(
                [
                    rank,
                    subcluster.category,
                    subcluster.publisher,
                    subcluster.host,
                    subcluster.candidate_source,
                    subcluster.path_pattern,
                    subcluster.count,
                    f"{subcluster.estimated_recoverable_rows:.2f}",
                    subcluster.support_candidates,
                    subcluster.recommended_agent,
                    subcluster.recommended_action,
                    subcluster.evidence_strength,
                    subcluster.prior_evidence_status,
                    subcluster.priority_band,
                    subcluster.next_probe_decision,
                ]
            )


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
    "ResidualSubcluster",
    "browserbase_candidates",
    "cluster_rows",
    "path_pattern",
    "subcluster_priority",
    "recommended_action",
    "recommended_agent",
    "redact_text",
    "redact_url",
    "residual_host",
    "residual_pattern_url",
    "read_residual_rows_ndjson",
    "subcluster_rows_by_path",
    "write_cluster_artifacts",
    "zyte_support_candidates",
]
