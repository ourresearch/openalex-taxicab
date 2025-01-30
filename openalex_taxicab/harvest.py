import uuid
from datetime import datetime
import gzip
from dataclasses import dataclass
from typing import Optional
import boto3

from .http_cache import http_get
from .util import guess_mime_type


@dataclass
class HarvestResult:
    id: str
    url: str
    content: bytes
    content_type: Optional[str] = None
    code: Optional[int] = None
    resolved_url: str = ''
    created_date: str = None

    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.content_type and self.content:
            self.content_type = guess_mime_type(self.content)

    @property
    def is_valid_pdf(self) -> bool:
        if not self.content:
            return False
        if self.content_type != 'pdf':
            return False
        if not self.content.startswith(b'%PDF-'):
            return False
        if len(self.content) < 100:
            return False
        return True


class Harvester:
    HTML_BUCKET = 'harvested-html-content'
    PDF_BUCKET = 'harvested-pdf-content'

    def __init__(self, s3=None):
        self._s3 = s3 or boto3.client('s3', region_name='us-east-1')
        self._dynamodb = None
        self._html_table = None
        self._pdf_table = None

    @property
    def dynamodb(self):
        if self._dynamodb is None:
            self._dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        return self._dynamodb

    @property
    def html_table(self):
        if self._html_table is None:
            self._html_table = self.dynamodb.Table('harvested-html')
        return self._html_table

    @property
    def pdf_table(self):
        if self._pdf_table is None:
            self._pdf_table = self.dynamodb.Table('harvested-pdf')
        return self._pdf_table

    def _store_content(self, result: HarvestResult) -> None:
        """Store content in appropriate S3 bucket and DynamoDB table"""
        # Determine bucket and table based on content type
        if result.content_type == 'pdf':
            bucket = self.PDF_BUCKET
            table = self.pdf_table
            key = f"{result.id}.pdf"
            content = result.content
        else:
            bucket = self.HTML_BUCKET
            table = self.html_table
            key = f"{result.id}.html.gz"
            content = gzip.compress(result.content)

        self._s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            Metadata={
                'url': result.url,
                'resolved_url': result.resolved_url,
                'created_date': result.created_date,
                'content_type': result.content_type or '',
                'id': result.id
            }
        )

        # store metadata in DynamoDB
        table.put_item(Item={
            'id': result.id,
            'url': result.url,
            'resolved_url': result.resolved_url,
            'created_date': result.created_date,
            's3_key': key
        })

    def harvest(self, url: str, harvest_id: str = None) -> HarvestResult:
        """Harvest content from URL and store in appropriate location"""
        if not url:
            raise ValueError('url must be specified')

        if not harvest_id:
            harvest_id = str(uuid.uuid4())

        # Fetch content
        response = http_get(url, ask_slowly=True)

        result = HarvestResult(
            id=harvest_id,
            url=url,
            content=response.content,
            code=response.status_code,
            resolved_url=response.url
        )

        # Skip invalid PDFs
        if result.content_type == 'pdf' and not result.is_valid_pdf:
            raise ValueError(f"Invalid PDF content from {url}")

        # Only store successful responses with content
        if result.code == 200 and result.content:
            self._store_content(result)

        return result