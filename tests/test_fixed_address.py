"""Repositories that allowlist our fixed address get their pages fetched from it first (oxjob #2381)."""
import base64
import io
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

import requests

from openalex_taxicab import deadline, fixed_address
from openalex_taxicab.http_cache import _listed_redirect_target, http_get, resolve_doi_redirects

PAGE = b"<html><head><meta name='citation_title' content='A thesis'></head><body>" + b"x" * 5000 + b"</body></html>"
WALL = b"<html><head><title>Just a moment...</title></head><body><script>window._cf_chl_opt={}</script></body></html>"
ENTRIES = ("repositorio.example.pt", "other-repo.example.edu")
PROXY = "https://user:pw@harvester-proxy.example.org:3129"


def answer(url, status=200, content=PAGE):
    resp = MagicMock()
    resp.content = content
    resp.headers = {"Content-Type": "text/html"}
    resp.status_code = status
    resp.url = url
    return resp


def fake_session(resp):
    s = MagicMock()
    s.get.return_value = resp
    return s


def zyte_page(url):
    return {"statusCode": 200, "url": url, "httpResponseHeaders": [],
            "httpResponseBody": base64.b64encode(b"<html><head><title>via zyte</title></head>" + b"y" * 5000 + b"</html>").decode()}


class IsListedTests(unittest.TestCase):
    def test_host_subdomain_and_www(self):
        with patch.object(fixed_address, "HOSTS", frozenset(ENTRIES)):
            self.assertTrue(fixed_address.is_listed("https://repositorio.example.pt/handle/1/2"))
            self.assertTrue(fixed_address.is_listed("https://www.repositorio.example.pt/x"))
            self.assertTrue(fixed_address.is_listed("https://files.repositorio.example.pt/a.pdf"))
            self.assertFalse(fixed_address.is_listed("http://hdl.handle.net/10400.5/12345"))
            self.assertFalse(fixed_address.is_listed("https://notrepositorio.example.pt/x"))
            self.assertFalse(fixed_address.is_listed("https://example.pt/x"))
            self.assertFalse(fixed_address.is_listed(""))

    def test_list_file_parses_comments_and_schemes(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "hosts.txt"
            p.write_text("# comment\nhttps://Repo.Example.edu  # why\n\nwww.other.example.org\n")
            self.assertEqual(fixed_address._load(p), {"repo.example.edu", "other.example.org"})

    def test_shipped_list_loads(self):
        self.assertGreater(len(fixed_address._load()), 100)


class HttpGetRouteTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {"STATIC_IP_PROXY": PROXY})
        self.env.start()
        self.entries = patch.object(fixed_address, "HOSTS", frozenset(ENTRIES))
        self.entries.start()
        fixed_address._refused_until.clear()

    def tearDown(self):
        self.entries.stop()
        self.env.stop()
        fixed_address._refused_until.clear()
        deadline.clear()

    def test_listed_page_comes_from_the_fixed_address_when_let_through(self):
        url = "https://repositorio.example.pt/handle/1/2"
        s = fake_session(answer(url))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=AssertionError("zyte called")):
            r = http_get(url)
        self.assertEqual(r.status_code, 200)
        self.assertIn("A thesis", r.content)
        kwargs = s.get.call_args.kwargs
        self.assertEqual(kwargs["proxies"], {"http": PROXY, "https": PROXY})
        self.assertEqual(kwargs["headers"]["User-Agent"], fixed_address.USER_AGENT)

    def test_a_wall_falls_through_to_the_usual_route(self):
        url = "https://repositorio.example.pt/handle/1/3"
        s = fake_session(answer(url, status=403, content=WALL))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            r = http_get(url)
        self.assertEqual(zyte.call_count, 1)
        self.assertIn("via zyte", r.content)

    def test_a_refused_site_is_skipped_for_an_hour(self):
        url = "https://repositorio.example.pt/handle/1/7"
        s = fake_session(answer(url, status=403, content=WALL))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            http_get(url)
            http_get("https://repositorio.example.pt/handle/1/8")
        self.assertEqual(s.get.call_count, 1)
        self.assertEqual(zyte.call_count, 2)
        self.assertTrue(fixed_address.usable("https://other-repo.example.edu/x"))

    def test_a_wall_off_site_after_a_listed_redirect_does_not_mark_the_repository(self):
        url, off_site = "https://repositorio.example.pt/handle/1/9", "https://publisher.example.org/article/9"
        s = fake_session(answer(off_site, status=403, content=WALL))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            http_get(url)
        self.assertEqual(zyte.call_count, 1)
        self.assertTrue(fixed_address.usable(url))

    def test_a_200_wall_falls_through_too(self):
        url = "https://repositorio.example.pt/handle/1/4"
        s = fake_session(answer(url, status=200, content=WALL))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            http_get(url)
        self.assertEqual(zyte.call_count, 1)

    def test_proxy_error_falls_through(self):
        import requests
        url = "https://repositorio.example.pt/handle/1/5"
        s = MagicMock()
        s.get.side_effect = requests.exceptions.ProxyError("proxy down")
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            http_get(url)
        self.assertEqual(zyte.call_count, 1)

    def test_a_real_404_is_kept(self):
        url = "https://repositorio.example.pt/handle/1/gone"
        s = fake_session(answer(url, status=404, content=b"<html>not found</html>"))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=AssertionError("zyte called")):
            r = http_get(url)
        self.assertEqual(r.status_code, 404)

    def test_a_pdf_stays_bytes(self):
        url = "https://repositorio.example.pt/bitstream/1/2/thesis.pdf"
        s = fake_session(answer(url, content=b"\n \n%PDF-1.7\n" + b"z" * 2000))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=AssertionError("zyte called")):
            r = http_get(url)
        self.assertTrue(r.content.lstrip().startswith(b"%PDF-"))

    def test_an_empty_app_shell_falls_through(self):
        url = "https://repositorio.example.pt/items/abc"
        shell = b"<html><head><title>DSpace</title></head><body><ds-app></ds-app><script src='main.js'></script></body></html>"
        s = fake_session(answer(url, status=200, content=shell))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            http_get(url)
        self.assertEqual(zyte.call_count, 1)

    def test_let_through_rules(self):
        self.assertTrue(fixed_address.let_through(200, "html"))
        self.assertTrue(fixed_address.let_through(200, "pdf"))
        self.assertTrue(fixed_address.let_through(404, "error"))
        self.assertFalse(fixed_address.let_through(200, "bot_wall"))
        self.assertFalse(fixed_address.let_through(200, "login"))
        self.assertFalse(fixed_address.let_through(200, "shell"))
        self.assertFalse(fixed_address.let_through(403, "error"))
        self.assertFalse(fixed_address.let_through(502, "error"))
        self.assertFalse(fixed_address.let_through(500, "error"))

    def test_unlisted_url_never_uses_the_fixed_address(self):
        url = "https://other.example.edu/items/1"
        with patch.object(fixed_address, "session", side_effect=AssertionError("fixed address used")), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            http_get(url)
        self.assertEqual(zyte.call_count, 1)

    def test_no_proxy_configured_means_usual_route(self):
        url = "https://repositorio.example.pt/handle/1/6"
        with patch.dict(os.environ, {"STATIC_IP_PROXY": ""}), \
                patch.object(fixed_address, "session", side_effect=AssertionError("fixed address used")), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=zyte_page(url)) as zyte:
            http_get(url)
        self.assertEqual(zyte.call_count, 1)

    def test_a_handle_that_resolves_onto_a_listed_host_uses_the_fixed_address(self):
        url = "http://hdl.handle.net/10451/999"
        final = "https://repositorio.example.pt/handle/10451/999"
        s = fake_session(answer(final))
        with patch("openalex_taxicab.http_cache.resolve_doi_redirects",
                   return_value={"final_url": final, "status_code": 403, "redirect_chain": [url, final]}), \
                patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=AssertionError("zyte called")):
            r = http_get(url)
        self.assertEqual(s.get.call_args.args[0], final)
        self.assertIn("A thesis", r.content)


