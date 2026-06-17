import json
import tempfile
import unittest
from pathlib import Path

from scripts.provider_pdf_probe import (
    filter_records,
    load_recipe_strategies,
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

    def test_recipe_file_adds_provider_advised_strategy(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "recipes.json"
            path.write_text(
                json.dumps(
                    {
                        "strategies": [
                            {
                                "name": "zyte_ticket_pdf_body",
                                "params": {
                                    "url": "{url}",
                                    "httpResponseBody": True,
                                    "httpResponseHeaders": True,
                                    "customHttpRequestHeaders": [
                                        {"name": "Accept", "value": "application/pdf,*/*"},
                                        {"name": "Referer", "value": "{{url}}"},
                                    ],
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            recipes = load_recipe_strategies(path)

            self.assertEqual(strategy_list("zyte_ticket_pdf_body", recipes), ["zyte_ticket_pdf_body"])
            self.assertEqual(
                strategy_list("all", recipes),
                [
                    "default_body",
                    "accept_pdf",
                    "google_referer",
                    "browser_html",
                    "zyte_ticket_pdf_body",
                ],
            )
            self.assertEqual(
                strategy_params(
                    "zyte_ticket_pdf_body",
                    "https://example.org/full.pdf?download=1",
                    recipes,
                ),
                {
                    "url": "https://example.org/full.pdf?download=1",
                    "httpResponseBody": True,
                    "httpResponseHeaders": True,
                    "customHttpRequestHeaders": [
                        {"name": "Accept", "value": "application/pdf,*/*"},
                        {"name": "Referer", "value": "https://example.org/full.pdf?download=1"},
                    ],
                },
            )

    def test_recipe_file_rejects_builtin_shadowing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "recipes.json"
            path.write_text(
                json.dumps(
                    {
                        "strategies": [
                            {"name": "default_body", "params": {"httpResponseBody": True}}
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_recipe_strategies(path)

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
            self.assertEqual(filtered[0].fetch_url, "https://link.springer.com/content/pdf/10.1/a.pdf?download=true")

    def test_reads_query_pdf_urls_with_separate_fetch_and_artifact_urls(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.csv"
            path.write_text(
                "doi,publisher,candidate_url\n"
                "10.1371/journal.pone.example,plos,"
                "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.example&type=printable\n",
                encoding="utf-8",
            )

            records = read_input_records(path)

            self.assertEqual(len(records), 1)
            self.assertEqual(
                records[0].candidate_url,
                "https://journals.plos.org/plosone/article/file",
            )
            self.assertEqual(
                records[0].fetch_url,
                "https://journals.plos.org/plosone/article/file?id=10.1371/journal.pone.example&type=printable",
            )

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

    def test_host_filter_normalizes_www_prefix(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.ndjson"
            path.write_text(
                json.dumps(
                    {
                        "doi": "10.1/a",
                        "category": "missing_pdf_harvest",
                        "publisher": "elsevier",
                        "candidate_url": "https://www.sciencedirect.com/science/article/pii/S123/pdfft",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            records = read_input_records(path)
            filtered = filter_records(
                records,
                category="missing_pdf_harvest",
                publisher="",
                host="www.sciencedirect.com",
                limit=10,
            )

            self.assertEqual(len(filtered), 1)
            self.assertEqual(filtered[0].host, "sciencedirect.com")

    def test_csv_records_classify_publisher_from_pdf_url(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "queue.csv"
            path.write_text(
                "doi,PDF URL\n"
                "10.9999/example,https://www.jstor.org/stable/pdf/jj.9345416.9.pdf\n",
                encoding="utf-8",
            )

            records = read_input_records(path)

            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].publisher, "jstor")
            self.assertEqual(records[0].host, "jstor.org")

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

    def test_write_probe_artifacts_uses_best_non_good_category(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "probe"
            rows = [
                {
                    "doi": "10.1/a",
                    "publisher": "springer",
                    "host": "link.springer.com",
                    "strategy_name": "default_body",
                    "category": "empty_response",
                    "status_code": 520,
                    "content_type": "",
                    "size_bytes": 0,
                    "candidate_url": "https://link.springer.com/content/pdf/10.1/a.pdf",
                },
                {
                    "doi": "10.1/a",
                    "publisher": "springer",
                    "host": "link.springer.com",
                    "strategy_name": "browser_html",
                    "category": "js_redirect_unresolved",
                    "status_code": 200,
                    "content_type": "text/html",
                    "size_bytes": 10000,
                    "candidate_url": "https://link.springer.com/content/pdf/10.1/a.pdf",
                },
            ]
            write_probe_artifacts(rows, out, run_id="unit-probe", source_path=Path("rows.ndjson"))

            summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["recovered_doi_count"], 0)
            self.assertEqual(summary["best_category_counts"], {"js_redirect_unresolved": 1})


if __name__ == "__main__":
    unittest.main()
