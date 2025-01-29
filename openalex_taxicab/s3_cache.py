from urllib.parse import quote
import gzip

from openalex_taxicab.s3_util import get_object

class S3Cache:
    HTML_BUCKET = 'openalex-harvested-content'
    PDF_BUCKET = 'openalex-harvested-pdfs'

    def __init__(self, s3):
        self.s3 = s3

    def get_bucket(self, result: 'HarvestResult') -> str:
        if result.content_type == 'pdf':
            return self.PDF_BUCKET
        return self.HTML_BUCKET

    def get_key(self, url: str):
        return quote(url.lower()).replace('/', '_')

    def try_get_object(self, url):
        key = self.get_key(url)
        for bucket in [self.HTML_BUCKET, self.PDF_BUCKET]:
            if obj := get_object(bucket, key, self.s3):
                return f's3://{bucket}/{key}', obj
        return None, None

    @staticmethod
    def read_object(obj):
        body = obj['Body'].read()
        if body[:3] == b'\x1f\x8b\x08':  # Check for gzip header
            body = gzip.decompress(body)
        return body

    def put_result(self, result: 'HarvestResult', *args) -> str:
        bucket = self.get_bucket(result)
        key = self.get_key(result.url)

        if isinstance(result.content, str):
            result.content = result.content.encode('utf-8', errors='ignore')
        content = result.content

        if result.content_type and 'html' in result.content_type.lower():
            content = gzip.compress(result.content)
        elif result.content_type and 'pdf' in result.content_type.lower() and not key.endswith('.pdf'):
            key += '.pdf'

        self.s3.put_object(Bucket=bucket,
                           Key=key,
                           Body=content,
                           Metadata={'resolved_url': result.resolved_url})
        return f's3://{bucket}/{key}'