def hop(url, status, location=None):
    r = requests.models.Response()
    r.status_code = status
    r.url = url
    r.reason = "x"
    r.headers = requests.structures.CaseInsensitiveDict({"Location": location} if location else {})
    r.raw = io.BytesIO(b"")
    return r


class RedirectLookupTests(unittest.TestCase):
    """A DOI or handle lookup stops before a listed repository; the fixed-address fetch follows the rest."""

    def setUp(self):
        self.env = patch.dict(os.environ, {"STATIC_IP_PROXY": PROXY})
        self.env.start()
        self.entries = patch.object(fixed_address, "HOSTS", frozenset(ENTRIES))
        self.entries.start()
        fixed_address._refused_until.clear()
        self.requested = []

    def tearDown(self):
        self.entries.stop()
        self.env.stop()
        fixed_address._refused_until.clear()
        deadline.clear()

    def lookup(self, url, answers):
        def send(adapter, request, **kwargs):
            self.requested.append(request.url)
            r = answers[request.url]
            r.request = request
            return r
        with patch.object(requests.adapters.HTTPAdapter, "send", send):
            return resolve_doi_redirects(url)

    def test_handle_onto_a_listed_repository_stops_before_requesting_it(self):
        url, listed = "http://hdl.handle.net/10451/999", "https://repositorio.example.pt/handle/10451/999"
        info = self.lookup(url, {url: hop(url, 302, listed)})
        self.assertEqual(self.requested, [url])
        self.assertEqual(info, {"final_url": listed, "redirect_chain": [url, listed], "status_code": 302})

    def test_stops_at_the_first_listed_hop_after_unlisted_ones(self):
        doi, mid = "https://doi.org/10.1/x", "http://id.publisher.example.org/x"
        listed = "https://files.other-repo.example.edu/x.pdf"
        info = self.lookup(doi, {doi: hop(doi, 302, mid), mid: hop(mid, 301, listed)})
        self.assertEqual(self.requested, [doi, mid])
        self.assertEqual(info["final_url"], listed)
        self.assertEqual(info["redirect_chain"], [doi, mid, listed])

    def test_relative_location_on_a_listed_host_still_stops(self):
        url = "http://hdl.handle.net/10451/7"
        info = self.lookup(url, {url: hop(url, 302, "//repositorio.example.pt/handle/10451/7")})
        self.assertEqual(self.requested, [url])
        self.assertEqual(info["final_url"], "http://repositorio.example.pt/handle/10451/7")

    def test_unlisted_chain_is_followed_to_the_end_as_before(self):
        url, mid, end = "https://doi.org/10.2/y", "https://publisher.example.org/y", "https://publisher.example.org/article/y"
        info = self.lookup(url, {url: hop(url, 302, mid), mid: hop(mid, 301, end), end: hop(end, 200)})
        self.assertEqual(self.requested, [url, mid, end])
        self.assertEqual(info, {"final_url": end, "redirect_chain": [url, mid, end], "status_code": 200})

    def test_without_the_proxy_a_listed_repository_is_requested_as_before(self):
        url, listed = "http://hdl.handle.net/10451/8", "https://repositorio.example.pt/handle/10451/8"
        with patch.dict(os.environ, {"STATIC_IP_PROXY": ""}):
            info = self.lookup(url, {url: hop(url, 302, listed), listed: hop(listed, 200)})
        self.assertEqual(self.requested, [url, listed])
        self.assertEqual(info["final_url"], listed)

    def test_a_repository_refusing_the_fixed_address_is_requested_as_before(self):
        url, listed = "http://hdl.handle.net/10451/9", "https://repositorio.example.pt/handle/10451/9"
        fixed_address.mark_refused(listed)
        info = self.lookup(url, {url: hop(url, 302, listed), listed: hop(listed, 403)})
        self.assertEqual(self.requested, [url, listed])
        self.assertEqual(info["status_code"], 403)

    def test_the_stopped_hop_is_closed(self):
        url, listed = "http://hdl.handle.net/10451/12", "https://repositorio.example.pt/handle/10451/12"
        first = hop(url, 302, listed)
        self.lookup(url, {url: first})
        self.assertTrue(first.raw.closed)

    def test_malformed_or_non_web_locations_are_left_to_requests(self):
        s = requests.Session()
        for location in ("http://bad[repositorio.example.pt/x", "ftp://repositorio.example.pt/x", "mailto:a@repositorio.example.pt"):
            self.assertIsNone(_listed_redirect_target(s, hop("http://hdl.handle.net/1/2", 302, location)), location)
        self.assertIsNone(_listed_redirect_target(s, hop("http://hdl.handle.net/1/2", 200)))

    def test_connection_error_still_returns_none(self):
        def send(adapter, request, **kwargs):
            raise requests.exceptions.ConnectionError("refused")
        with patch.object(requests.adapters.HTTPAdapter, "send", send):
            self.assertIsNone(resolve_doi_redirects("http://hdl.handle.net/10451/10"))

    def test_http_get_fetches_the_listed_hop_from_the_fixed_address(self):
        url, listed = "http://hdl.handle.net/10451/11", "https://repositorio.example.pt/handle/10451/11"
        s = fake_session(answer(listed))
        with patch.object(fixed_address, "session", return_value=s), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=AssertionError("zyte called")):
            def send(adapter, request, **kwargs):
                self.requested.append(request.url)
                r = hop(url, 302, listed)
                r.request = request
                return r
            with patch.object(requests.adapters.HTTPAdapter, "send", send):
                r = http_get(url)
        self.assertEqual(self.requested, [url])
        self.assertEqual(s.get.call_args.args[0], listed)
        self.assertIn("A thesis", r.content)


if __name__ == "__main__":
    unittest.main()
