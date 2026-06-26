import importlib.util
import json
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "taxicab_batch_e2e.py"
SPEC = importlib.util.spec_from_file_location("taxicab_batch_e2e", MODULE_PATH)
batch_e2e = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(batch_e2e)


class BatchE2ETests(unittest.TestCase):
    def test_parse_parseland_payload_skips_pdfpreview_images(self):
        payload = {
            "urls": [
                {"url": "https://www.jstage.jst.go.jp/pub/pdfpreview/circj/76/8_76_CJ-12-0636.jpg"},
                {"url": "https://example.org/article/full.pdf?download=1#section"},
                {"url": "https://example.org/article/pdfft"},
            ]
        }

        parsed = batch_e2e.parse_parseland_payload(json.dumps(payload).encode("utf-8"))

        self.assertEqual(parsed["parseland_pdf_url_count"], 2)
        self.assertEqual(parsed["parseland_first_pdf_url"], "https://example.org/article/full.pdf")


if __name__ == "__main__":
    unittest.main()
