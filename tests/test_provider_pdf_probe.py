import json
import tempfile
import unittest
from pathlib import Path

from scripts.provider_pdf_probe import (
    filter_records,
    read_input_records,
    sanitize_url,
    strategy_list,
    strategy_params,
    write_probe_artifacts,
)


class ProviderPdfProbeTests(unittest.TestCase):
    def test_sanitize_url_drops_query_and_fragment(self):
        self.assertEqual(
            sanitize_url("https://example.org/full.pdf?download=1&token=secret#page=2"),
            "https://example.org/full.pdf",
        )

    def test_strategy_params_are_expected_zyte_shapes(self):
        url = "https://example.org/full.pdf"
        self.assertEqual(
            strategy_params("default_body", url),
            {"url": url, "httpResponseBody": True, "httpResponseHeaders": True},
        )
        self.assertEqual(
            strategy_params("accept_pdf", url),
            {
                "url": url,
                "httpResponseBody": True,
                "httpResponseHeaders": True,
                "customHttpRequestHeaders": [{"name": "Accept", "value": "application/pdf,*/*"}],
            },
        )
        self.assertEqual(
            strategy_params("browser_html", url),
            {"url": url, "browserHtml": True, "javascript": True},
        )

    def test_strategy_list_validates_unknown_strategy(self):
        self.assertIn("browser_html", strategy_list("all"))
        with self.assertRaises(ValueError):
            strategy_list("default_body,not-a-strategy")

    def test_reads_ndjson_rows_and_filters_missing_cluster(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.ndjson"
            rows = [
                {
                    "doi": "10.1/a",
                    "category": "missing_pdf_harvest",
                    "publisher": "springer",
                    "host": "link.springer.com",
                    "candidate_url": "https://link.springer.com/content/pdf/10.1/a.pdf?download=true",
                },
                {
                    "doi": "10.1/b",
                    "category": "good_pdf",
                    "publisher": "springer",
                    "host": "link.springer.com",
                    "candidate_url": "https://link.springer.com/content/pdf/10.1/b.pdf",
                },
            ]
            path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

            records = read_input_records(path)
            filtered = filter_records(
                records,
                category="missing_pdf_harvest",
                publisher="springer",
                host="link.springer.com",
                limit=10,
            )

            self.assertEqual(len(filtered), 1)
            self.assertEqual(filtered[0].doi, "10.1/a")
            self.assertEqual(filtered[0].candidate_url, "https://link.springer.com/content/pdf/10.1/a.pdf")

    def test_limit_zero_returns_no_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.ndjson"
            path.write_text(
                json.dumps(
                    {
                        "doi": "10.1/a",
                        "category": "missing_pdf_harvest",
                        "publisher": "springer",
                        "host": "link.springer.com",
                        "candidate_url": "https://link.springer.com/content/pdf/10.1/a.pdf",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            records = read_input_records(path)
            self.assertEqual(
                filter_records(
                    records,
                    category="missing_pdf_harvest",
                    publisher="springer",
                    host="link.springer.com",
                    limit=0,
                ),
                [],
            )

    def test_write_probe_artifacts_counts_best_good_per_doi(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe"
            rows = [
                {
                    "doi": "10.1/a",
                    "publisher": "springer",
                    "host": "link.springer.com",
                    "strategy_name": "default_body",
                    "category": "html_instead_of_pdf",
                    "status_code": 200,
                    "content_type": "text/html",
                    "size_bytes": 200,
                    "candidate_url": "https://link.springer.com/content/pdf/10.1/a.pdf",
                },
                {
                    "doi": "10.1/a",
                    "publisher": "springer",
                    "host": "link.springer.com",
                    "strategy_name": "accept_pdf",
                    "category": "good_pdf",
                    "status_code": 200,
                    "content_type": "application/pdf",
                    "size_bytes": 4096,
                    "candidate_url": "https://link.springer.com/content/pdf/10.1/a.pdf",
                },
            ]
            write_probe_artifacts(rows, out, run_id="unit-probe", source_path=Path("rows.ndjson"))

            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["doi_count"], 1)
            self.assertEqual(summary["recovered_doi_count"], 1)
            self.assertEqual(summary["best_category_counts"], {"good_pdf": 1})
            self.assertTrue((out / "rows.ndjson").exists())
            self.assertIn("Recovered DOI count: 1/1", (out / "report.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
