import base64
import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

from openalex_taxicab.http_cache import (
    http_get,
    jbc_fulltext_url_from_url,
    sciencedirect_article_url_from_pdf_asset,
)


class ScienceDirectUrlTests(unittest.TestCase):
    def test_http_get_uses_pdf_body_strategy_for_wiley_pdfdirect(self):
        pdf_url = "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ijsw.12017"
        captured = []

        class FakeResponse:
            def json(self):
                return {
                    "statusCode": 200,
                    "url": pdf_url,
                    "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                    "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1111/ijsw.12017")

        self.assertEqual(len(captured), 1)
        self.assertTrue(captured[0]["httpResponseBody"])
        self.assertTrue(captured[0]["httpResponseHeaders"])
        self.assertNotIn("browserHtml", captured[0])
        self.assertEqual(response.url, pdf_url)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_falls_back_for_wiley_pdfdirect_strategies(self):
        pdf_url = "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/jols.12117"
        captured = []
        responses = [
            {"status": 520, "detail": "ban-free response unavailable"},
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>not pdf</html>").decode(),
            },
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1111/jols.12117")

        self.assertEqual(len(captured), 3)
        self.assertNotIn("customHttpRequestHeaders", captured[0])
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "Accept", "value": "application/pdf,*/*"}],
        )
        self.assertEqual(
            captured[2]["customHttpRequestHeaders"],
            [
                {"name": "Accept", "value": "application/pdf,*/*"},
                {"name": "Referer", "value": "https://www.google.com/"},
            ],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_rewrites_jbc_pdf_url_to_fulltext(self):
        self.assertEqual(
            jbc_fulltext_url_from_url("https://www.jbc.org/article/S0021-9258(17)43626-X/pdf"),
            "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext",
        )

    def test_rewrites_jbc_linkinghub_url_to_fulltext(self):
        self.assertEqual(
            jbc_fulltext_url_from_url("https://linkinghub.elsevier.com/retrieve/pii/S002192581743626X"),
            "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext",
        )

    def test_rewrites_jbc_doi_url_to_fulltext(self):
        self.assertEqual(
            jbc_fulltext_url_from_url("https://doi.org/10.1016/s0021-9258(17)43626-x"),
            "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext",
        )

    def test_does_not_rewrite_non_jbc_linkinghub_url(self):
        self.assertIsNone(
            jbc_fulltext_url_from_url("https://linkinghub.elsevier.com/retrieve/pii/S0140673624000012")
        )

    def test_extracts_sciencedirect_article_url_from_query_pii(self):
        url = (
            "https://pdf.sciencedirectassets.com/286905/1-s2.0-S2238785424X00034/"
            "1-s2.0-S2238785424010007/main.pdf?hash=abc&pii=S2238785424010007"
        )

        self.assertEqual(
            sciencedirect_article_url_from_pdf_asset(url),
            "https://www.sciencedirect.com/science/article/pii/S2238785424010007",
        )

    def test_extracts_sciencedirect_article_url_from_pdf_path(self):
        url = (
            "https://pdf.sciencedirectassets.com/784962/3-s2.0-C20210009482/"
            "3-s2.0-B9780323999717050013/main.pdf?hash=abc"
        )

        self.assertEqual(
            sciencedirect_article_url_from_pdf_asset(url),
            "https://www.sciencedirect.com/science/article/pii/B9780323999717050013",
        )

    def test_ignores_non_sciencedirect_pdf_url(self):
        self.assertIsNone(sciencedirect_article_url_from_pdf_asset("https://example.org/article.pdf?pii=S123"))

    def test_http_get_rewrites_sciencedirect_pdf_asset_before_zyte(self):
        pdf_asset_url = (
            "https://pdf.sciencedirectassets.com/271370/1-s2.0-S0011916424X00132/"
            "1-s2.0-S0011916424005289/main.pdf?hash=abc&pii=S0011916424005289"
        )
        article_url = "https://www.sciencedirect.com/science/article/pii/S0011916424005289"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>ScienceDirect article</title>"
                    "<meta name=\"citation_title\" content=\"ScienceDirect article\"></head>"
                    "<body><article>Article landing page HTML.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(pdf_asset_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertEqual(response.url, article_url)
        self.assertIn("ScienceDirect article", response.content)

    def test_http_get_uses_browser_html_for_asme(self):
        article_url = "https://asmedigitalcollection.asme.org/PVP/proceedings/PVP2007/42878/379/324449"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": "https://asmedigitalcollection.asme.org/PVP/proceedings-abstract/PVP2007/42878/379/324449",
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>ASME article</title>"
                    "<meta name=\"citation_title\" content=\"ASME article\"></head>"
                    "<body><article>Article landing page HTML.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(
            response.url,
            "https://asmedigitalcollection.asme.org/PVP/proceedings-abstract/PVP2007/42878/379/324449",
        )
        self.assertIn("ASME article", response.content)

    def test_http_get_uses_browser_html_for_uq_espace(self):
        article_url = "https://espace.library.uq.edu.au/view/UQ:352154"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>UQ eSpace article</title>"
                    "<meta name=\"citation_title\" content=\"UQ eSpace article\"></head>"
                    "<body><article>Rendered repository item.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("UQ eSpace article", response.content)

    def test_http_get_uses_browser_html_for_preprints(self):
        article_url = "https://www.preprints.org/manuscript/202005.0515/v1"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>Preprints article</title>"
                    "<meta name=\"citation_title\" content=\"Preprints article\"></head>"
                    "<body><article>Rendered preprint landing page.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("Preprints article", response.content)

    def test_http_get_rewrites_jbc_linkinghub_to_fulltext_before_zyte(self):
        linkinghub_url = "https://linkinghub.elsevier.com/retrieve/pii/S002192581743626X"
        article_url = "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": (
                    "PGh0bWw+PGhlYWQ+PHRpdGxlPkpCQyBhcnRpY2xlPC90aXRsZT48L2hlYWQ+"
                    "PGJvZHk+PGFydGljbGU+Sm91cm5hbCBvZiBCaW9sb2dpY2FsIENoZW1pc3RyeTwvYXJ0aWNsZT48L2JvZHk+PC9odG1sPg=="
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(linkinghub_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertNotIn("browserHtml", captured["params"])
        self.assertEqual(response.url, article_url)
        self.assertIn("JBC article", str(response.content))

    def test_http_get_uses_browser_html_after_preprints_doi_redirect_even_when_head_403(self):
        doi_url = "https://doi.org/10.20944/preprints202005.0515.v1"
        article_url = "https://www.preprints.org/manuscript/202005.0515/v1"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>Preprints article</title>"
                    "<meta name=\"citation_title\" content=\"Preprints article\"></head>"
                    "<body><article>Rendered preprint landing page.</article></body></html>"
                ),
            }

        with patch(
            "openalex_taxicab.http_cache.resolve_doi_redirects",
            return_value={
                "final_url": article_url,
                "redirect_chain": [doi_url, article_url],
                "status_code": 403,
            },
        ), patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(doi_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("Preprints article", response.content)

    def test_http_get_uses_browser_html_after_mdpi_doi_redirect_even_when_head_403(self):
        doi_url = "https://doi.org/10.3390/app8030428"
        article_url = "https://www.mdpi.com/2076-3417/8/3/428"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>MDPI article</title>"
                    "<meta name=\"citation_title\" content=\"MDPI article\"></head>"
                    "<body><article>Rendered MDPI article with abstract.</article></body></html>"
                ),
            }

        with patch(
            "openalex_taxicab.http_cache.resolve_doi_redirects",
            return_value={
                "final_url": article_url,
                "redirect_chain": [doi_url, article_url],
                "status_code": 403,
            },
        ), patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(doi_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("MDPI article", response.content)


if __name__ == "__main__":
    unittest.main()
