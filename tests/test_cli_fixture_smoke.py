import csv
import json
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from scripts.taxicab_eval import main


class HangingPostHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        time.sleep(10)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, format, *args):
        return


class DaemonThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True


class CliFixtureSmokeTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
