import unittest
from time import time
from unittest.mock import patch

import requests

from openalex_taxicab import deadline
from openalex_taxicab.harvest import Harvester
from openalex_taxicab.http_cache import http_get


class BoundedTimeoutTests(unittest.TestCase):
    def tearDown(self):
        deadline.clear()

    def test_no_budget_passes_timeouts_through(self):
        self.assertEqual(deadline.bounded_timeout((10, 60)), (10, 60))
        self.assertEqual(deadline.bounded_timeout(15), 15)
        self.assertIsNone(deadline.bounded_timeout(None))

    def test_shrinks_to_time_left(self):
        deadline.start(budget=20)
        connect, read = deadline.bounded_timeout((10, 60))
        self.assertEqual(connect, 10)
        self.assertLessEqual(read, 20)
        self.assertGreater(read, 19)
        self.assertLessEqual(deadline.bounded_timeout(None), 20)

    def test_raises_when_budget_spent(self):
        deadline.start(started_at=time() - 60, budget=55)
        with self.assertRaises(deadline.DeadlineExceeded):
            deadline.bounded_timeout((10, 60))

    def test_alb_received_at_reads_trace_root(self):
        now = 1_800_000_000
        header = f"Self=1-abc;Root=1-{now - 7:08x}-0123456789abcdef01234567"
        self.assertEqual(deadline.alb_received_at(header, now=now), now - 7)

    def test_alb_received_at_rejects_missing_or_implausible(self):
        now = 1_800_000_000
        self.assertIsNone(deadline.alb_received_at(None, now=now))
        self.assertIsNone(deadline.alb_received_at("garbage", now=now))
        self.assertIsNone(deadline.alb_received_at(f"Root=1-{now - 600:08x}-0123", now=now))
        self.assertIsNone(deadline.alb_received_at(f"Root=1-{now + 60:08x}-0123", now=now))


class HttpGetBudgetTests(unittest.TestCase):
    def tearDown(self):
        deadline.clear()

    def test_skips_retry_when_budget_cannot_cover_it(self):
        calls = []

        def fake_zyte(url, params=None):
            calls.append(url)
            return {"status": 429}

        deadline.start(budget=10)
        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_zyte):
            with self.assertRaises(Exception) as caught:
                http_get("https://example.org/article/1")
        self.assertEqual(type(caught.exception).__name__, "RetryError")
        self.assertEqual(len(calls), 1)

    def test_zyte_post_gets_a_timeout(self):
        deadline.start(budget=30)
        with patch("openalex_taxicab.http_cache.requests.post") as fake_post:
            fake_post.return_value.json.return_value = {"status": 404}
            http_get("https://example.org/article/2")
        timeout = fake_post.call_args.kwargs["timeout"]
        self.assertLessEqual(max(timeout), 30)


class HarvestBudgetTests(unittest.TestCase):
    def setUp(self):
        self.harvester = Harvester(s3=object())

    def test_spent_budget_returns_504_with_nothing_stored(self):
        with patch("openalex_taxicab.harvest.http_get", side_effect=deadline.DeadlineExceeded("spent")):
            result = self.harvester.harvest("https://example.org/a", "10.1/x", "doi", started_at=time())
        self.assertIsNone(result["id"])
        self.assertEqual(result["status_code"], 504)
        self.assertIsNone(result["s3_path"])
        self.assertIsNone(deadline.time_left())

    def test_request_timeout_returns_504(self):
        with patch("openalex_taxicab.harvest.http_get", side_effect=requests.exceptions.ReadTimeout("slow")):
            result = self.harvester.harvest("https://example.org/b", "oai:x", "pmh")
        self.assertEqual(result["status_code"], 504)
        self.assertIsNone(result["id"])


if __name__ == "__main__":
    unittest.main()
