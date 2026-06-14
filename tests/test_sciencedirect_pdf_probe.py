import unittest

from scripts.sciencedirect_pdf_probe import (
    build_sciencedirect_pdf_variants,
    extract_sciencedirect_pii,
    sanitize_url,
)


class ScienceDirectPdfProbeTests(unittest.TestCase):
    def test_sanitize_url_drops_query_and_fragment(self):
        self.assertEqual(
            sanitize_url("https://www.sciencedirect.com/science/article/pii/S123/pdf?hash=secret#frag"),
            "https://www.sciencedirect.com/science/article/pii/S123/pdf",
        )

    def test_extracts_pii_from_sciencedirect_article_route(self):
        self.assertEqual(
            extract_sciencedirect_pii("https://www.sciencedirect.com/science/article/pii/S0011916424005289/pdfft"),
            "S0011916424005289",
        )

    def test_extracts_pii_from_sciencedirect_am_route(self):
        self.assertEqual(
            extract_sciencedirect_pii("https://www.sciencedirect.com/science/article/am/pii/S0168192322004890"),
            "S0168192322004890",
        )

    def test_extracts_pii_from_first_page_pdf_route(self):
        self.assertEqual(
            extract_sciencedirect_pii(
                "https://www.sciencedirect.com/sdfe/pdf/download/eid/1-s2.0-003306209390027B/first-page-pdf"
            ),
            "003306209390027B",
        )

    def test_extracts_pii_from_pdf_asset_path_without_query(self):
        self.assertEqual(
            extract_sciencedirect_pii(
                "https://pdf.sciencedirectassets.com/271370/1-s2.0-S0011916424X00132/"
                "1-s2.0-S0011916424005289/main.pdf"
            ),
            "S0011916424005289",
        )

    def test_builds_sanitized_article_pdf_variants(self):
        variants = build_sciencedirect_pdf_variants(
            "https://www.sciencedirect.com/science/article/pii/S0011916424005289/pdfft?download=true"
        )
        self.assertEqual(
            variants,
            [
                {
                    "name": "candidate",
                    "url": "https://www.sciencedirect.com/science/article/pii/S0011916424005289/pdfft",
                },
                {
                    "name": "article",
                    "url": "https://www.sciencedirect.com/science/article/pii/S0011916424005289",
                },
                {
                    "name": "pdf",
                    "url": "https://www.sciencedirect.com/science/article/pii/S0011916424005289/pdf",
                },
            ],
        )


if __name__ == "__main__":
    unittest.main()
