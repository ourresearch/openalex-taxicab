import gzip
import io
from abc import ABC
from urllib.parse import quote

import pandas as pd
from mypy_boto3_s3 import S3Client
from pandas.core.interchange.dataframe_protocol import DataFrame

from openalex_taxicab.const import LEGACY_PUBLISHER_PDF_BUCKET, \
    LEGACY_PUBLISHER_LANDING_PAGE_BUCKET, \
    LEGACY_REPO_LANDING_PAGE_BUCKET, CONTENT_BUCKET
from openalex_taxicab.harvest import HarvestResult
from openalex_taxicab.legacy.pdf_version import PDFVersion
from openalex_taxicab.log import LOGGER
from openalex_taxicab.s3_cache import AbstractS3Cache, S3Cache
from openalex_taxicab.s3_util import get_object
from openalex_taxicab.util import normalize_doi

S3_REPO_KEY_LOOKUP_DF: DataFrame = None
S3_PDF_URL_LOOKUP_DF: DataFrame = None


def initialize(s3: S3Client):
    LOGGER.info('Initializing s3 key lookup tables...')
    global S3_REPO_KEY_LOOKUP_DF
    global S3_PDF_URL_LOOKUP_DF

    if S3_PDF_URL_LOOKUP_DF and S3_REPO_KEY_LOOKUP_DF:
        return

    response = s3.get_object(Bucket='openalex-elt', Key='page_s3_keys.parquet')
    data = io.BytesIO(response['Body'].read())
    S3_REPO_KEY_LOOKUP_DF = pd.read_parquet(data, engine='pyarrow')

    response = s3.get_object(Bucket='openalex-elt', Key='doi_pdf_urls.parquet')
    data = io.BytesIO(response['Body'].read())
    S3_PDF_URL_LOOKUP_DF = pd.read_parquet(data, engine='pyarrow')

    LOGGER.info('Finished initializing s3 key lookup tables')

def landing_page_key(doi: str):
    doi = normalize_doi(doi)
    return quote(doi.lower(), safe='')

class LegacyS3Cache(AbstractS3Cache, ABC):

    def __init__(self, s3: S3Client):
        super().__init__(s3)
        if S3_REPO_KEY_LOOKUP_DF is None:
            initialize(s3)
        self.default_cache = S3Cache(s3)


class PDFCache(LegacyS3Cache):

    BUCKET = LEGACY_PUBLISHER_PDF_BUCKET

    def get_key(self, doi, version):
        v = PDFVersion.from_version_str(version)
        return v.s3_key(doi)

    def try_get_object(self, doi, version):
        key = S3_PDF_URL_LOOKUP_DF[(S3_PDF_URL_LOOKUP_DF.doi == doi.lower()) & (S3_PDF_URL_LOOKUP_DF.version == version)]
        if not key.empty:
            url = key.iloc[0].url
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
        matching_rows = S3_REPO_KEY_LOOKUP_DF[S3_REPO_KEY_LOOKUP_DF.url == url]
        if matching_rows.empty:
            return None
        return matching_rows.iloc[0].landing_page_key

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
