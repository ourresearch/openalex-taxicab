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

BROWSER_HTML_URLS = [
    "cghjournal.org",
    "doi.org/10.1016",
    "elsevier.com",
    "iop.org",
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


def is_browser_html_url(url):
    return any(re.search(f"(^|[./])({re.escape(pattern)})(\/|$)", url)
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


def before_retry(retry_state):
    redirected_url = retry_state.outcome.result().url
    logger.info(f"retrying due to {retry_state.outcome.result().status_code}")
    retry_state.kwargs['redirected_url'] = redirected_url
    retry_state.kwargs['attempt_n'] = retry_state.attempt_number


def is_retry_status(response):
    return response.status_code in {429, 500, 502, 503, 504, 520, 403}


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

        # Check if it's a DOI URL that needs resolution
        is_doi_url = 'doi.org/' in url

        if is_doi_url and not attempt_n:  # Only resolve on first attempt
            logger.info(f"Resolving DOI URL: {url}")
            redirect_info = resolve_doi_redirects(url)

            if redirect_info and redirect_info["status_code"] < 400:
                url = redirect_info["final_url"]
                logger.info(f"DOI resolved to: {url}")

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

    # Special handling for PMC PDFs
    if ("ncbi.nlm.nih.gov" in url or "pmc.ncbi.nlm.nih.gov" in url) and (".pdf" in url or "/pdf/" in url):
        logger.info(f"getting cookies for PMC PDF {url}")
        # First request to solve challenge and get cookies
        cookies_response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                         json={
                                             "url": url,
                                             "browserHtml": True,
                                             "javascript": True,
                                             "experimental": {
                                                 "responseCookies": True
                                             }
                                         }, verify=False)
        cookies_response_data = json.loads(cookies_response.text)
        cookies = cookies_response_data.get("experimental", {}).get("responseCookies", {})

        # Second request with cookies to get actual PDF
        if cookies:
            logger.info(f"Using cookies to fetch PDF: {cookies}")
            response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                     json={
                                         "url": url,
                                         "httpResponseHeaders": True,
                                         "httpResponseBody": True,
                                         "experimental": {
                                             "requestCookies": cookies
                                         }
                                     }, verify=False)
        else:
            logger.info("No cookies returned, using standard request")
            response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                     json=params, verify=False)
    elif "wiley.com" in url:
        # get cookies
        logger.info(f"getting cookies for {url} due to wiley.com")
        cookies_response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                         json={
                                             "url": url,
                                             "browserHtml": True,
                                             "javascript": True,
                                             "experimental": {
                                                 "responseCookies": True
                                             }
                                         }, verify=False)
        cookies_response = json.loads(cookies_response.text)
        cookies = cookies_response.get("experimental", {}).get(
            "responseCookies", {})

        # use cookies to get valid response
        if cookies:
            response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                     json={
                                         "url": url,
                                         "httpResponseHeaders": True,
                                         "httpResponseBody": True,
                                         "experimental": {
                                             "requestCookies": cookies
                                         }
                                     }, verify=False)
        else:
            response = requests.post(zyte_api_url, auth=(zyte_api_key, ''),
                                     json={
                                         "url": url,
                                         "httpResponseHeaders": True,
                                         "httpResponseBody": True,
                                         "requestHeaders": {
                                             "referer": "https://www.google.com/"},
                                     }, verify=False)
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
