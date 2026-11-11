"""One stored PDF per distinct bytes (oxjob #2023): a PDF we already hold is not stored again."""
import datetime
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "application/pdf")))

import boto3
from botocore.exceptions import ClientError

from openalex_taxicab import deadline
from openalex_taxicab.harvest import Harvester

DDB = boto3.client("dynamodb", region_name="us-east-1", aws_access_key_id="x", aws_secret_access_key="x")
PDF = b"%PDF-1.7\n" + b"x" * 5000 + b"\n%%EOF"


class FakeS3:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Key, Body, Metadata):
        self.objects[(Bucket, Key)] = Body

    def head_object(self, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            raise ClientError({"Error": {"Code": "404"}}, "HeadObject")
        return {}


class FakeMd5Table:
    meta = types.SimpleNamespace(client=DDB)

    def __init__(self, fail=False):
        self.items, self.fail = {}, fail

    def put_item(self, Item, ConditionExpression, ExpressionAttributeValues=None, **kw):
        if self.fail:
            raise RuntimeError("dynamodb down")
        held = self.items.get(Item["md5"])
        ok = held is None if "attribute_not_exists" in ConditionExpression else (
            held is not None and held["id"] == ExpressionAttributeValues[":held"])
        if not ok:
            resp = {"Error": {"Code": "ConditionalCheckFailedException"}}
            if held:
                resp["Item"] = {k: {"S": v} for k, v in held.items()}
            raise DDB.exceptions.ConditionalCheckFailedException(resp, "PutItem")
        self.items[Item["md5"]] = Item


def fetched(url, content=PDF):
    resp = MagicMock()
    resp.content, resp.status_code, resp.url = content, 200, url
    resp.headers = {"Content-Type": "application/pdf"}
    return resp


class PdfMd5Tests(unittest.TestCase):
    def setUp(self):
        self.s3 = FakeS3()
        self.h = Harvester(s3=self.s3)
        self.h._md5_table = FakeMd5Table()
        self.h._pdf_table = MagicMock()

    def tearDown(self):
        deadline.clear()

    def harvest(self, url, content=PDF, native_id="10.1234/abc"):
        with patch("openalex_taxicab.harvest.http_get", return_value=fetched(url, content)):
            return self.h.harvest(url, native_id, "doi")

    def pdf_keys(self):
        return [k for b, k in self.s3.objects if b == Harvester.PDF_BUCKET]

    def test_same_pdf_twice_returns_the_same_id_and_stores_once(self):
        first = self.harvest("https://example.org/a.pdf")
        again = self.harvest("https://example.org/a.pdf")
        self.assertFalse(first["reused"])
        self.assertTrue(again["reused"])
        self.assertEqual(again["id"], first["id"])
        self.assertEqual(again["s3_path"], f"s3://openalex-pdfs/{first['id']}.pdf")
        self.assertEqual(self.pdf_keys(), [f"{first['id']}.pdf"])
        self.assertEqual(self.h._pdf_table.put_item.call_count, 1)

    def test_same_pdf_at_another_link_reuses_the_file(self):
        first = self.harvest("https://journal.example.org/a.pdf")
        other = self.harvest("https://repository.example.edu/files/7", native_id="oai:repo:7")
        self.assertTrue(other["reused"])
        self.assertEqual(other["id"], first["id"])
        self.assertEqual(len(self.pdf_keys()), 1)

    def test_new_pdf_at_the_same_link_is_stored(self):
        first = self.harvest("https://example.org/a.pdf")
        second = self.harvest("https://example.org/a.pdf", content=PDF + b" corrected version")
        self.assertFalse(second["reused"])
        self.assertNotEqual(second["id"], first["id"])
        self.assertEqual(len(self.pdf_keys()), 2)

    def test_held_file_moved_out_is_stored_again(self):
        first = self.harvest("https://example.org/a.pdf")
        del self.s3.objects[(Harvester.PDF_BUCKET, f"{first['id']}.pdf")]
        claim = next(iter(self.h._md5_table.items.values()))
        claim["created_date"] = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=40)).isoformat()
        second = self.harvest("https://example.org/a.pdf")
        self.assertFalse(second["reused"])
        self.assertEqual(self.pdf_keys(), [f"{second['id']}.pdf"])
        self.assertEqual(next(iter(self.h._md5_table.items.values()))["id"], second["id"])

    def test_md5_table_down_stores_as_before(self):
        self.h._md5_table = FakeMd5Table(fail=True)
        first = self.harvest("https://example.org/a.pdf")
        again = self.harvest("https://example.org/a.pdf")
        self.assertFalse(again["reused"])
        self.assertNotEqual(again["id"], first["id"])
        self.assertEqual(len(self.pdf_keys()), 2)


if __name__ == "__main__":
    unittest.main()
