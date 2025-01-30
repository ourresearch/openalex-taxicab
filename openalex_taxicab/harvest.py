import uuid
from datetime import datetime
import gzip
from typing import Optional
import boto3

from .http_cache import http_get
from .util import guess_mime_type


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

    def _is_valid_pdf(self, content: bytes) -> bool:
        """Validate that the content is a PDF"""
        return (
            content
            and content.startswith(b'%PDF-')
            and len(content) >= 100
        )

    def _check_soft_block(self, content: bytes) -> bool:
        """Check if the content indicates a soft block"""
        if not content:
            return False

        patterns = [
            'ShieldSquare Captcha',
            '429 - Too many requests',
            'We apologize for the inconvenience',
            '<title>APA PsycNet</title>',
            'Your request cannot be processed at this time',
            '/cookieAbsent'
        ]

        content_str = content.decode('utf-8', errors='ignore')
        return any(pattern in content_str for pattern in patterns)

    def _store_content(
        self,
        harvest_id: str,
        url: str,
        resolved_url: str,
        content: bytes,
        content_type: str,
        created_date: str,
        is_soft_block: bool
    ) -> None:
        """Store content in appropriate S3 bucket and DynamoDB table"""
        if content_type == 'pdf':
            bucket = self.PDF_BUCKET
            table = self.pdf_table
            key = f"{harvest_id}.pdf"
        else:
            bucket = self.HTML_BUCKET
            table = self.html_table
            key = f"{harvest_id}.html.gz"
            content = gzip.compress(content)

        self._s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            Metadata={
                'url': url,
                'resolved_url': resolved_url,
                'created_date': created_date,
                'content_type': content_type,
                'id': harvest_id,
                'is_soft_block': str(is_soft_block).lower()
            }
        )

        # Store metadata in DynamoDB
        table.put_item(Item={
            'id': harvest_id,
            'url': url,
            'resolved_url': resolved_url,
            'created_date': created_date,
            's3_key': key,
            'is_soft_block': is_soft_block
        })

    def harvest(self, url: str, harvest_id: Optional[str] = None) -> dict:
        """Harvest content from URL and store in appropriate location"""
        if not url:
            raise ValueError('url must be specified')

        if not harvest_id:
            harvest_id = str(uuid.uuid4())

        # Fetch content
        response = http_get(url, ask_slowly=True)

        content = response.content
        status_code = response.status_code
        resolved_url = response.url
        created_date = datetime.now().isoformat()
        content_type = guess_mime_type(content) if content else None
        is_soft_block = self._check_soft_block(content) if content_type != 'pdf' else False

        # Skip invalid PDFs
        if content_type == 'pdf' and not self._is_valid_pdf(content):
            raise ValueError(f"Invalid PDF content from {url}")

        # Only store successful responses with content
        if status_code == 200 and content:
            self._store_content(
                harvest_id,
                url,
                resolved_url,
                content,
                content_type,
                created_date,
                is_soft_block
            )

        return {
            "id": harvest_id,
            "url": url,
            "resolved_url": resolved_url,
            "content": content,
            "content_type": content_type,
            "code": status_code,
            "created_date": created_date,
            "is_soft_block": is_soft_block
        }