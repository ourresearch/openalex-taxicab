import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

from openalex_taxicab.http_cache import (
    http_get,
    sciencedirect_article_url_from_pdf_asset,
)


class ScienceDirectUrlTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
