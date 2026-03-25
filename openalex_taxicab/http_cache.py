from base64 import b64decode
import os
import re
from dataclasses import dataclass
from time import time
from typing import Optional
import json

import requests
import tenacity

from tenacity import retry, stop_after_attempt, wait_exponential, \
    retry_if_result
import requests.exceptions

from openalex_taxicab.log import _make_logger
from .util import elapsed

logger = _make_logger()

requests.packages.urllib3.disable_warnings()

DIRECT_FETCH_URLS = [
    "doaj.org",
    "handle.uba.uva.nl",
    "kerwa.ucr.ac.cr",
    "nbn-resolving.de",
    "nusl.cz",
    "publications.rwth-aachen.de",
    "pure.amsterdamumc.nl",
    "pure.au.dk",
    "pure.qub.ac.uk",
    "pure.uva.nl",
    "research.wu.ac.at",
    "researchprofiles.ku.dk",
]

BROWSER_HTML_URLS = [
    "cghjournal.org",
    "doi.org/10.1016",
    "doi.org/10.1037",
    "dsp.tecnalia.com",
    "elsevier.com",
    "iop.org",
    "psycnet.apa.org",
    "sciencedirect.com",
    "scholarship.libraries.rutgers.edu",
    "science.org",
    "wiley.com",
    "ncbi.nlm.nih.gov",
    "pmc.ncbi.nlm.nih.gov"
]

CRAWLERA_KEY = os.environ.get("CRAWLERA_KEY")
HTTP_PROXY = os.environ.get("HTTP_PROXY", "")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY", "")
STATIC_IP_PROXY = os.environ.get("STATIC_IP_PROXY")
ZYTE_API_KEY = os.environ.get("ZYTE_API_KEY")


MAX_PAYLOAD_SIZE_BYTES = 1000 * 1000 * 10  # 10mb

os.environ['NO_PROXY'] = 'impactstory.crawlera.com'


@dataclass
class ResponseObject:
    content: bytes
    headers: dict
    status_code: int
    url: str
    cookies: Optional[str] = None

    def __post_init__(self):
        self.headers = {header['name']: header['value'] for header in
                        self.headers}

    def text_small(self):
        return self.content

    def text_big(self):
        return self.content

    def content_big(self):
        return self.content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                f'Bad status code for URL {self.url}: {self.status_code}')


def is_direct_fetch_url(url):
    if re.search(r'(^|[./])dspace\.[a-z]', url):
        return True
    return any(re.search(f"(^|[./])({re.escape(pattern)})(/|$)", url)
              for pattern in DIRECT_FETCH_URLS)


def is_browser_html_url(url):
    return any(re.search(f"(^|[./])({re.escape(pattern)})(/|$)", url)
              for pattern in BROWSER_HTML_URLS)


BOT_PROTECTION_DOMAINS = [
    'perfdrive.com',
    'distilnetworks.com',
    'datadome.co',
    'imperva.com',
    'kasada.io',
]


