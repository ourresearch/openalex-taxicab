import abc
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from typing import Optional

import boto3
from botocore.exceptions import ClientError
import uuid

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
            'ShieldSquare Captcha',
            '429 - Too many requests',
            'We apologize for the inconvenience',
            '<title>APA PsycNet</title>',
            'Your request cannot be processed at this time',
            '/cookieAbsent'
        ]

        if isinstance(self.content, bytes):
            content_str = self.content.decode('utf-8', errors='ignore')
        else:
            content_str = self.content

        return any(pattern in content_str for pattern in patterns)

    @property
    def is_valid_pdf(self) -> bool:
        if not self.content:
            return False

        # check content type
        if self.content_type != 'pdf':
            return False

        # check PDF header signature
        if not self.content.startswith(b'%PDF-'):
            return False

        # check minimum size (100 bytes)
        if len(self.content) < 100:
            return False

        return True

    def to_dict(self):
        d = asdict(self)
        d['is_soft_block'] = self.is_soft_block
        d['content_type'] = self.content_type
        d['last_harvested_dt'] = self.last_harvested_dt
        d['is_valid_pdf'] = self.is_valid_pdf
        return d


class AbstractHarvester(abc.ABC):
    def __init__(self, s3):
        self._s3 = s3
        self.cache: 'S3Cache'

    @abc.abstractmethod
    def cached_result(self, *args, **kwargs) -> Optional[HarvestResult]:
        pass

    @abc.abstractmethod
    def fetched_result(self, *args,
                       **kwargs) -> HarvestResult:  # url for PDF, repo landing page | doi, publisher for publisher landing page
        pass

    def harvest(self, *args, **kwargs) -> HarvestResult:
        if (not args or all(not arg for arg in args)) and not kwargs.get('url'):
            raise ValueError('harvest args or url kwarg must be specified')

        # check if result is cached
        if cached_result := self.cached_result(*args, **kwargs):
            print(f"Skipping fetch: result is cached")
            return cached_result

        # fetch new result
        result = self.fetched_result(*args, **kwargs)

        if result.content_type == 'pdf':
            if not result.is_valid_pdf:
                print(f"Skipping save: Invalid PDF content for {result.url}")
                result.code = 400
                return result

        # skip saving invalid results
        if result.code != 200 or not result.content:
            print(f"Skipping save: status={result.code}, content={bool(result.content)}")
            return result
        else:
            print(f"Saving valid result for {result.url} to {result.s3_path}")

        # save valid result to S3
        new_s3_path = self.cache.put_result(result, *args)
        result.s3_path = new_s3_path
        return result


class Harvester(AbstractHarvester):

    def __init__(self, s3):
        super().__init__(s3)
        self.cache = S3Cache(s3)
        self._dynamodb = None
        self._logs_table = None

    def fetched_result(self, url) -> HarvestResult:
        start = time.time()
        r = http_get(url, ask_slowly=True)
        end = time.time()

        result = HarvestResult(
            s3_path=None,
            last_harvested=datetime.now().isoformat(),
            url=url,
            content=r.content,
            code=r.status_code,
            elapsed=round(end - start, 2),
            resolved_url=r.url
        )

        if r.status_code == 200 and r.content:
            result.s3_path = f"s3://{self.cache.get_bucket(result)}/{self.cache.get_key(url)}"

        return result

    @property
    def dynamodb(self):
        if self._dynamodb is None:
            session = boto3.Session(region_name='us-east-1')
            self._dynamodb = session.resource('dynamodb')
        return self._dynamodb

    @property
    def logs_table(self):
        if self._logs_table is None:
            self._logs_table = self.dynamodb.Table('harvest-logs')
        return self._logs_table

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

    def log_to_dynamodb(self, result: HarvestResult):
        """
        Logs the harvest result to DynamoDB.
        """
        log_entry = {
            'id': str(uuid.uuid4()),
            'url': result.url,
            'resolved_url': result.resolved_url,
            'status_code': result.code,
            'elapsed': Decimal(str(result.elapsed)) if result.elapsed is not None else None,
            'content_type': result.content_type,
            'last_harvested': result.last_harvested,
            's3_path': result.s3_path,
            'is_soft_block': result.is_soft_block,
            'timestamp': datetime.now().isoformat(),
        }

        try:
            self.logs_table.put_item(Item=log_entry)
            print(f"Logged harvest result for {result.url} to DynamoDB.")
        except ClientError as e:
            print(f"Failed to log to DynamoDB: {e.response['Error']['Message']}")

    def harvest(self, url) -> HarvestResult:
        return super().harvest(url)
