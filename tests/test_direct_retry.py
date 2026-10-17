"""fetch_mode=direct: the caller retries a page Zyte was banned from by fetching it ourselves (oxjob #1712)."""
import importlib
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

from openalex_taxicab import deadline
from openalex_taxicab.harvest import Harvester
from openalex_taxicab.http_cache import http_get

HTML = b"<html><head><meta name='citation_title' content='A paper'></head><body>" + b"x" * 5000 + b"</body></html>"


def fake_direct_response(url, status=200, content=HTML):
    resp = MagicMock()
    resp.content = content
    resp.headers = {"Content-Type": "text/html"}
    resp.status_code = status
    resp.url = url
    return resp


def zyte_must_not_be_called(*args, **kwargs):
    raise AssertionError("a direct retry must not call Zyte")


class ForceDirectHttpGetTests(unittest.TestCase):
    def tearDown(self):
        deadline.clear()

    def test_force_direct_fetches_without_zyte(self):
        url = "https://repository.example.edu/items/123"
        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=zyte_must_not_be_called), \
                patch("openalex_taxicab.http_cache.requests.get", return_value=fake_direct_response(url)) as get:
            r = http_get(url, force_direct=True)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(get.call_args.args[0], url)
        self.assertIn("A paper", r.content)

    def test_force_direct_skips_publisher_recipes(self):
        url = "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ijsw.12017"
        with patch("openalex_taxicab.http_cache._fetch_wiley_pdf", side_effect=AssertionError("recipe ran")), \
                patch("openalex_taxicab.http_cache._fetch_wiley_pdfdirect", side_effect=AssertionError("recipe ran")), \
                patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=zyte_must_not_be_called), \
                patch("openalex_taxicab.http_cache.requests.get", return_value=fake_direct_response(url)):
            r = http_get(url, force_direct=True)
        self.assertEqual(r.status_code, 200)

    def test_force_direct_keeps_status_of_a_refusal(self):
        url = "https://repository.example.edu/items/403"
        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=zyte_must_not_be_called), \
                patch("openalex_taxicab.http_cache.requests.get",
                      return_value=fake_direct_response(url, status=403, content=b"<html>no</html>")):
            r = http_get(url, force_direct=True)
        self.assertEqual(r.status_code, 403)

    def test_default_still_goes_through_zyte(self):
        url = "https://repository.example.edu/items/456"
        with patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value={"status": 404}) as zyte, \
                patch("openalex_taxicab.http_cache.requests.get", side_effect=AssertionError("went direct")):
            http_get(url)
        self.assertEqual(zyte.call_count, 1)


class HarvestFetchModeTests(unittest.TestCase):
    def setUp(self):
        self.harvester = Harvester(s3=object())

    def _harvest(self, **kwargs):
        with patch("openalex_taxicab.harvest.http_get", side_effect=deadline.DeadlineExceeded("stop")) as get:
            self.harvester.harvest("https://example.org/a", "oai:x", "pmh", **kwargs)
        return get.call_args.kwargs

    def test_direct_mode_reaches_http_get(self):
        self.assertTrue(self._harvest(fetch_mode="direct")["force_direct"])

    def test_default_and_unknown_modes_use_zyte(self):
        self.assertFalse(self._harvest()["force_direct"])
        self.assertFalse(self._harvest(fetch_mode="zyte")["force_direct"])


class AppFetchModeTests(unittest.TestCase):
    def test_post_passes_fetch_mode_through(self):
        os.environ.setdefault("R2_ACCOUNT_ID", "test-account")
        os.environ.setdefault("R2_ACCESS_KEY_ID", "test-access-key")
        os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test-secret-key")
        sys.modules.pop("app", None)
        with patch("boto3.client"):
            app_module = importlib.import_module("app")
        client = app_module.app.test_client()
        result = {"id": None, "url": "https://example.org/a", "status_code": 504}
        with patch.object(app_module.harvester, "harvest", return_value=result) as harvest:
            client.post("/taxicab", json={"url": "https://example.org/a", "native_id": "oai:x",
                                          "native_id_namespace": "pmh", "fetch_mode": "direct"})
            client.post("/taxicab", json={"url": "https://example.org/a", "native_id": "oai:x",
                                          "native_id_namespace": "pmh"})
        self.assertEqual(harvest.call_args_list[0].kwargs["fetch_mode"], "direct")
        self.assertIsNone(harvest.call_args_list[1].kwargs["fetch_mode"])


if __name__ == "__main__":
    unittest.main()
