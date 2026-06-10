import tempfile
import unittest
from pathlib import Path

from scripts.taxicab_eval import main


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


if __name__ == "__main__":
    unittest.main()
