import time
from datetime import datetime
from typing import Optional

from mypy_boto3_s3 import S3Client
from openalex_http import http_get

from openalex_taxicab.const import LEGACY_PUBLISHER_LANDING_PAGE_BUCKET
from openalex_taxicab.harvest import AbstractHarvester, HarvestResult
from openalex_taxicab.legacy.pdf_version import PDFVersion
from openalex_taxicab.legacy.s3_cache import PDFCache, \
    PublisherLandingPageCache, RepoLandingPageCache, LOOKUP_DB_CONN


class PDFHarvester(AbstractHarvester):
    def __init__(self, s3: S3Client):
        super().__init__(s3)
        self.cache = PDFCache(s3)

    @staticmethod
    def try_get_url(doi: str, version: str) -> Optional[str]:
        query = """
        SELECT pdf_url
        FROM doi_pdf_urls
        WHERE doi = ? AND version = ?
        LIMIT 1
        """

        cursor = LOOKUP_DB_CONN.cursor()
        cursor.execute(query, (doi, version))

        result = cursor.fetchone()

        if result:
            return result[0]

        return None

    def cached_result(self, doi: str, version: str, url: str = None) -> Optional[HarvestResult]:
        version = PDFVersion.from_version_str(version).full_version_str
        s3_path, obj = self.cache.try_get_object(doi, version, url=url)
        if obj:
            contents = self.cache.read_object(obj)
            return HarvestResult(
                s3_path=s3_path,
                last_harvested=obj['LastModified'],
                content=contents,
                url=url
            )
        return None

    def fetched_result(self, doi: str, version: str, url: str = None) -> HarvestResult:
        v = PDFVersion.from_version_str(version)
        start = time.time()
        response = http_get(url)
        end = time.time()

        return HarvestResult(
            s3_path=v.s3_url(doi),
            last_harvested=datetime.now(),
            content=response.content,
            code=response.status_code,
            elapsed=round(end - start, 2),
            resolved_url=response.url
        )

    def harvest(self, doi: str, version: str, url: str = None) -> HarvestResult:
        if not url:
            url = self.try_get_url(doi, version)
        return super().harvest( doi, version, url=url)


class PublisherLandingPageHarvester(AbstractHarvester):

    BUCKET = LEGACY_PUBLISHER_LANDING_PAGE_BUCKET


    def __init__(self, s3: S3Client):
        super().__init__(s3)
        self.cache = PublisherLandingPageCache(s3)


    def cached_result(self, doi) -> Optional[HarvestResult]:
        s3_path, obj = self.cache.try_get_object(doi)
        if obj:
            content = self.cache.read_object(obj)
            result = HarvestResult(
                s3_path=s3_path,
                url=f'https://doi.org/{doi.lower()}',
                last_harvested=obj['LastModified'],
                content=content,
            )
            return result
        return None


    def fetched_result(self, doi) -> HarvestResult:
        url = f'https://doi.org/{doi}'
        start = time.time()
        response = http_get(url, ask_slowly=True)
        end = time.time()
        result = HarvestResult(
            url=url,
            last_harvested=datetime.now(),
            content=response.content,
            code=response.status_code,
            elapsed=round(end - start, 2),
            resolved_url=response.url
        )
        return result

    def harvest(self, doi) -> HarvestResult:
        return super().harvest(doi)


class RepoLandingPageHarvester(AbstractHarvester):

    def __init__(self, s3):
        super().__init__(s3)
        self.cache = RepoLandingPageCache(s3)

    def cached_result(self, url) -> Optional[HarvestResult]:
        s3_path, obj = self.cache.try_get_object(url)
        if obj:
            content = self.cache.read_object(obj)
            return HarvestResult(
                s3_path=s3_path,
                last_harvested=obj['LastModified'],
                content=content,
                url=url,
            )
        return None

    def fetched_result(self, url) -> HarvestResult:
        start = time.time()
        r = http_get(url)
        end = time.time()
        return HarvestResult(
            url=url,
            last_harvested=datetime.now(),
            content=r.content,
            code=r.status_code,
            elapsed=round(end  - start, 2),
            resolved_url=r.url,
        )

    def harvest(self, url) -> HarvestResult:
        return super().harvest(url)


