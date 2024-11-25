import abc
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from functools import cached_property
from typing import Optional

from mypy_boto3_s3.client import S3Client
from openalex_taxicab.http_cache import http_get

from openalex_taxicab.s3_cache import S3Cache
from openalex_taxicab.util import guess_mime_type


@dataclass
class Version:
    parsed_url: str
    parsed_version: str

@dataclass
class HarvestResult:
    s3_path: str
    last_harvested: str
    content: bytes
    url: str
    code: int = None
    elapsed: float = None
    resolved_url: str = ''

    @cached_property
    def content_type(self) -> str | None:
        if not self.content:
            return None
        return guess_mime_type(self.content)

    @property
    def last_harvested_dt(self) -> datetime | None:
        if not self.last_harvested:
            return None
        return datetime.fromisoformat(self.last_harvested)

    @property
    def is_soft_block(self) -> bool | None:
        if not self.content:
            return None
        patterns = [
            b'ShieldSquare Captcha',
            b'429 - Too many requests',
            b'We apologize for the inconvenience',
            b'<title>APA PsycNet</title>',
            b'Your request cannot be processed at this time',
            b'/cookieAbsent'
        ]
        return any(pattern in self.content for pattern in patterns)

    def to_dict(self):
        d = asdict(self)
        d['is_soft_block'] = self.is_soft_block
        d['content_type'] = self.content_type
        d['last_harvested_dt'] = self.last_harvested_dt
        return d



class AbstractHarvester(abc.ABC):
    def __init__(self, s3: S3Client):
        self._s3 = s3
        self.cache: 'S3Cache'

    @abc.abstractmethod
    def cached_result(self, *args, **kwargs) -> Optional[HarvestResult]:
        pass

    @abc.abstractmethod
    def fetched_result(self, *args, **kwargs) -> HarvestResult: # url for PDF, repo landing page | doi, publisher for publisher landing page
        pass

    def harvest(self, *args, **kwargs) -> HarvestResult:
        if (not args or all(not arg for arg in args)) and not kwargs['url']:
            raise ValueError('harvest args or url kwarg must be specified')
        if cached_result := self.cached_result(*args, **kwargs):
            return cached_result
        result = self.fetched_result(*args, **kwargs)
        new_s3_path = self.cache.put_result(result, *args)
        result.s3_path = new_s3_path
        return result


class Harvester(AbstractHarvester):

    def __init__(self, s3: S3Client):
        super().__init__(s3)
        self.cache = S3Cache(s3)

    def fetched_result(self, url) -> HarvestResult:
        start = time.time()
        r = http_get(url, ask_slowly=True)
        end = time.time()

        return HarvestResult(
            s3_path=f's3://{self.cache.BUCKET}/{self.cache.get_key(url)}',
            last_harvested=datetime.now().isoformat(),
            url=url,
            content=r.content,
            code=r.status_code,
            elapsed=round(end - start, 2),
            resolved_url=r.url
        )

    def cached_result(self, url) -> Optional[HarvestResult]:
        s3_path, obj = self.cache.try_get_object(url)
        if obj:
            return HarvestResult(
                s3_path=s3_path,
                last_harvested=obj['LastModified'].isoformat(),
                content=self.cache.read_object(obj),
                url=url,
                resolved_url=obj.get('Metadata', {}).get('resolved_url', '')
            )
        return None

    def harvest(self, url) -> HarvestResult:
        return super().harvest(url)