def resolve_doi_redirects(doi_url, max_redirects=10):
    """
    Follow all redirects for a DOI URL using regular requests
    and return the final destination URL. If the final URL lands on a
    known bot protection domain, walk back to the last real publisher URL.
    """
    try:
        # Create a session to handle cookies and redirects
        session = requests.Session()

        # Use a HEAD request first to efficiently follow redirects
        response = session.head(
            doi_url,
            allow_redirects=True,
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )

        redirect_chain = [r.url for r in response.history] + [response.url]
        logger.info(f"DOI redirect chain: {' -> '.join(redirect_chain)}")

        final_url = response.url

        # If final URL is a bot protection page, walk back to the last real URL
        if any(domain in final_url for domain in BOT_PROTECTION_DOMAINS):
            for url in reversed(redirect_chain[:-1]):
                if not any(domain in url for domain in BOT_PROTECTION_DOMAINS):
                    logger.info(f"Bot protection detected at {final_url}, using {url} instead")
                    final_url = url
                    break

        return {
            "final_url": final_url,
            "redirect_chain": redirect_chain,
            "status_code": response.status_code
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error resolving DOI redirects: {e}")
        return None


def chooser_redirect(r):
    """
    Handle Crossref record pages and extract the first redirect link.

    This function works with ResponseObject instances returned by Zyte API.
    Identifies Crossref pages by their meta description and returns the first link
    in the resource container.
    """
    # Get the content as text
    try:
        content = r.text_small() if hasattr(r, 'text_small') else r.content

        # if content is bytes, decode it
        if isinstance(content, bytes):
            content = content.decode('utf-8', 'ignore')

        # check if it's a Crossref page using the meta description
        crossref_identifier = 'choose from multiple link options via crossref'

        if crossref_identifier in content.lower():
            # extract the first resource link
            pattern = r'<div class="resource-line">.*?<a\s+href="([^"]+)"[^>]*>'
            match = re.search(pattern, content, re.DOTALL)

            if match:
                url = match.group(1)
                logger.info(f'Found Crossref redirect: {url}')
                return url

    except Exception as e:
        logger.error(f"Error in chooser_redirect: {str(e)}")

    return None


def _fetch_dspace7_metadata(resolved_url):
    """Fetch metadata from the DSpace 7 REST API and synthesize an HTML page
    with standard citation_* meta tags.

    DSpace 7 pages are client-rendered Angular SPAs that contain no
    server-side metadata.  This function extracts the handle from the
    resolved URL, queries the REST API, and builds an HTML document that
    Parseland's generic publisher parser can extract authors, abstract,
    license, and PDF URLs from.

    Returns synthesized HTML string on success, or None on failure.
    """
    # Extract base URL and handle from the resolved URL
    # e.g. https://kops.uni-konstanz.de/handle/123456789/66470
    handle_match = re.search(r'(https?://[^/]+)/handle/(.+?)(?:\?|#|$)', resolved_url)
    if not handle_match:
        return None

    base_url = handle_match.group(1)
    handle = handle_match.group(2)

    # Search for the item by handle via the discover API
    try:
        search_resp = requests.get(
            f"{base_url}/server/api/discover/search/objects",
            params={"query": f"handle:{handle}"},
            headers={"Accept": "application/json"},
            timeout=15,
        )
        if search_resp.status_code != 200:
            logger.warning(f"DSpace 7 discover API returned {search_resp.status_code} for {resolved_url}")
            return None

        search_data = search_resp.json()
        objects = (search_data
                   .get("_embedded", {})
                   .get("searchResult", {})
                   .get("_embedded", {})
                   .get("objects", []))
        if not objects:
            logger.warning(f"DSpace 7 discover API returned no results for handle {handle}")
            return None

        item = objects[0].get("_embedded", {}).get("indexableObject", {})
        metadata = item.get("metadata", {})
    except Exception as e:
        logger.error(f"DSpace 7 REST API error for {resolved_url}: {e}")
        return None

    # Build HTML with citation_* meta tags
    meta_tags = []

    # Title
    for t in metadata.get("dc.title", []):
        meta_tags.append(f'<meta name="citation_title" content="{_esc(t["value"])}">')

    # Authors
    for a in metadata.get("dc.contributor.author", []):
        meta_tags.append(f'<meta name="citation_author" content="{_esc(a["value"])}">')

    # Abstract
    for ab in metadata.get("dc.description.abstract", []):
        meta_tags.append(f'<meta name="description" content="{_esc(ab["value"])}">')

    # DOI
    for doi in metadata.get("dc.identifier.doi", []):
        meta_tags.append(f'<meta name="citation_doi" content="{_esc(doi["value"])}">')

    # Date
    for d in metadata.get("dc.date.issued", []):
        meta_tags.append(f'<meta name="citation_date" content="{_esc(d["value"])}">')

    # Language
    for lang in metadata.get("dc.language.iso", []):
        meta_tags.append(f'<meta name="citation_language" content="{_esc(lang["value"])}">')

    # Journal / source
    for src in metadata.get("source.periodicalTitle", []):
        meta_tags.append(f'<meta name="citation_journal_title" content="{_esc(src["value"])}">')

    # Publisher
    for pub in metadata.get("source.publisher", []) or metadata.get("dc.publisher", []):
        meta_tags.append(f'<meta name="citation_publisher" content="{_esc(pub["value"])}">')

    # ISSN
    for issn in metadata.get("source.identifier.issn", []):
        meta_tags.append(f'<meta name="citation_issn" content="{_esc(issn["value"])}">')

    # Volume / issue / pages
    for vol in metadata.get("source.bibliographicInfo.volume", []):
        meta_tags.append(f'<meta name="citation_volume" content="{_esc(vol["value"])}">')
    for iss in metadata.get("source.bibliographicInfo.issue", []):
        meta_tags.append(f'<meta name="citation_issue" content="{_esc(iss["value"])}">')
    for fp in metadata.get("source.bibliographicInfo.firstPage", []):
        meta_tags.append(f'<meta name="citation_firstpage" content="{_esc(fp["value"])}">')
    for lp in metadata.get("source.bibliographicInfo.lastPage", []):
        meta_tags.append(f'<meta name="citation_lastpage" content="{_esc(lp["value"])}">')

    # License / rights
    for rights in metadata.get("dc.rights", []):
        meta_tags.append(f'<meta name="dc.rights" content="{_esc(rights["value"])}">')
    for rights_uri in metadata.get("dc.rights.uri", []):
        meta_tags.append(f'<meta name="dc.rights.uri" content="{_esc(rights_uri["value"])}">')

    # Canonical URL
    meta_tags.append(f'<link rel="canonical" href="{_esc(resolved_url)}">')

    # Try to get PDF bitstream URL
    bundles_url = item.get("_links", {}).get("bundles", {}).get("href")
    if bundles_url:
        try:
            bundles_resp = requests.get(
                bundles_url,
                headers={"Accept": "application/json"},
                timeout=10,
            )
            if bundles_resp.status_code == 200:
                bundles = bundles_resp.json().get("_embedded", {}).get("bundles", [])
                for bundle in bundles:
                    if bundle.get("name") == "ORIGINAL":
                        bitstreams_url = bundle.get("_links", {}).get("bitstreams", {}).get("href")
                        if bitstreams_url:
                            bs_resp = requests.get(
                                bitstreams_url,
                                headers={"Accept": "application/json"},
                                timeout=10,
                            )
                            if bs_resp.status_code == 200:
                                for bs in bs_resp.json().get("_embedded", {}).get("bitstreams", []):
                                    fmt = bs.get("format", "")
                                    name = bs.get("name", "")
                                    if name.lower().endswith(".pdf") or "pdf" in str(fmt).lower():
                                        content_url = bs.get("_links", {}).get("content", {}).get("href")
                                        if content_url:
                                            meta_tags.append(f'<meta name="citation_pdf_url" content="{_esc(content_url)}">')
                                            break
        except Exception as e:
            logger.warning(f"DSpace 7 bitstream lookup failed for {resolved_url}: {e}")

    meta_block = "\n".join(meta_tags)
    title = metadata.get("dc.title", [{}])[0].get("value", "") if metadata.get("dc.title") else ""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{_esc(title)}</title>
{meta_block}
</head>
<body>
<!-- Synthesized from DSpace 7 REST API -->
</body>
</html>"""


def _esc(text):
    """Escape text for safe inclusion in HTML attribute values."""
    if not text:
        return ""
    return (text
            .replace("&", "&amp;")
            .replace('"', "&quot;")
            .replace("<", "&lt;")
            .replace(">", "&gt;"))


def before_retry(retry_state):
    redirected_url = retry_state.outcome.result().url
    logger.info(f"retrying due to {retry_state.outcome.result().status_code}")
    retry_state.kwargs['redirected_url'] = redirected_url
    retry_state.kwargs['attempt_n'] = retry_state.attempt_number


def is_retry_status(response):
    return response.status_code in {429, 500, 502, 503}


@retry(stop=stop_after_attempt(2),
       wait=wait_exponential(multiplier=1, min=4, max=10),
       retry=retry_if_result(is_retry_status),
       before_sleep=before_retry)
def http_get(url,
             headers=None,
             read_timeout=60,
             connect_timeout=60,
             stream=False,
             publisher=None,
             session_id=None,
             ask_slowly=False,
             verify=False,
             cookies=None,
             redirected_url=None,
             attempt_n=0):
    """
    Unified function that handles both DOI resolution and Zyte API calls.
    """
    headers = headers or {}
    start_time = time()
    os.environ["HTTP_PROXY"] = ""

    # Use redirected URL if provided (from retry mechanism)
    if redirected_url:
        logger.info(f"Using redirected URL: {redirected_url}")
        url = redirected_url

    try:
        logger.info(f"LIVE GET on {url}")

        # Check if it's a DOI or Handle URL that needs resolution
        is_doi_url = 'doi.org/' in url
        is_handle_url = 'hdl.handle.net/' in url

        if (is_doi_url or is_handle_url) and not attempt_n:  # Only resolve on first attempt
            logger.info(f"Resolving {'DOI' if is_doi_url else 'Handle'} URL: {url}")
            redirect_info = resolve_doi_redirects(url)

            if redirect_info and redirect_info["status_code"] < 400:
                url = redirect_info["final_url"]
                logger.info(f"Resolved to: {url}")

        # Direct fetch for open-access sites that don't need Zyte
        if is_direct_fetch_url(url):
            logger.info(f"Direct fetch (bypassing Zyte) for {url}")
            try:
                direct_resp = requests.get(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
                    timeout=(connect_timeout, read_timeout),
                    verify=verify,
                )
                r = ResponseObject(
                    content=direct_resp.content,
                    headers=[{"name": k, "value": v} for k, v in direct_resp.headers.items()],
                    status_code=direct_resp.status_code,
                    url=direct_resp.url,
                )
                if not isinstance(r.content, bytes) or not r.content.startswith(b'%PDF-'):
                    try:
                        r.content = r.content.decode('utf-8', 'ignore') if isinstance(r.content, bytes) else r.content
                    except (UnicodeDecodeError, AttributeError):
                        pass
                # DSpace 7 without server-side rendering returns a bare Angular
                # SPA shell (`<ds-app></ds-app>`) with no metadata.  Some
                # DSpace 7 instances use Angular Universal (SSR) and include
                # full content — we only intercept the empty shell case.
                if (isinstance(r.content, str)
                        and '<ds-app>' in r.content
                        and '</ds-app>' in r.content
                        and len(r.content) < 2000):
                    synthesized = _fetch_dspace7_metadata(r.url)
                    if synthesized:
                        logger.info(f"DSpace 7 SPA detected at {r.url}, synthesized HTML from REST API")
                        r.content = synthesized
                return r
            except requests.exceptions.RequestException as e:
                logger.error(f"Direct fetch failed for {url}: {e}, falling back to Zyte")

        # Set up Zyte API parameters
        zyte_params = {
            "url": url,
            "httpResponseBody": True,
            "httpResponseHeaders": True,
        }

        # Check if URL is likely a PDF
        is_likely_pdf_url = url.lower().endswith('.pdf') or '/pdf/' in url.lower()

        # Special handling for PMC PDFs that need JavaScript to bypass challenges
        is_pmc_pdf = ('ncbi.nlm.nih.gov' in url or 'pmc.ncbi.nlm.nih.gov' in url) and is_likely_pdf_url

        if is_pmc_pdf:
            logger.info(f"Using browserHtml with httpResponseBody for PMC PDF: {url}")
            zyte_params["browserHtml"] = True
            zyte_params["httpResponseBody"] = True
            zyte_params["javascript"] = True
        elif is_browser_html_url(url) and not is_likely_pdf_url:
            logger.info(f"Setting browserHtml to True and javascript to True for {url}")
            zyte_params["browserHtml"] = True
            zyte_params["httpResponseBody"] = False
            zyte_params["javascript"] = True

        if is_browser_html_url(url) or is_pmc_pdf:
            # Apply site-specific settings
            if 'saemobilus.sae.org/articles' in url:
                zyte_params["actions"] = [{"action": "waitForSelector",
                                           "selector": {"type": "css", "state": "visible", "value": "#itemDnlBtn"}}]
            elif '10.1016/j.physletb' in url:
                zyte_params["actions"] = [
                    {"action": "waitForSelector",
                     "selector": {"type": "css", "state": "visible", "value": "#show-more-btn"}},
                    {"action": "click", "selector": {"type": "css", "value": "#show-more-btn"}},
                    {"action": "waitForSelector", "timeout": 15,
                     "selector": {"type": "css", "state": "visible",
                                  "value": "div.author-collaboration div.author-group"}}]
            elif 'sciencedirect.com/science/article' in url or 'linkinghub.elsevier.com/retrieve/pii' in url:
                zyte_params["actions"] = [
                    {"action": "evaluate",
                     "source": '(function(){ var btn = document.getElementById("show-more-btn"); if(btn) btn.click(); })()'},
                    {"action": "waitForTimeout", "timeout": 5}]
            elif 'adsabs.harvard.edu' in url:
                zyte_params["actions"] = [
                    {"action": "waitForSelector",
                     "selector": {"type": "css", "state": "visible", "value": "#toggle-aff"}},
                    {"action": "click", "selector": {"type": "css", "value": "#toggle-aff"}},
                    {"action": "waitForSelector", "timeout": 15,
                     "selector": {"type": "css", "state": "visible", "value": "span.affiliation"}}]
            elif 'doi.org/10.2196' in url:
                zyte_params["actions"] = [
                    {"action": "waitForSelector",
                     "selector": {"type": "css", "state": "visible", "value": "#toggle-aff"}},
                    {"action": "click", "selector": {"type": "css", "value": "#toggle-aff"}},
                    {"action": "waitForSelector", "timeout": 15,
                     "selector": {"type": "css", "state": "visible", "value": "span.affiliation"}}]
            elif '10.1103/physrevc' in url:
                zyte_params["actions"] = [{"action": "waitForSelector",
                                           "selector": {"type": "css", "state": "visible",
                                                        "value": "section.authors div.help-message"}},
                                          {"action": "click",
                                           "selector": {"type": "css", "value": "section.authors div.help-message"}},
                                          {"action": "waitForSelector", "timeout": 15,
                                           "selector": {"type": "css", "state": "visible",
                                                        "value": "section.authors ul li"}}]
            elif 'medsciencegroup.us' in url:
                zyte_params["requestCookies"] = [
                    {"name": "queryhead1", "value": "true", "domain": "medsciencegroup.us"}]

        # Make the API call
        zyte_api_response = call_with_zyte_api(url, zyte_params)
        good_status_code = zyte_api_response.get('statusCode')
        bad_status_code = zyte_api_response.get('status')

        if good_status_code is not None and good_status_code < 400:
            logger.info(f"Zyte API good status code for {url}: {good_status_code}")

            headers = zyte_api_response.get('httpResponseHeaders', [])

            content = None
            if 'httpResponseBody' in zyte_api_response:
                content = b64decode(zyte_api_response.get('httpResponseBody'))
            elif 'browserHtml' in zyte_api_response:
                content = zyte_api_response.get('browserHtml').encode()
            else:
                content = b''

            # Create response object
            r = ResponseObject(
                content=content,
                headers=headers,
                status_code=good_status_code,
                url=zyte_api_response.get('url', url),
            )

            # Check if content is PDF by signature first (most reliable)
            is_pdf = False
            if isinstance(r.content, bytes) and len(r.content) > 4:
                is_pdf = r.content.startswith(b'%PDF-')

            # Also check Content-Type header as backup
            if not is_pdf:
                content_type = r.headers.get("Content-Type", "").lower()
                is_pdf = "application/pdf" in content_type

            # Only decode to UTF-8 if it's definitely not a PDF
            if not is_pdf and isinstance(r.content, bytes):
                try:
                    r.content = r.content.decode('utf-8', 'ignore')
                except (UnicodeDecodeError, AttributeError):
                    # Keep as binary if decoding fails
                    pass

            # Check for doi.org chooser redirects
            redirect_url = chooser_redirect(r)
            if redirect_url:
                logger.info(f"Following chooser redirect to {redirect_url}")

                # Recursively follow the redirect
                return http_get(
                    url=redirect_url,
                    headers=headers,
                    read_timeout=read_timeout,
                    connect_timeout=connect_timeout,
                    stream=stream,
                    publisher=publisher,
                    session_id=session_id,
                    ask_slowly=ask_slowly,
                    verify=verify,
                    cookies=cookies,
                    attempt_n=attempt_n
                )

            return r
        else:
            # Create a response for error cases
            r = ResponseObject(
                content='',
                headers=[],
                status_code=bad_status_code or 500,  # Use 500 as fallback
                url=url,
            )
            logger.info(f"Zyte API bad status code for {url}: {bad_status_code}")
            return r

    except Exception as e:
        logger.error(f"Error in http_get for {url}: {str(e)}")
        raise

    finally:
        logger.info(f"Finished http_get for {url} in {elapsed(start_time, 2)} seconds")


COOKIE_DOMAINS = [
    "iop.org",
    "wiley.com",
]


def _needs_cookie_fetch(url):
    """Check if URL needs the two-step cookie approach."""
    # PMC PDFs
    if ("ncbi.nlm.nih.gov" in url or "pmc.ncbi.nlm.nih.gov" in url) and (".pdf" in url or "/pdf/" in url):
        return True
    return any(domain in url for domain in COOKIE_DOMAINS)


def _fetch_with_cookies(url, zyte_api_url, zyte_api_key, fallback_params):
    """Fetch with browser to bypass bot protection. Uses the browser response
    directly if it has valid HTML content, otherwise gets cookies and makes a
    second request (needed for PDFs and some publishers)."""
    logger.info(f"getting cookies for {url}")
    browser_response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                     json={
                                         "url": url,
                                         "browserHtml": True,
                                         "javascript": True,
                                         "experimental": {
                                             "responseCookies": True
                                         }
                                     }, verify=False)
    browser_data = json.loads(browser_response.text)
    browser_html = browser_data.get("browserHtml", "")
    cookies = browser_data.get("experimental", {}).get("responseCookies", {})

    # If browser response has valid HTML content, use it directly
    is_pdf_url = url.lower().endswith('.pdf') or '/pdf/' in url.lower()
    if browser_html and not is_pdf_url and '<title>Radware Bot Manager' not in browser_html:
        logger.info(f"Using browser HTML directly for {url}")
        return browser_response

    # Otherwise use cookies for a second request (PDFs, challenge pages)
    if cookies:
        logger.info(f"Using cookies for second request to {url}")
        return requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                             json={
                                 "url": url,
                                 "httpResponseHeaders": True,
                                 "httpResponseBody": True,
                                 "experimental": {
                                     "requestCookies": cookies
                                 }
                             }, verify=False)
    else:
        logger.info(f"No cookies returned for {url}, using standard request")
        return requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                             json=fallback_params, verify=False)


def call_with_zyte_api(url, params=None):
    zyte_api_url = "https://api.zyte.com/v1/extract"
    zyte_api_key = os.getenv("ZYTE_API_KEY")
    default_params = {
        "url": url,
        "httpResponseHeaders": True,
        "httpResponseBody": True,
        "requestHeaders": {"referer": "https://www.google.com/"},
    }
    if not params:
        params = default_params
    params['url'] = url
    os.environ["HTTP_PROXY"] = ''
    os.environ["HTTPS_PROXY"] = ''

    logger.info(f"calling zyte api for {url}")

    if _needs_cookie_fetch(url):
        response = _fetch_with_cookies(url, zyte_api_url, zyte_api_key, params)
    else:
        response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                 json=params, verify=False)
    return response.json()


def get_cookies_with_zyte_api(url):
    zyte_api_url = "https://api.zyte.com/v1/extract"
    cookies_response = requests.post(zyte_api_url, auth=(ZYTE_API_KEY, ''),
                                     json={
                                         "url": url,
                                         "browserHtml": True,
                                         "javascript": True,
                                         "experimental": {
                                             "responseCookies": True
                                         }
                                     })
    cookies_response = json.loads(cookies_response.text)
    cookies = cookies_response.get("experimental", {}).get("responseCookies",
                                                           {})
    return cookies
