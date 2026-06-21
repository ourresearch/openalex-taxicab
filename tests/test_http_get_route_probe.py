import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.http_get_route_probe import (
    classify_route_response,
    header_value,
    is_timeout_exception,
    run_probe,
    write_route_artifacts,
)
from scripts.provider_pdf_probe import ProbeRecord


class FakeResponse:
    def __init__(self, *, content, headers, status_code=200, url="https://dl.acm.org/doi/pdf/10.1145/example"):
        self.content = content
        self.headers = headers
        self.status_code = status_code
        self.url = url


class HttpGetRouteProbeTests(unittest.TestCase):
    def test_header_value_is_case_insensitive(self):
        self.assertEqual(
            header_value({"content-type": "application/pdf"}, "Content-Type"),
            "application/pdf",
        )
        self.assertEqual(
            header_value({"Content-Type": "text/html"}, "content-type"),
            "text/html",
        )

    def test_timeout_exception_detection_covers_retry_text(self):
        self.assertTrue(is_timeout_exception(TimeoutError("timed out")))
        self.assertTrue(is_timeout_exception(RuntimeError("RetryError after timeout")))
        self.assertFalse(is_timeout_exception(RuntimeError("bad json")))

    def test_classify_route_response_preserves_baseline_category(self):
        record = ProbeRecord(
            doi="10.1145/example",
            publisher="acm",
            host="dl.acm.org",
            candidate_url="https://dl.acm.org/doi/pdf/10.1145/example",
            baseline_category="missing_pdf_harvest",
        )
        response = FakeResponse(
            content=b"%PDF-1.7\n1 0 obj<</Type/Page>>endobj\n%%EOF",
            headers={"Content-Type": "application/pdf"},
        )

        row = classify_route_response(record, response, run_id="unit", duration_ms=12)

        self.assertEqual(row["baseline_category"], "missing_pdf_harvest")
        self.assertEqual(row["category"], "good_pdf")
        self.assertEqual(row["duration_ms"], 12)

    def test_write_route_artifacts_are_aggregate_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "route"
            rows = [
                {
                    "doi": "10.1145/a",
                    "baseline_category": "missing_pdf_harvest",
                    "category": "good_pdf",
                    "size_bytes": 4096,
                },
                {
                    "doi": "10.1145/b",
                    "baseline_category": "good_pdf",
                    "category": "html_instead_of_pdf",
                    "size_bytes": 500,
                },
            ]

            write_route_artifacts(rows, out, run_id="unit-route", source_path=Path("rows.ndjson"))
            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            report = (out / "report.html").read_text(encoding="utf-8")

            self.assertEqual(summary["artifact_kind"], "http_get_route_probe_aggregate")
            self.assertFalse(summary["contains_doi_lists"])
            self.assertNotIn("recovered_dois", summary)
            self.assertEqual(summary["prior_non_good_recovered"], 1)
            self.assertEqual(summary["already_good_regressed"], 1)
            self.assertIn("missing_pdf_harvest-&gt;good_pdf", report)
            self.assertNotIn("10.1145/a", report)

    def test_run_probe_calls_http_get_and_writes_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows_path = Path(tmp) / "rows.ndjson"
            fetch_url = "https://scholarhub.ui.ac.id/cgi/viewcontent.cgi?article=1201&context=journal"
            rows_path.write_text(
                json.dumps(
                    {
                        "doi": "10.7454/example",
                        "category": "missing_pdf_harvest",
                        "publisher": "unknown",
                        "host": "scholarhub.ui.ac.id",
                        "candidate_url": fetch_url,
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            out = Path(tmp) / "out"
            args = argparse.Namespace(
                input=str(rows_path),
                category="missing_pdf_harvest",
                publisher="unknown",
                host="scholarhub.ui.ac.id",
                limit=1,
                out=str(out),
                run_id="unit-http-get-route",
                read_timeout=1,
                connect_timeout=1,
                sleep=0,
                env_file="",
            )

            with patch(
                "scripts.http_get_route_probe.http_get",
                return_value=FakeResponse(
                    content=b"%PDF-1.7\n1 0 obj<</Type/Page>>endobj\n%%EOF",
                    headers={"Content-Type": "application/pdf"},
                ),
            ) as mocked:
                self.assertEqual(run_probe(args), 0)

            mocked.assert_called_once()
            self.assertEqual(mocked.call_args.args[0], fetch_url)
            self.assertIn("article=1201", mocked.call_args.args[0])
            summary = json.loads((out / "unit-http-get-route" / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["category_counts"], {"good_pdf": 1})
            self.assertEqual(summary["prior_non_good_recovered"], 1)


if __name__ == "__main__":
    unittest.main()
