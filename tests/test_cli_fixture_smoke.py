import csv
import json
import os
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from openalex_taxicab.eval_harness import EvalRow
from scripts.taxicab_eval import (
    browserbase_metadata_value,
    collect_browserbase_evidence,
    main,
    read_doi_file,
    row_doi_and_input_url,
    row_publisher,
)


class HangingPostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        time.sleep(10)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, format, *args):
        return


class EmptyLookupHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/taxicab/doi/"):
            body = b'{"html": [], "pdf": [], "grobid": []}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


class DaemonThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


class CliFixtureSmokeTests(unittest.TestCase):
    def test_browserbase_metadata_value_sanitizes_doi(self):
        self.assertEqual(browserbase_metadata_value("10.3390/app8030428"), "10.3390_app8030428")
        self.assertEqual(len(browserbase_metadata_value("x" * 200)), 120)

    def test_doi_file_reads_quarry_candidate_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            queue = Path(tmp) / "browserbase-candidates.csv"
            with queue.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["doi", "category", "publisher", "host", "resolved_url"])
                writer.writeheader()
                writer.writerow(
                    {
                        "doi": "10.3390/app8030428",
                        "category": "router_only",
                        "publisher": "mdpi",
                        "host": "mdpi.com",
                        "resolved_url": "https://www.mdpi.com/2076-3417/8/3/428",
                    }
                )

            rows = read_doi_file(queue)

            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["DOI"], "10.3390/app8030428")
            self.assertEqual(row_doi_and_input_url(rows[0])[1], "https://www.mdpi.com/2076-3417/8/3/428")
            self.assertEqual(row_publisher(rows[0]), "mdpi")

    def test_browserbase_not_configured_records_resolved_target_url(self):
        old_key = os.environ.pop("BROWSERBASE_API_KEY", None)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                row = EvalRow(
                    run_id="test",
                    doi="10.3390/app8030428",
                    category="router_only",
                    publisher="mdpi",
                    host="mdpi.com",
                    input_url="https://doi.org/10.3390/app8030428",
                    resolved_url="https://www.mdpi.com/2076-3417/8/3/428",
                    status_code=200,
                    content_type="text/html",
                    size_bytes=100,
                    title="",
                    evidence_snippet="bm-verify",
                    support_candidate=True,
                    uuid="uuid",
                    html_record_count=1,
                    created_date="",
                    duration_ms=1,
                    mode="read_only",
                    error="",
                )

                evidence = collect_browserbase_evidence(row, evidence_dir=Path(tmp))

                self.assertEqual(evidence["verdict"], "not_configured")
                self.assertEqual(evidence["target_url"], "https://www.mdpi.com/2076-3417/8/3/428")
                self.assertTrue(Path(evidence["evidence_path"]).exists())
        finally:
            if old_key is not None:
                os.environ["BROWSERBASE_API_KEY"] = old_key

    def test_browserbase_session_not_configured_records_mode(self):
        old_key = os.environ.pop("BROWSERBASE_API_KEY", None)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                row = EvalRow(
                    run_id="test",
                    doi="10.3390/app8030428",
                    category="router_only",
                    publisher="mdpi",
                    host="mdpi.com",
                    input_url="https://doi.org/10.3390/app8030428",
                    resolved_url="https://www.mdpi.com/2076-3417/8/3/428",
                    status_code=200,
                    content_type="text/html",
                    size_bytes=100,
                    title="",
                    evidence_snippet="bm-verify",
                    support_candidate=True,
                    uuid="uuid",
                    html_record_count=1,
                    created_date="",
                    duration_ms=1,
                    mode="read_only",
                    error="",
                )

                evidence = collect_browserbase_evidence(row, evidence_dir=Path(tmp), mode="session")

                self.assertEqual(evidence["verdict"], "not_configured")
                self.assertEqual(evidence["mode"], "session")
                self.assertEqual(evidence["target_url"], "https://www.mdpi.com/2076-3417/8/3/428")
                self.assertTrue(Path(evidence["evidence_path"]).exists())
        finally:
            if old_key is not None:
                os.environ["BROWSERBASE_API_KEY"] = old_key

    def test_fixture_smoke_exits_zero_and_writes_artifacts(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = main(["--fixture-smoke", "--run-id", "fixture-test", "--out", tmp])
            self.assertEqual(code, 0)
            run_dir = Path(tmp) / "fixture-test"
            self.assertTrue((run_dir / "rows.ndjson").exists())
            self.assertTrue((run_dir / "summary.json").exists())
            self.assertTrue((run_dir / "hardness.json").exists())
            self.assertTrue((run_dir / "report.html").exists())

    def test_row_timeout_writes_timeout_row_for_hanging_reharvest(self):
        server = DaemonThreadingHTTPServer(("127.0.0.1", 0), HangingPostHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                corpus = Path(tmp) / "corpus.csv"
                with corpus.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["DOI", "Link"])
                    writer.writeheader()
                    writer.writerow({"DOI": "10.5555/hanging", "Link": "https://doi.org/10.5555/hanging"})
                code = main(
                    [
                        "--corpus",
                        str(corpus),
                        "--base-url",
                        base_url,
                        "--out",
                        tmp,
                        "--run-id",
                        "watchdog-test",
                        "--limit",
                        "1",
                        "--workers",
                        "1",
                        "--timeout",
                        "30",
                        "--retries",
                        "0",
                        "--reharvest",
                        "--row-timeout",
                        "1",
                        "--progress-every",
                        "1",
                    ]
                )
                self.assertEqual(code, 0)
                rows_path = Path(tmp) / "watchdog-test" / "rows.ndjson"
                rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["category"], "timeout")
                self.assertIn("wall-clock timeout", rows[0]["error"])
        finally:
            server.shutdown()
            server.server_close()

    def test_doi_file_live_run_uses_candidate_url_and_publisher(self):
        server = DaemonThreadingHTTPServer(("127.0.0.1", 0), EmptyLookupHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base_url = f"http://127.0.0.1:{server.server_port}"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                queue = Path(tmp) / "queue.csv"
                with queue.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.DictWriter(handle, fieldnames=["doi", "publisher", "resolved_url"])
                    writer.writeheader()
                    writer.writerow(
                        {
                            "doi": "10.3390/app8030428",
                            "publisher": "mdpi",
                            "resolved_url": "https://www.mdpi.com/2076-3417/8/3/428",
                        }
                    )
                code = main(
                    [
                        "--doi-file",
                        str(queue),
                        "--base-url",
                        base_url,
                        "--out",
                        tmp,
                        "--run-id",
                        "doi-file-test",
                        "--workers",
                        "1",
                        "--retries",
                        "0",
                    ]
                )
                self.assertEqual(code, 0)
                rows_path = Path(tmp) / "doi-file-test" / "rows.ndjson"
                rows = [json.loads(line) for line in rows_path.read_text().splitlines()]
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["category"], "missing_harvest")
                self.assertEqual(rows[0]["publisher"], "mdpi")
                self.assertEqual(rows[0]["input_url"], "https://www.mdpi.com/2076-3417/8/3/428")
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
