import unittest

from openalex_taxicab.eval_harness import select_html_record


class RecordSelectionTests(unittest.TestCase):
    def test_latest_created_date_wins(self):
        record, count = select_html_record(
            {
                "html": [
                    {"id": "old", "created_date": "2026-01-01T00:00:00"},
                    {"id": "new", "created_date": "2026-06-01T00:00:00"},
                ]
            }
        )
        self.assertEqual(count, 2)
        self.assertEqual(record["id"], "new")

    def test_empty_html_records(self):
        record, count = select_html_record({"html": []})
        self.assertIsNone(record)
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
