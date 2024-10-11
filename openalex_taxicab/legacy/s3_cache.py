import gzip
import io
import os
import sqlite3
import tempfile
from abc import ABC
from sqlite3 import Connection
from urllib.parse import quote

import pandas as pd
from tqdm.auto import tqdm
from mypy_boto3_s3 import S3Client

from openalex_taxicab.const import LEGACY_PUBLISHER_PDF_BUCKET, \
    LEGACY_PUBLISHER_LANDING_PAGE_BUCKET, \
    LEGACY_REPO_LANDING_PAGE_BUCKET, CONTENT_BUCKET
from openalex_taxicab.harvest import HarvestResult
from openalex_taxicab.legacy.pdf_version import PDFVersion
from openalex_taxicab.log import LOGGER
from openalex_taxicab.s3_cache import AbstractS3Cache, S3Cache
from openalex_taxicab.s3_util import get_object
from openalex_taxicab.util import normalize_doi

LOOKUP_DB_CONN: Connection = None



def initialize(s3: S3Client):
    bucket = 'openalex-elt'
    key = 's3_keys_lookup.db'
    object_size = s3.head_object(Bucket=bucket, Key=key)[
        'ContentLength']

    progress_bar = tqdm(total=object_size, unit='B', unit_scale=True,
                        desc="Downloading SQLite DB")

    def progress_callback(bytes_transferred):
        # You can use tqdm to show the progress of the download (optional)
        progress_bar.update(bytes_transferred - progress_bar.n)

    LOGGER.info('Initializing s3 key lookup tables...')
    global LOOKUP_DB_CONN

    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')

    with os.fdopen(temp_fd, 'wb') as temp_file:
        s3.download_fileobj(bucket, key, temp_file, Callback=progress_callback)
        temp_file.flush()
    LOOKUP_DB_CONN = sqlite3.connect(temp_path)
    LOGGER.info('Finished initializing s3 key lookup tables')

def landing_page_key(doi: str):
    doi = normalize_doi(doi)
    return quote(doi.lower(), safe='')

class LegacyS3Cache(AbstractS3Cache, ABC):

    def __init__(self, s3: S3Client):
        super().__init__(s3)
        if LOOKUP_DB_CONN is None:
            initialize(s3)
        self.default_cache = S3Cache(s3)


class PDFCache(LegacyS3Cache):

    BUCKET = LEGACY_PUBLISHER_PDF_BUCKET

    def get_key(self, doi, version):
        v = PDFVersion.from_version_str(version)
        return v.s3_key(doi)

    def try_get_object(self, doi, version, url=None):
        if url:
            s3_path, obj = self.default_cache.try_get_object(url)
            if obj:
                return s3_path, obj
        key = self.get_key(doi, version)
        if obj := get_object(self.BUCKET, key, self.s3, _raise=False):
            return f's3://{self.BUCKET}/{key}', obj
        return None, None

    def put_result(self, result: HarvestResult, *args) -> str:
        return self.default_cache.put_result(result)


class PublisherLandingPageCache(LegacyS3Cache):

    BUCKET = LEGACY_PUBLISHER_LANDING_PAGE_BUCKET

    def get_key(self, doi):
        return landing_page_key(doi)

    def try_get_object(self, doi):
        s3_path, obj = self.default_cache.try_get_object(f'https://doi.org/{doi}')
        if obj:
            return s3_path, obj
        key = self.get_key(doi)
        if obj := get_object(self.BUCKET, key, self.s3):
            return f's3://{self.BUCKET}/{key}', obj
        return None, None

    def put_result(self, result: HarvestResult, *args) -> str:
        return self.default_cache.put_result(result, *args)


class RepoLandingPageCache(LegacyS3Cache):

    BUCKET = LEGACY_REPO_LANDING_PAGE_BUCKET

    def get_key(self, url):
        query = """
        SELECT landing_page_key
        FROM page_s3_keys
        WHERE url = ?
        LIMIT 1
        """

        # Execute the query using the provided connection
        cursor = LOOKUP_DB_CONN.cursor()
        cursor.execute(query, (url,))

        # Fetch the result
        result = cursor.fetchone()

        # If a result is found, return the landing_page_key; otherwise, return None
        if result:
            return result[0]

        return None

    def try_get_object(self, url):
        s3_path, obj = self.default_cache.try_get_object(url)
        if obj:
            return s3_path, obj
        key = self.get_key(url)
        if not key:
            return None
        if obj := get_object(self.BUCKET, key, self.s3):
            return f's3://{self.BUCKET}/{key}', obj
        return None, None

    def put_result(self, result, *args) -> str:
        return self.default_cache.put_result(result, *args)
