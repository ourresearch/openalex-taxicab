import json
import tempfile
import unittest
from pathlib import Path

from openalex_taxicab.pdf_eval_harness import (
    PDF_CATEGORIES,
    PDF_CATEGORY_GOOD_PDF,
    PDF_CATEGORY_HTML_INSTEAD_OF_PDF,
    PDF_CATEGORY_NO_PDF_EXPECTED,
    PdfEvidence,
    classify_pdf_content,
    make_pdf_transport_row,
    summarize_pdf_rows,
    write_pdf_artifacts,
)
from scripts.taxicab_pdf_eval import main


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "pdf"


class PdfEvalHarnessTests(unittest.TestCase):
    def classify_fixture(self, item):
        return classify_pdf_content(
            PdfEvidence(
                doi=item.get("doi", f"fixture/{item['file']}"),
                work_id=item.get("work_id", ""),
                title=item.get("title", ""),
                publisher=item.get("publisher", "fixture"),
                candidate_url=item.get("candidate_url", ""),
                content_type=item.get("content_type", ""),
                body=(FIXTURE_DIR / item["file"]).read_bytes(),
                pdf_expected=item.get("pdf_expected", True),
                status_code=item.get("status_code", 200),
                mode="fixture",
            ),
            run_id="test",
        )

    def test_manifest_fixtures_match_expected_categories(self):
        manifest = json.loads((FIXTURE_DIR / "manifest.json").read_text())
        for item in manifest["fixtures"]:
            with self.subTest(item=item["file"]):
                row = self.classify_fixture(item)
                self.assertEqual(row.category, item["expected"])

    def test_valid_pdf_records_validation_signals(self):
        item = {
            "file": "valid_fulltext.pdf",
            "doi": "10.5555/goodpdf",
            "title": "Example Full Text Article",
            "content_type": "application/pdf",
        }
        row = self.classify_fixture(item)
        self.assertEqual(row.category, PDF_CATEGORY_GOOD_PDF)
        self.assertTrue(row.pdf_magic)
        self.assertGreater(row.page_count, 0)
        self.assertTrue(row.doi_match)
        self.assertGreater(row.title_overlap, 0)

    def test_no_pdf_expected_short_circuits_content(self):
        row = classify_pdf_content(
            PdfEvidence(
                doi="10.5555/no-pdf",
                title="No PDF",
                body=b"<html><body>not a pdf</body></html>",
                content_type="text/html",
                pdf_expected=False,
            ),
            run_id="test",
        )
        self.assertEqual(row.category, PDF_CATEGORY_NO_PDF_EXPECTED)

    def test_html_without_specific_interstitial_is_html_instead_of_pdf(self):
        row = classify_pdf_content(
            PdfEvidence(
                doi="10.5555/html",
                title="HTML",
                body=b"<html><body><p>Article landing page instead of PDF.</p></body></html>",
                content_type="text/html",
            ),
            run_id="test",
        )
        self.assertEqual(row.category, PDF_CATEGORY_HTML_INSTEAD_OF_PDF)

    def test_summary_uses_pdf_expected_denominator(self):
        rows = [
            self.classify_fixture(
                {
                    "file": "valid_fulltext.pdf",
                    "doi": "10.5555/goodpdf",
                    "title": "Example Full Text Article",
                    "content_type": "application/pdf",
                }
            ),
            classify_pdf_content(PdfEvidence(doi="10.5555/no-pdf", pdf_expected=False), run_id="test"),
            make_pdf_transport_row(
                run_id="test",
                doi="10.5555/html",
                category=PDF_CATEGORY_HTML_INSTEAD_OF_PDF,
                error="html returned instead of pdf",
            ),
        ]
        summary = summarize_pdf_rows(rows, run_id="test")
        self.assertEqual(summary["total"], 3)
        self.assertEqual(summary["pdf_expected_total"], 2)
        self.assertEqual(summary["good_pdf"], 1)
        self.assertEqual(sum(summary["category_counts"].values()), 3)

    def test_write_artifacts(self):
        rows = [
            self.classify_fixture(
                {
                    "file": "valid_fulltext.pdf",
                    "doi": "10.5555/goodpdf",
                    "title": "Example Full Text Article",
                    "content_type": "application/pdf",
                }
            )
        ]
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_pdf_artifacts(rows, Path(tmp), run_id="test")
            for path in paths.values():
                self.assertTrue(path.exists())

    def test_fixture_smoke_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = main(["--fixture-smoke", "--run-id", "pdf-fixture-test", "--out", tmp])
            self.assertEqual(code, 0)
            run_dir = Path(tmp) / "pdf-fixture-test"
            self.assertTrue((run_dir / "rows.ndjson").exists())
            self.assertTrue((run_dir / "summary.json").exists())
            self.assertTrue((run_dir / "hardness.json").exists())
            self.assertTrue((run_dir / "report.html").exists())

    def test_all_pdf_categories_are_represented_by_fixture_smoke(self):
        manifest = json.loads((FIXTURE_DIR / "manifest.json").read_text())
        represented = set()
        for item in manifest["fixtures"]:
            represented.add(self.classify_fixture(item).category)
        for item in manifest["synthetic_rows"]:
            represented.add(item["expected"])
        self.assertEqual(set(PDF_CATEGORIES), represented)


if __name__ == "__main__":
    unittest.main()
