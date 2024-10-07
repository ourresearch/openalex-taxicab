import abc
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from bs4 import BeautifulSoup
from mypy_boto3_s3.client import S3Client
from parseland_lib.legacy_parse_utils.fulltext import parse_publisher_fulltext_locations, parse_repo_fulltext_locations

from openalex_http import http_get

from openalex_taxicab.const import PUBLISHER_LANDING_PAGE_BUCKET
from openalex_taxicab.pdf_version import PDFVersion
from openalex_taxicab.s3_cache import PDFCache, S3Cache, PublisherLandingPageCache
from openalex_taxicab.s3_util import landing_page_key


@dataclass
class ResponseMeta:
    code: int
    elapsed: int
    resolved_url: str


@dataclass
class BaseHarvestResult:
    s3_path: str
    last_harvested: datetime
    content: bytes
    response_meta: Optional[ResponseMeta] = None  # On cache/S3 hit, this will be None

@dataclass
class LandingPageHarvestResult(BaseHarvestResult):
    pdf_url: Optional[str] = None
    is_pdf: bool = False
    pdf_version: Optional[str] = None
    is_soft_block: bool = False

    @property
    def pdf_found(self) -> bool:
        return self.pdf_url is not None


class Harvester(abc.ABC):
    def __init__(self, s3: S3Client):
        self._s3 = s3
        self.cache: S3Cache

    @abc.abstractmethod
    def cached_result(self, *args) -> Optional[BaseHarvestResult]:
        pass

    @abc.abstractmethod
    def fetched_result(self, *args) -> BaseHarvestResult: # url for PDF, repo landing page | doi, publisher for publisher landing page
        pass

    def harvest(self, *args) -> BaseHarvestResult:
        if cached_result := self.cached_result(*args):
            return cached_result
        result = self.fetched_result(*args)
        self.cache.put_object(result.content, *args)
        return result


class PDFHarvester(Harvester):
    def __init__(self, s3: S3Client):
        super().__init__(s3)
        self.cache = PDFCache(s3)

    def cached_result(self, url: str, doi: str, version: str) -> Optional[
        BaseHarvestResult]:
        if obj := self.cache.try_get_object(doi, version):
            contents = self.cache.read_object(obj)
            v = PDFVersion.from_version_str(version)
            return BaseHarvestResult(
                s3_path=v.s3_url(doi),
                last_harvested=obj['LastModified'],
                content=contents
            )
        return None

    def fetched_result(self, url, doi, version) -> BaseHarvestResult:
        v = PDFVersion.from_version_str(version)
        response = http_get(url)

        return BaseHarvestResult(
            s3_path=v.s3_url(doi),
            last_harvested=datetime.now(),
            content=response.content,
            response_meta=ResponseMeta(
                code=response.status_code,
                elapsed=response.elapsed.total_seconds(),
                resolved_url=response.url
            )
        )

    def harvest(self, url: str, doi: str, version: str) -> BaseHarvestResult:
        return super().harvest(url, doi, version)


class PublisherLandingPageHarvester(Harvester):

    BUCKET = PUBLISHER_LANDING_PAGE_BUCKET


    def __init__(self, s3: S3Client):
        super().__init__(s3)
        self.cache = PublisherLandingPageCache(s3)


    def cached_result(self, doi, publisher, resolved_url='') -> Optional[LandingPageHarvestResult]:
        if obj := self.cache.try_get_object(doi):
            content = self.cache.read_object(obj)
            soup = BeautifulSoup(content, features='lxml',
                                 parser='lxml')

            result = LandingPageHarvestResult(
                s3_path=f's3://{self.BUCKET}/{landing_page_key(doi)}',
                last_harvested=datetime.now(),
                content=content,
            )
            result.is_pdf = None  # TODO: implement
            result.is_soft_block = None  # TODO implement
            fulltext_locations = parse_publisher_fulltext_locations(soup,
                                                                    publisher,
                                                                    obj['Metadata'].get('resolved_url') or resolved_url)
            if fulltext_locations:
                # only 1 location returned from parse_publisher_fulltext_locations (multiple returned from parse_repo_fulltext_locations)
                location = fulltext_locations[0]
                result.pdf_url = location['url']
                result.pdf_version = location['version']

            return result
        return None


    def fetched_result(self, doi, publisher) -> LandingPageHarvestResult:
        url = f'https://doi.org/{doi}'
        response = http_get(url)
        soup = BeautifulSoup(response.content, features='lxml', parser='lxml')
        result = LandingPageHarvestResult(
            s3_path=f's3://{self.BUCKET}/{landing_page_key(doi)}',
            last_harvested=datetime.now(),
            content=response.content,
            response_meta=ResponseMeta(
                code=response.status_code,
                elapsed=response.elapsed.total_seconds(),
                resolved_url=response.url
            ),
        )
        result.is_pdf = None  # TODO: implement
        result.is_soft_block = None  # TODO implement
        fulltext_locations = parse_publisher_fulltext_locations(soup, publisher, response.url)
        if fulltext_locations:
            # only 1 location returned from parse_publisher_fulltext_locations (multiple returned from parse_repo_fulltext_locations)
            location = fulltext_locations[0]
            result.pdf_url = location['url']
            result.pdf_version = location['version']

        return result

    def harvest(self, doi, publisher) -> LandingPageHarvestResult:
        if cached_result := self.cached_result(doi, publisher):
            return cached_result
        result = self.fetched_result(doi, publisher)
        self.cache.put_object(result.content, doi, result.response_meta.resolved_url)
        return result
