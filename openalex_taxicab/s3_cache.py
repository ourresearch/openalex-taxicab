import gzip
from abc import abstractmethod
from urllib.parse import quote

from mypy_boto3_s3.client import S3Client
import abc

from openalex_taxicab.s3_util import get_object


class AbstractS3Cache(abc.ABC):

    BUCKET = None

    def __init__(self, s3: S3Client):
        self.s3 = s3

    @abstractmethod
    def get_key(self, *args):
        pass

    @abstractmethod
    def try_get_object(self, *args, **kwargs) -> (str, dict):
        pass

    @staticmethod
    def read_object(obj):
        body = obj['Body'].read()
        if body[:3] == b'\x1f\x8b\x08':
            body = gzip.decompress(body)
        return body

    @abstractmethod
    def put_result(self, result: 'HarvestResult', *args) -> str:
        pass



class S3Cache(AbstractS3Cache):

    BUCKET = 'openalex-harvested-content'

    def get_key(self, url: str):
        return quote(url.lower()).replace('/', '_')

    def try_get_object(self, url):
        key = self.get_key(url)
        if obj := get_object(self.BUCKET, key, self.s3):
            return f's3://{self.BUCKET}/{key}', obj
        return None, None

    def put_result(self, result: 'HarvestResult', *args) -> str:
        if isinstance(result.content, str):
            result.content = result.content.encode('utf-8', errors='ignore')
        content = result.content
        if result.content_type == 'html':
            content = gzip.compress(result.content)
        self.s3.put_object(Bucket=self.BUCKET,
                          Key=self.get_key(result.url),
                          Body=content,
                          Metadata={'resolved_url': result.resolved_url})
        return f's3://{self.BUCKET}/{self.get_key(result.url)}'

