"""Campaign Zyte keys: a request names a campaign key and its Zyte calls bill to it (oxjob #1790)."""
import importlib
import json
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

from openalex_taxicab import zyte_key
from openalex_taxicab.harvest import Harvester
from openalex_taxicab.http_cache import ResponseObject, call_with_zyte_api

MAIN = "main-key-for-tests"
CAMPAIGN = "campaign-key-for-tests"
ENV = {"ZYTE_API_KEY": MAIN, "ZYTE_CAMPAIGN_KEYS": json.dumps({"campaign-bronze": CAMPAIGN})}
HTML = "<html><head><meta name='citation_title' content='A paper'></head><body>" + "x" * 5000 + "</body></html>"


def page(url):
    return ResponseObject(content=HTML, headers=[{"name": "Content-Type", "value": "text/html"}], status_code=200, url=url)


class ZyteKeyTests(unittest.TestCase):
    def tearDown(self):
        zyte_key.clear()

    def test_no_name_means_the_main_key(self):
        with patch.dict(os.environ, ENV):
            zyte_key.use(None)
            self.assertEqual(zyte_key.current(), MAIN)
            zyte_key.use("")
            self.assertEqual(zyte_key.current(), MAIN)

    def test_known_name_selects_its_key_until_cleared(self):
        with patch.dict(os.environ, ENV):
            zyte_key.use("campaign-bronze")
            self.assertEqual(zyte_key.current(), CAMPAIGN)
            zyte_key.clear()
            self.assertEqual(zyte_key.current(), MAIN)

    def test_unknown_name_is_refused_not_billed_to_the_main_key(self):
        with patch.dict(os.environ, ENV):
            with self.assertRaises(zyte_key.UnknownZyteKey):
                zyte_key.use("campaign-typo")
            self.assertEqual(zyte_key.current(), MAIN)

    def test_names_are_refused_when_no_campaign_keys_are_configured(self):
        with patch.dict(os.environ, {"ZYTE_API_KEY": MAIN}, clear=True):
            with self.assertRaises(zyte_key.UnknownZyteKey):
                zyte_key.use("campaign-bronze")

    def test_bad_json_is_refused_without_echoing_it(self):
        with patch.dict(os.environ, {"ZYTE_API_KEY": MAIN, "ZYTE_CAMPAIGN_KEYS": "{secret-value"}):
            with self.assertRaises(zyte_key.UnknownZyteKey) as ctx:
                zyte_key.use("campaign-bronze")
            self.assertNotIn("secret-value", str(ctx.exception))

    def test_zyte_calls_carry_the_selected_key(self):
        posted = MagicMock()
        posted.json.return_value = {"statusCode": 200}
        with patch.dict(os.environ, ENV), \
                patch("openalex_taxicab.http_cache.requests.post", return_value=posted) as post:
            call_with_zyte_api("https://example.org/a")
            zyte_key.use("campaign-bronze")
            call_with_zyte_api("https://example.org/b")
        self.assertEqual(post.call_args_list[0].kwargs["auth"], (MAIN, ""))
        self.assertEqual(post.call_args_list[1].kwargs["auth"], (CAMPAIGN, ""))


class HarvestZyteKeyTests(unittest.TestCase):
    def setUp(self):
        self.harvester = Harvester(s3=MagicMock())
        self.harvester._store_content = MagicMock()
        self.keys_seen = []

    def tearDown(self):
        zyte_key.clear()

    def fake_http_get(self, url, **kwargs):
        self.keys_seen.append(zyte_key.current())
        return page(url)

    def test_harvest_without_a_name_uses_the_main_key(self):
        with patch.dict(os.environ, ENV), \
                patch("openalex_taxicab.harvest.http_get", side_effect=self.fake_http_get):
            result = self.harvester.harvest("https://example.org/a", "10.1/a", "doi")
        self.assertEqual(self.keys_seen, [MAIN])
        self.assertEqual(result["status_code"], 200)

    def test_harvest_with_a_name_bills_the_campaign_key_then_resets(self):
        with patch.dict(os.environ, ENV), \
                patch("openalex_taxicab.harvest.http_get", side_effect=self.fake_http_get):
            self.harvester.harvest("https://example.org/a", "10.1/a", "doi", zyte_key_name="campaign-bronze")
            self.assertEqual(zyte_key.current(), MAIN)
            self.harvester.harvest("https://example.org/b", "10.1/b", "doi")
        self.assertEqual(self.keys_seen, [CAMPAIGN, MAIN])

    def test_key_is_reset_even_when_the_fetch_fails(self):
        with patch.dict(os.environ, ENV), \
                patch("openalex_taxicab.harvest.http_get", side_effect=RuntimeError("boom")):
            with self.assertRaises(RuntimeError):
                self.harvester.harvest("https://example.org/a", "10.1/a", "doi", zyte_key_name="campaign-bronze")
            self.assertEqual(zyte_key.current(), MAIN)

    def test_unknown_name_fetches_nothing(self):
        with patch.dict(os.environ, ENV), \
                patch("openalex_taxicab.harvest.http_get", side_effect=AssertionError("fetched")):
            with self.assertRaises(zyte_key.UnknownZyteKey):
                self.harvester.harvest("https://example.org/a", "10.1/a", "doi", zyte_key_name="campaign-typo")


class AppZyteKeyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("R2_ACCOUNT_ID", "test-account")
        os.environ.setdefault("R2_ACCESS_KEY_ID", "test-access-key")
        os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test-secret-key")
        sys.modules.pop("app", None)
        with patch("boto3.client"):
            cls.app_module = importlib.import_module("app")
        cls.client = cls.app_module.app.test_client()

    def tearDown(self):
        zyte_key.clear()

    def post(self, body):
        return self.client.post("/taxicab", json=body)

    def test_request_without_zyte_key_behaves_as_before(self):
        body = {"url": "https://example.org/a", "native_id": "10.1/a", "native_id_namespace": "doi"}
        with patch.object(self.app_module.harvester, "harvest", return_value={"id": "abc"}) as harvest:
            response = self.post(body)
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(harvest.call_args.kwargs["zyte_key_name"])
        self.assertIsNone(harvest.call_args.kwargs["fetch_mode"])

    def test_unknown_zyte_key_is_a_400_and_nothing_is_fetched(self):
        body = {"url": "https://example.org/a", "native_id": "10.1/a", "native_id_namespace": "doi",
                "zyte_key": "campaign-typo"}
        with patch.dict(os.environ, ENV), \
                patch("openalex_taxicab.harvest.http_get", side_effect=AssertionError("fetched")):
            response = self.post(body)
        self.assertEqual(response.status_code, 400)
        self.assertIn("unknown zyte_key", response.get_json()["error"])

    def test_known_zyte_key_reaches_the_fetch(self):
        body = {"url": "https://example.org/a", "native_id": "10.1/a", "native_id_namespace": "doi",
                "zyte_key": "campaign-bronze"}
        seen = []

        def fake_http_get(url, **kwargs):
            seen.append(zyte_key.current())
            return page(url)

        with patch.dict(os.environ, ENV), \
                patch("openalex_taxicab.harvest.http_get", side_effect=fake_http_get), \
                patch.object(self.app_module.harvester, "_store_content"):
            response = self.post(body)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(seen, [CAMPAIGN])


if __name__ == "__main__":
    unittest.main()
