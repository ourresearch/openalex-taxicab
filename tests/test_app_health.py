import importlib
import os
import sys
import unittest
from unittest.mock import patch


class AppHealthTests(unittest.TestCase):
    def test_root_and_health_are_lightweight(self):
        os.environ.setdefault("R2_ACCOUNT_ID", "test-account")
        os.environ.setdefault("R2_ACCESS_KEY_ID", "test-access-key")
        os.environ.setdefault("R2_SECRET_ACCESS_KEY", "test-secret-key")
        sys.modules.pop("app", None)

        with patch("boto3.client"):
            app_module = importlib.import_module("app")

        client = app_module.app.test_client()
        for path in ("/", "/health"):
            response = client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_json()["status"], "ok")
