"""The live load balancers (harvester, parseland, grobid) accept only requests that carry the origin key
(oxjob #1782 / #1831, since 2026-10-28). Set OPENALEX_ORIGIN_KEY, or have the databricks CLI logged in."""
import base64
import json
import os
import subprocess


def origin_headers():
    key = os.environ.get("OPENALEX_ORIGIN_KEY", "").strip()
    if not key:
        try:
            out = subprocess.run(["databricks", "secrets", "get-secret", "openalex-harvest", "origin-key", "-o", "json"],
                                 capture_output=True, text=True, timeout=30).stdout
            key = base64.b64decode(json.loads(out)["value"]).decode().strip()
        except Exception:
            key = ""
    return {"X-OpenAlex-Origin-Key": key} if key else {}


HEADER = "X-OpenAlex-Origin-Key"
OUR_HOSTS = {
    "harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com",
    "parseland-load-balancer-667160048.us-east-1.elb.amazonaws.com",
    "grobid-api-load-balancer-1880850154.us-east-1.elb.amazonaws.com",
}


def ours(url):
    from urllib.parse import urlsplit
    return (urlsplit(url).hostname or "") in OUR_HOSTS


def headers_for(url):
    """The origin key header for our load balancers only; {} for any other host (never send the key elsewhere)."""
    return origin_headers() if ours(url) else {}


try:
    import requests

    class OriginKeySession(requests.Session):
        """requests.Session that adds the key only to requests for our load balancers and drops it on a redirect
        to any other host (requests keeps custom headers across redirects)."""

        def __init__(self):
            super().__init__()
            self._origin = origin_headers()

        def prepare_request(self, request):
            prepared = super().prepare_request(request)
            if ours(prepared.url):
                prepared.headers.update(self._origin)
            return prepared

        def rebuild_auth(self, prepared_request, response):
            super().rebuild_auth(prepared_request, response)
            if not ours(prepared_request.url):
                prepared_request.headers.pop(HEADER, None)
except ImportError:  # parseland_webapp.py runs on the standard library only
    pass
