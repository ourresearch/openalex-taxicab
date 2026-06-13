import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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
from scripts.taxicab_pdf_eval import TaxicabClient, classify_live_pdf_row, main


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "pdf"


class PdfLookupHandler(BaseHTTPRequestHandler):
    pdf_body = (FIXTURE_DIR / "valid_fulltext.pdf").read_bytes()

    def do_GET(self):
        if self.path.startswith("/taxicab/doi/10.5555%2Fgoodpdf"):
            body = json.dumps(
                {
                    "html": [],
                    "pdf": [
                        {
                            "id": "pdf-good",
                            "resolved_url": "https://example.org/fulltext.pdf",
                            "created_date": "2026-06-13T00:00:00+00:00",
                        }
                    ],
                    "grobid": [],
                }
            ).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/taxicab/doi/10.5555%2Fmissingpdf"):
            body = b'{"html": [], "pdf": [], "grobid": []}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/taxicab/doi/10.5555%2Fdownload404"):
            body = b'{"html": [], "pdf": [{"id": "pdf-missing", "resolved_url": "https://example.org/missing.pdf"}], "grobid": []}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.startswith("/taxicab/pdf-good"):
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Length", str(len(self.pdf_body)))
            self.end_headers()
            self.wfile.write(self.pdf_body)
            return
        if self.path.startswith("/taxicab/pdf-missing"):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"File not found")
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


class DaemonThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


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

    def test_large_valid_pdf_uses_full_body_for_eof_check(self):
        body = (FIXTURE_DIR / "valid_fulltext.pdf").read_bytes()
        eof_index = body.rfind(b"%%EOF")
        self.assertGreater(eof_index, 0)
        padded = body[:eof_index] + (b"0" * (300 * 1024)) + body[eof_index:]
        row = classify_pdf_content(
            PdfEvidence(
                doi="10.5555/goodpdf",
                title="Example Full Text Article",
                body=padded,
                content_type="application/pdf",
            ),
            run_id="test",
        )
        self.assertEqual(row.category, PDF_CATEGORY_GOOD_PDF)
        self.assertNotIn("missing eof marker", row.validation_errors)

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

    def test_live_pdf_row_reads_taxicab_pdf_record(self):
        server = DaemonThreadingHTTPServer(("127.0.0.1", 0), PdfLookupHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = TaxicabClient(f"http://127.0.0.1:{server.server_port}", timeout=2, retries=0)
            row = classify_live_pdf_row(
                {
                    "DOI": "10.5555/goodpdf",
                    "Link": "https://doi.org/10.5555/goodpdf",
                    "title": "Example Full Text Article",
                },
                client=client,
                run_id="test",
            )
            self.assertEqual(row.category, PDF_CATEGORY_GOOD_PDF)
            self.assertEqual(row.uuid, "pdf-good")
            self.assertEqual(row.pdf_record_count, 1)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    def test_live_pdf_row_missing_and_download_404(self):
        server = DaemonThreadingHTTPServer(("127.0.0.1", 0), PdfLookupHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            client = TaxicabClient(f"http://127.0.0.1:{server.server_port}", timeout=2, retries=0)
            missing = classify_live_pdf_row(
                {"DOI": "10.5555/missingpdf", "Link": "https://doi.org/10.5555/missingpdf"},
                client=client,
                run_id="test",
            )
            download_404 = classify_live_pdf_row(
                {"DOI": "10.5555/download404", "Link": "https://doi.org/10.5555/download404"},
                client=client,
                run_id="test",
            )
            self.assertEqual(missing.category, "missing_pdf_harvest")
            self.assertEqual(download_404.category, "download_404")
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

    def test_pdf_cli_workers_write_expected_summary(self):
        server = DaemonThreadingHTTPServer(("127.0.0.1", 0), PdfLookupHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                doi_file = Path(tmp) / "sample.csv"
                doi_file.write_text(
                    "DOI,Link,title\n"
                    "10.5555/goodpdf,https://doi.org/10.5555/goodpdf,Example Full Text Article\n"
                    "10.5555/missingpdf,https://doi.org/10.5555/missingpdf,\n"
                    "10.5555/download404,https://doi.org/10.5555/download404,\n",
                    encoding="utf-8",
                )
                code = main(
                    [
                        "--base-url",
                        f"http://127.0.0.1:{server.server_port}",
                        "--doi-file",
                        str(doi_file),
                        "--run-id",
                        "pdf-workers-test",
                        "--out",
                        tmp,
                        "--workers",
                        "2",
                        "--timeout",
                        "2",
                        "--retries",
                        "0",
                    ]
                )
                self.assertEqual(code, 0)
                summary = json.loads((Path(tmp) / "pdf-workers-test" / "summary.json").read_text())
                self.assertEqual(summary["total"], 3)
                self.assertEqual(summary["category_counts"][PDF_CATEGORY_GOOD_PDF], 1)
                self.assertEqual(summary["category_counts"]["missing_pdf_harvest"], 1)
                self.assertEqual(summary["category_counts"]["download_404"], 1)
        finally:
            server.shutdown()
            thread.join(timeout=5)
            server.server_close()

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
