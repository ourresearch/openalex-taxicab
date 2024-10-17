import os
import tempfile
from abc import ABC
from typing import Callable
from urllib.parse import quote

from mypy_boto3_s3 import S3Client
from tqdm.auto import tqdm

from openalex_taxicab.const import LEGACY_PUBLISHER_PDF_BUCKET, \
    LEGACY_PUBLISHER_LANDING_PAGE_BUCKET, \
    LEGACY_REPO_LANDING_PAGE_BUCKET
from openalex_taxicab.harvest import HarvestResult
from openalex_taxicab.legacy.pdf_version import PDFVersion
from openalex_taxicab.s3_cache import AbstractS3Cache, S3Cache
from openalex_taxicab.s3_util import get_object
from openalex_taxicab.util import normalize_doi


def landing_page_key(doi: str):
    doi = normalize_doi(doi)
    return quote(doi.lower(), safe='')

class LegacyS3Cache(AbstractS3Cache, ABC):

    def __init__(self, s3: S3Client):
        super().__init__(s3)
        self.default_cache = S3Cache(s3)


class PDFCache(LegacyS3Cache):

    BUCKET = LEGACY_PUBLISHER_PDF_BUCKET

    def __init__(self, s3: S3Client):
        super().__init__(s3)

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

    def __init__(self, s3: S3Client, get_key_func: Callable[[str], str | None]):
        super().__init__(s3)
        self.get_key_func = get_key_func

    def get_key(self, url):
        return self.get_key_func(url)

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
