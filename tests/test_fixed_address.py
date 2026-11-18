"""Repositories that allowlist our fixed address get their pages fetched from it first (oxjob #2381)."""
import base64
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

from openalex_taxicab import deadline, fixed_address
from openalex_taxicab.http_cache import http_get

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


if __name__ == "__main__":
    unittest.main()
