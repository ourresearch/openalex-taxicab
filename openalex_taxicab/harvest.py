import uuid
from collections import OrderedDict
from datetime import datetime
import gzip
import re
from typing import Optional
from urllib.parse import quote

import boto3
import tenacity

from .http_cache import http_get
from .util import guess_mime_type


class Harvester:
    HTML_BUCKET = 'openalex-harvested-html'
    PDF_BUCKET = 'openalex-harvested-pdfs'

    def __init__(self, s3=None):
        self._s3 = s3 or boto3.client('s3', region_name='us-east-1')
        self._dynamodb = None
        self._html_table = None
        self._pdf_table = None
        self._grobid_table = None

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

    @property
    def grobid_table(self):
        if self._grobid_table is None:
            self._grobid_table = self.dynamodb.Table('grobid-xml')
        return self._grobid_table

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

        content_str = content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else str(content)
        return any(pattern in content_str for pattern in patterns)

    def _normalize_doi(self, native_id) -> Optional[str]:
        native_id = native_id.strip().lower()

        # test cases for this regex are at https://regex101.com/r/zS4hA0/4
        p = re.compile(r'(10\.\d+/[^\s]+)')
        matches = re.findall(p, native_id)

        if len(matches) == 0:
            return None

        doi = matches[0]
        if isinstance(doi, bytes):
            doi = str(doi, "utf-8", errors="ignore")

        return doi.replace('\0', '')

    def get_dynamodb_table_count(self, table):
        dynamodb = boto3.client("dynamodb")
        response = dynamodb.describe_table(TableName=table.name)
        return response["Table"]["ItemCount"]

    def metadata(self):
        # get count of records in HTML table
        html_count = self.get_dynamodb_table_count(self.html_table)
        pdf_count = self.get_dynamodb_table_count(self.pdf_table)
        grobid_count = self.get_dynamodb_table_count(self.grobid_table)

        # get most recent HTML records
        html_sample = self.html_table.scan(
            Limit=20,
            FilterExpression='attribute_exists(created_date)'
        )

        # get most recent PDF records
        pdf_sample = self.pdf_table.scan(
            Limit=20,
            FilterExpression='attribute_exists(created_date)'
        )

        grobid_sample = self.grobid_table.scan(
            Limit=20,
            FilterExpression='attribute_exists(created_date)'
        )

        # sort the samples by created_date since scan doesn't guarantee order
        html_items = sorted(html_sample['Items'],
                            key=lambda x: x.get('created_date', ''),
                            reverse=True)[:20]
        pdf_items = sorted(pdf_sample['Items'],
                           key=lambda x: x.get('created_date', ''),
                           reverse=True)[:20]

        grobid_items = sorted(grobid_sample['Items'],
                                key=lambda x: x.get('created_date', ''),
                                reverse=True)[:20]

        key_order = [
            "id",
            "url",
            "resolved_url",
            "native_id",
            "native_id_namespace",
            "s3_path",
            "created_date",
        ]

        def to_ordered_dict(item):
            return OrderedDict((key, item[key]) for key in key_order if key in item)

        ordered_html_items = [to_ordered_dict(item) for item in html_items]
        ordered_pdf_items = [to_ordered_dict(item) for item in pdf_items]
        ordered_grobid_items = [to_ordered_dict(item) for item in grobid_items]

        return {
            'meta': {
                'html': html_count,
                'pdf': pdf_count,
                'grobid': grobid_count,
                'total': html_count + pdf_count + grobid_count
            },
            'results': {
                'html': ordered_html_items,
                'pdf': ordered_pdf_items,
                'grobid': ordered_grobid_items
            }
        }

    def _store_content(
            self,
            harvest_id: str,
            url: str,
            resolved_url: str,
            content: bytes,
            content_type: str,
            created_date: str,
            native_id: str,
            native_id_namespace: str
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

            if isinstance(content, str):
                content = content.encode('utf-8')
            elif not isinstance(content, bytes):
                content = str(content).encode('utf-8')
            content = gzip.compress(content)

        encoded_url = quote(str(url or ''))
        encoded_resolved_url = quote(str(resolved_url or ''))

        s3_metadata = {
            'url': encoded_url,
            'resolved_url': encoded_resolved_url,
            'created_date': str(created_date or ''),
            'content_type': str(content_type or ''),
            'id': str(harvest_id or ''),
            'native_id': str(native_id or ''),
            'native_id_namespace': str(native_id_namespace or '')
        }

        s3_path = f"s3://{bucket}/{key}"

        # store in s3
        self._s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=content,
            Metadata=s3_metadata
        )

        # store metadata in DynamoDB
        normalized_doi = self._normalize_doi(native_id)
        if not normalized_doi:
            normalized_doi = f"non-doi-{harvest_id}"

        table.put_item(Item={
            'id': harvest_id,
            'url': url,
            'native_id': native_id,
            'native_id_namespace': native_id_namespace,
            'normalized_doi': normalized_doi,
            'resolved_url': resolved_url,
            's3_key': key,
            's3_path': s3_path,
            'created_date': created_date,
        })

    def harvest(
            self,
            url: str,
            native_id: str,
            native_id_namespace: str
    ) -> dict:
        """Harvest content from URL and store in appropriate location"""
        if not url:
            raise ValueError('url must be specified')

        harvest_id = str(uuid.uuid4())

        try:
            response = http_get(url, ask_slowly=True)
        except tenacity.RetryError as e:
            # get status code from the last failed attempt
            last_attempt = e.last_attempt.result()
            return OrderedDict([
                ("id", None),
                ("url", url),
                ("code", last_attempt.status_code),
                ("resolved_url", last_attempt.url),
                ("native_id", native_id),
                ("native_id_namespace", native_id_namespace),
                ("content_type", None),
                ("is_soft_block", False),
                ("created_date", None),
            ])

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
        if status_code == 200 and content and not is_soft_block:
            self._store_content(
                harvest_id,
                url,
                resolved_url,
                content,
                content_type,
                created_date,
                native_id,
                native_id_namespace
            )

        return OrderedDict([
            ("id", harvest_id),
            ("url", url),
            ("code", status_code),
            ("resolved_url", resolved_url),
            ("native_id", native_id),
            ("native_id_namespace", native_id_namespace),
            ("is_soft_block", is_soft_block),
            ("content_type", content_type),
            ("created_date", created_date),
        ])