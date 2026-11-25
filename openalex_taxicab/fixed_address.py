"""Page checks from our fixed address, for repositories that allowlist it (oxjob #2381).

Some repositories show every bot a wall (Cloudflare, Anubis, "confirm you are human") on their record and file pages,
so we can't confirm their open copies. We ask them to allowlist the address and User-Agent our OAI-PMH harvester
already uses (44.208.99.237, published on help.openalex.org/how-to/repositories/). That only helps if the page
checks come from that address too; through Zyte they come from addresses we can't name.

So for a URL on a listed repository (fixed_address_hosts.txt), the harvester first fetches the page itself through
the harvester's proxy (STATIC_IP_PROXY: Squid at harvester-proxy.openalex.org, exit 44.208.99.237) with the
harvester's User-Agent. If the site still answers with a wall or a refusal (it hasn't allowlisted us yet), the
fetch falls through to the usual route, so listing a repository never loses a page we would have got. A refused
site is skipped for an hour, so a site that hasn't let us through yet doesn't get two requests for every page.
"""
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import certifi
import requests
from requests.adapters import HTTPAdapter

from openalex_taxicab import page_class

USER_AGENT = 'OpenAlexHarvester/1.0 (+https://help.openalex.org/how-to/repositories/; mailto:support@openalex.org)'
LIST_FILE = Path(__file__).with_name('fixed_address_hosts.txt')
# Answers that mean "not let through": the site hasn't allowlisted us (or our proxy refused); try the usual route.
REFUSED = {202, 401, 403, 407, 429}
REFUSED_FOR_SECONDS = 3600
# The attempt's share of the 55 s request budget. Walls answer fast, so the first byte gets 30 s: some repository
# servers take 10-20 s to start a record page or file, and the usual route behind a listed site is usually walled,
# so a timeout there loses the page (oxjob #2381).
CONNECT_SECONDS, FIRST_BYTE_SECONDS = 5, 30


def _strip_www(host):
    return host[4:] if host.startswith('www.') else host


def _load(path=LIST_FILE):
    """One host per line (it covers its subdomains); `#` starts a comment."""
    hosts = set()
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.split('#', 1)[0].strip().lower()
            if line:
                hosts.add(_strip_www(line.split('://', 1)[-1].split('/', 1)[0]))
    return frozenset(hosts)


HOSTS = _load()
_refused_until = {}  # host -> time; plain dict reads and writes are atomic under the GIL


def _host(url):
    return _strip_www((urlparse(url if '://' in url else 'http://' + url).hostname or '').lower())


def is_listed(url):
    """The URL's host or one of its parent domains is on the list (a set lookup per label, not a scan)."""
    labels = _host(url).split('.') if url else []
    return any('.'.join(labels[i:]) in HOSTS for i in range(len(labels) - 1))


def usable(url):
    """True when this URL should be tried from the fixed address first."""
    if not os.environ.get('STATIC_IP_PROXY') or not is_listed(url):
        return False
    return _refused_until.get(_host(url), 0) < time.time()


def mark_refused(url):
    _refused_until[_host(url)] = time.time() + REFUSED_FOR_SECONDS


def let_through(status_code, page_kind):
    """Keep the fixed-address answer only when it is the site's real answer: a page or file, or a plain 404/410.
    Anything else uses the usual route: walls and refusals (the site hasn't allowlisted us yet), 5xx (Squid answers
    502/503 when it can't reach the site), and logins or empty app shells, which the usual route's browser render
    may get past."""
    if status_code in REFUSED or status_code >= 500:
        return False
    if page_kind == 'error':
        return status_code in (404, 410)
    return page_kind not in page_class.NOT_STORED


class _ProxyVerifyingAdapter(HTTPAdapter):
    """requests verifies an https:// proxy's certificate only for https:// targets; for http:// targets it connects to
    the proxy unverified, so a man in the middle could read the proxy password. Verify it for those too (as
    openalex-ingest's harvester does, oxjob #1604)."""

    def cert_verify(self, conn, url, verify, cert):
        super().cert_verify(conn, url, verify, cert)
        if not url.lower().startswith('https') and getattr(conn, 'scheme', None) == 'https':
            conn.cert_reqs = 'CERT_REQUIRED'
            conn.ca_certs = certifi.where()


# One adapter for every fetch, so connections to the proxy are pooled; urllib3's pools are thread-safe, a shared
# Session isn't documented to be, so each fetch gets its own Session on this adapter.
_ADAPTER = _ProxyVerifyingAdapter(pool_connections=20, pool_maxsize=50)


def session():
    s = requests.Session()
    s.mount('http://', _ADAPTER)
    s.mount('https://', _ADAPTER)
    return s


def proxies():
    p = os.environ.get('STATIC_IP_PROXY', '')
    return {'http': p, 'https': p}
