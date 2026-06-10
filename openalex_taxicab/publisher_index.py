"""DOI prefix and URL-domain publisher classifier for Taxicab evals.

Vendored/adapted from Parseland's ``scripts/lib/publisher_index.py``.
Taxicab uses it to group retrieval failures by publisher and host. Network
registrant lookup is disabled by default so eval runs are reproducible.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse


DOI_PREFIX_PUBLISHER: dict[str, str] = {
    "10.1001": "ama",
    "10.1002": "wiley",
    "10.1007": "springer",
    "10.1016": "elsevier",
    "10.1017": "cup",
    "10.1021": "acs",
    "10.1023": "springer",
    "10.1029": "wiley",
    "10.1037": "apa",
    "10.1038": "springer",
    "10.1039": "rsc",
    "10.1051": "edp_sciences",
    "10.1055": "thieme",
    "10.1056": "nejm",
    "10.1057": "springer",
    "10.1063": "aip_publishing",
    "10.1080": "taylor",
    "10.1088": "iop",
    "10.1089": "mary_ann_liebert",
    "10.1093": "oxford",
    "10.1097": "lippincott",
    "10.1101": "cshlp",
    "10.1103": "aps",
    "10.1108": "emerald",
    "10.1109": "ieee",
    "10.1111": "wiley",
    "10.1115": "asme",
    "10.1117": "spie",
    "10.1121": "asa",
    "10.1126": "aaas",
    "10.1128": "asm",
    "10.1136": "bmj",
    "10.1142": "world_scientific",
    "10.1145": "acm",
    "10.1148": "rsna",
    "10.1155": "hindawi",
    "10.1158": "aacr",
    "10.1159": "karger",
    "10.1161": "lippincott",
    "10.1163": "brill",
    "10.1175": "ams",
    "10.1177": "sage",
    "10.1182": "ash",
    "10.1186": "springer",
    "10.1200": "asco",
    "10.1201": "taylor",
    "10.1242": "company_biologists",
    "10.1364": "optica",
    "10.1371": "plos",
    "10.1504": "inderscience",
    "10.1515": "de_gruyter",
    "10.1590": "scielo",
    "10.21037": "ame",
    "10.21203": "research_square",
    "10.2139": "ssrn",
    "10.2174": "bentham",
    "10.3389": "frontiers",
    "10.3390": "mdpi",
    "10.3917": "cairn",
    "10.4324": "taylor",
    "10.5194": "copernicus",
}


DOMAIN_PUBLISHER: dict[str, str | None] = {
    "doi.org": None,
    "dx.doi.org": None,
    "sciencedirect.com": "elsevier",
    "linkinghub.elsevier.com": "elsevier",
    "elsevier.com": "elsevier",
    "onlinelibrary.wiley.com": "wiley",
    "wiley.com": "wiley",
    "agupubs.onlinelibrary.wiley.com": "wiley",
    "link.springer.com": "springer",
    "springer.com": "springer",
    "springeropen.com": "springer",
    "nature.com": "springer",
    "biomedcentral.com": "springer",
    "ieeexplore.ieee.org": "ieee",
    "ieee.org": "ieee",
    "pubs.acs.org": "acs",
    "acs.org": "acs",
    "tandfonline.com": "taylor",
    "taylorfrancis.com": "taylor",
    "journals.sagepub.com": "sage",
    "sagepub.com": "sage",
    "journals.lww.com": "lippincott",
    "lww.com": "lippincott",
    "academic.oup.com": "oxford",
    "oup.com": "oxford",
    "cambridge.org": "cup",
    "frontiersin.org": "frontiers",
    "mdpi.com": "mdpi",
    "journals.plos.org": "plos",
    "plos.org": "plos",
    "bmj.com": "bmj",
    "nejm.org": "nejm",
    "dl.acm.org": "acm",
    "acm.org": "acm",
    "science.org": "aaas",
    "ascopubs.org": "asco",
    "ahajournals.org": "lippincott",
    "thieme-connect.com": "thieme",
    "karger.com": "karger",
    "rsc.org": "rsc",
    "pubs.rsc.org": "rsc",
    "iopscience.iop.org": "iop",
    "iop.org": "iop",
    "pubs.aip.org": "aip_publishing",
    "aip.org": "aip_publishing",
    "journals.aps.org": "aps",
    "aps.org": "aps",
    "degruyter.com": "de_gruyter",
    "brill.com": "brill",
    "liebertpub.com": "mary_ann_liebert",
    "spie.org": "spie",
    "spiedigitallibrary.org": "spie",
    "emerald.com": "emerald",
    "emeraldinsight.com": "emerald",
    "hindawi.com": "hindawi",
    "scielo.br": "scielo",
    "scielo.cl": "scielo",
    "scielo.org": "scielo",
    "edpsciences.org": "edp_sciences",
    "copernicus.org": "copernicus",
    "f1000research.com": "f1000",
    "f1000.com": "f1000",
    "ssrn.com": "ssrn",
    "papers.ssrn.com": "ssrn",
    "researchsquare.com": "research_square",
    "biorxiv.org": "rxiv",
    "arxiv.org": "rxiv",
    "medrxiv.org": "rxiv",
    "chemrxiv.org": "rxiv",
    "preprints.org": "rxiv",
    "psyarxiv.com": "rxiv",
}


REGISTRANT_NORMALIZE: list[tuple[str, str]] = [
    ("wiley", "wiley"),
    ("elsevier", "elsevier"),
    ("springer", "springer"),
    ("nature", "springer"),
    ("biomed central", "springer"),
    ("ieee", "ieee"),
    ("american chemical society", "acs"),
    ("taylor", "taylor"),
    ("informa", "taylor"),
    ("sage", "sage"),
    ("wolters kluwer", "lippincott"),
    ("lippincott", "lippincott"),
    ("oxford", "oxford"),
    ("cambridge", "cup"),
    ("frontiers", "frontiers"),
    ("mdpi", "mdpi"),
    ("public library of science", "plos"),
    ("plos", "plos"),
    ("bmj", "bmj"),
    ("massachusetts medical society", "nejm"),
    ("association for computing machinery", "acm"),
    ("american association for the advancement of science", "aaas"),
    ("aip publishing", "aip_publishing"),
    ("american physical society", "aps"),
    ("american meteorological society", "ams"),
    ("emerald", "emerald"),
    ("radiological society", "rsna"),
    ("hindawi", "hindawi"),
    ("brill", "brill"),
    ("spie", "spie"),
    ("american psychological association", "apa"),
    ("de gruyter", "de_gruyter"),
    ("copernicus", "copernicus"),
    ("ame publishing", "ame"),
    ("cairn", "cairn"),
    ("optica publishing", "optica"),
    ("company of biologists", "company_biologists"),
    ("portland press", "portland_press"),
    ("cold spring harbor", "cshlp"),
    ("american association for cancer research", "aacr"),
    ("american society of hematology", "ash"),
    ("american society of clinical oncology", "asco"),
    ("american society of mechanical engineers", "asme"),
    ("bentham", "bentham"),
    ("american geophysical union", "wiley"),
    ("acoustical society of america", "asa"),
    ("royal society of chemistry", "rsc"),
    ("iop publishing", "iop"),
    ("thieme", "thieme"),
    ("karger", "karger"),
    ("mary ann liebert", "mary_ann_liebert"),
    ("scielo", "scielo"),
    ("edp sciences", "edp_sciences"),
    ("f1000", "f1000"),
    ("ssrn", "ssrn"),
    ("research square", "research_square"),
    ("biorxiv", "rxiv"),
    ("arxiv", "rxiv"),
    ("medrxiv", "rxiv"),
    ("chemrxiv", "rxiv"),
    ("psyarxiv", "rxiv"),
    ("preprints", "rxiv"),
]


_REGISTRANT_CACHE_PATH = Path(__file__).resolve().parents[1] / "eval_runs" / "_registrant-cache.json"


def _load_registrant_cache(path: Path | None = None) -> dict[str, str | None]:
    cache_path = path or _REGISTRANT_CACHE_PATH
    if not cache_path.exists():
        return {}
    try:
        return json.loads(cache_path.read_text())
    except Exception:
        return {}


def _save_registrant_cache(cache: dict[str, str | None], path: Path | None = None) -> None:
    cache_path = path or _REGISTRANT_CACHE_PATH
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cache, indent=2, sort_keys=True))
    tmp.replace(cache_path)


def normalize_doi(doi: str) -> str:
    if not doi:
        return ""
    s = doi.strip()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
    ):
        if s.lower().startswith(prefix):
            s = s[len(prefix):]
            break
    return s.strip().lower()


def doi_prefix(doi: str) -> str:
    normalized = normalize_doi(doi)
    if "/" not in normalized or not normalized.startswith("10."):
        return ""
    return normalized.split("/", 1)[0]


def prefix_to_publisher(doi: str) -> str | None:
    prefix = doi_prefix(doi)
    if not prefix:
        return None
    return DOI_PREFIX_PUBLISHER.get(prefix)


def host_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def domain_to_publisher(url: str) -> str | None:
    host = host_from_url(url)
    if not host:
        return None
    if host in DOMAIN_PUBLISHER:
        return DOMAIN_PUBLISHER[host]
    for domain, publisher in DOMAIN_PUBLISHER.items():
        if publisher is not None and host.endswith("." + domain):
            return publisher
    return None


def normalize_registrant_name(name: str) -> str | None:
    if not name:
        return None
    normalized = name.lower()
    for needle, publisher in REGISTRANT_NORMALIZE:
        if needle in normalized:
            return publisher
    return None


def registrant_to_publisher(
    doi: str,
    *,
    allow_network: bool = False,
    _cache: dict[str, str | None] | None = None,
) -> str | None:
    prefix = doi_prefix(doi)
    if not prefix:
        return None
    cache = _cache if _cache is not None else _load_registrant_cache()
    if prefix in cache:
        return cache[prefix]
    if not allow_network:
        return None
    try:
        import urllib.request

        url = f"https://api.crossref.org/prefixes/{prefix}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "taxicab-eval/0.1 (mailto:team@openalex.org)"},
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read())
        name = (data.get("message") or {}).get("name") or ""
        publisher = normalize_registrant_name(name)
        cache[prefix] = publisher
    except Exception:
        publisher = None
        cache[prefix] = None
    if _cache is None:
        _save_registrant_cache(cache)
    return publisher


def classify_row(
    row: dict,
    *,
    allow_network: bool = False,
    resolved_url: str = "",
    _cache: dict[str, str | None] | None = None,
) -> str:
    doi = row.get("DOI") or row.get("doi") or ""
    link = row.get("Link") or row.get("link") or row.get("url") or ""
    for candidate in (
        prefix_to_publisher(doi),
        domain_to_publisher(resolved_url),
        domain_to_publisher(link),
        registrant_to_publisher(doi, allow_network=allow_network, _cache=_cache),
    ):
        if candidate:
            return candidate
    return "unknown"


__all__ = [
    "DOI_PREFIX_PUBLISHER",
    "DOMAIN_PUBLISHER",
    "REGISTRANT_NORMALIZE",
    "classify_row",
    "doi_prefix",
    "domain_to_publisher",
    "host_from_url",
    "normalize_doi",
    "normalize_registrant_name",
    "prefix_to_publisher",
    "registrant_to_publisher",
]
