import json
import tempfile
import unittest
from pathlib import Path

from scripts.sciencedirect_pdf_probe import (
    build_sciencedirect_pdf_variants,
    extract_sciencedirect_pii,
    sanitize_url,
    write_probe_artifacts,
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

    def test_write_probe_artifacts_uses_best_non_good_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe"
            rows = [
                {
                    "doi": "10.1/a",
                    "variant_name": "candidate",
                    "category": "empty_response",
                    "status_code": 520,
                    "content_type": "",
                    "size_bytes": 0,
                    "variant_url": "https://www.sciencedirect.com/science/article/pii/S123/pdf",
                },
                {
                    "doi": "10.1/a",
                    "variant_name": "article",
                    "category": "html_instead_of_pdf",
                    "status_code": 200,
                    "content_type": "text/html",
                    "size_bytes": 10000,
                    "variant_url": "https://www.sciencedirect.com/science/article/pii/S123",
                },
            ]
            write_probe_artifacts(rows, out, run_id="unit-probe", split_path=Path("split.json"))

            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["recovered_doi_count"], 0)
            self.assertEqual(summary["best_category_counts"], {"html_instead_of_pdf": 1})


if __name__ == "__main__":
    unittest.main()
