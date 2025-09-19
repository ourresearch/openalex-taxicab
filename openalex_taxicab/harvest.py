import uuid
from collections import OrderedDict
from datetime import datetime
import gzip
import os
import re
from typing import Optional
from urllib.parse import quote

import boto3
from boto3.dynamodb.conditions import Key
import requests
import tenacity

from .http_cache import http_get
from .util import guess_mime_type


class Harvester:
    HTML_BUCKET = 'openalex-html'
    PDF_BUCKET = 'openalex-pdfs'
    XML_BUCKET = 'openalex-grobid-xml'

    def __init__(self, s3=None):
        if s3 is None:
            # Configure R2 client if no S3 client provided
            r2_account_id = os.environ.get('R2_ACCOUNT_ID')
            r2_access_key = os.environ.get('R2_ACCESS_KEY_ID')
            r2_secret_key = os.environ.get('R2_SECRET_ACCESS_KEY')

            if not all([r2_account_id, r2_access_key, r2_secret_key]):
                raise ValueError("R2 credentials not configured. Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, and R2_SECRET_ACCESS_KEY environment variables.")

            self._s3 = boto3.client(
                's3',
                endpoint_url=f'https://{r2_account_id}.r2.cloudflarestorage.com',
                aws_access_key_id=r2_access_key,
                aws_secret_access_key=r2_secret_key,
                region_name='auto'
            )
        else:
            self._s3 = s3

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

    def _create_item_dict(self, item: dict) -> OrderedDict:
        """Create a standardized OrderedDict for item responses."""
        return OrderedDict([
            ("id", item.get("id")),
            ("url", item.get("url")),
            ("resolved_url", item.get("resolved_url")),
            ("native_id", item.get("native_id")),
            ("native_id_namespace", item.get("native_id_namespace")),
            ("download_url",
             f"http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com/taxicab/{item.get('id')}"),
            ("s3_path", item.get("s3_path")),
            ("version", item.get("type")),
            ("created_date", item.get("created_date")),
        ])

    def metadata(self):
        # get count of records in HTML table
        html_count = self.get_dynamodb_table_count(self.html_table)
        pdf_count = self.get_dynamodb_table_count(self.pdf_table)
        grobid_count = self.get_dynamodb_table_count(self.grobid_table)

        html_sample_doi = self.html_table.query(
            IndexName="by_native_id_namespace_with_sort",
            KeyConditionExpression=Key("native_id_namespace").eq("doi"),
            ScanIndexForward=False,
            Limit=10
        ).get("Items", [])

        html_sample_pmh = self.html_table.query(
            IndexName="by_native_id_namespace_with_sort",
            KeyConditionExpression=Key("native_id_namespace").eq("pmh"),
            ScanIndexForward=False,
            Limit=10
        ).get("Items", [])

        pdf_sample_doi = self.pdf_table.query(
            IndexName="by_native_id_namespace_with_sort",
            KeyConditionExpression=Key("native_id_namespace").eq("doi"),
            ScanIndexForward=False,
            Limit=10
        ).get("Items", [])

        pdf_sample_pmh = self.pdf_table.query(
            IndexName="by_native_id_namespace_with_sort",
            KeyConditionExpression=Key("native_id_namespace").eq("pmh"),
            ScanIndexForward=False,
            Limit=10
        ).get("Items", [])

        grobid_sample = self.grobid_table.scan(
            Limit=20,
            FilterExpression='attribute_exists(created_date)'
        )

        # merge and sort results for HTML
        html_sample = html_sample_doi + html_sample_pmh
        html_items = sorted(html_sample, key=lambda x: x["created_timestamp"], reverse=True)

        # merge and sort results for PDF
        pdf_sample = pdf_sample_doi + pdf_sample_pmh
        pdf_items = sorted(pdf_sample, key=lambda x: x["created_timestamp"], reverse=True)

        grobid_items = sorted(grobid_sample['Items'],
                                key=lambda x: x.get('created_date', ''),
                                reverse=True)[:20]

        ordered_html_items = [self._create_item_dict(item) for item in html_items]
        ordered_pdf_items = [self._create_item_dict(item) for item in pdf_items]
        ordered_grobid_items = [self._create_item_dict(item) for item in grobid_items]

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

    def fetch_by_doi(self, doi: str) -> dict:
        """Fetch content by DOI"""
        normalized_doi = self._normalize_doi(doi)
        if not normalized_doi:
            return {}

        html_response = self.html_table.query(
            IndexName='by_normalized_doi',
            KeyConditionExpression='normalized_doi = :doi',
            ExpressionAttributeValues={':doi': normalized_doi}
        )

        pdf_response = self.pdf_table.query(
            IndexName='by_normalized_doi',
            KeyConditionExpression='normalized_doi = :doi',
            ExpressionAttributeValues={':doi': normalized_doi}
        )

        grobid_response = self.grobid_table.query(
            IndexName='by_normalized_doi',
            KeyConditionExpression='normalized_doi = :doi',
            ExpressionAttributeValues={':doi': normalized_doi}
        )

        html_items = [self._create_item_dict(item) for item in html_response.get('Items', [])]
        pdf_items = [self._create_item_dict(item) for item in pdf_response.get('Items', [])]
        grobid_items = [self._create_item_dict(item) for item in grobid_response.get('Items', [])]

        return {
            'html': html_items,
            'pdf': pdf_items,
            'grobid': grobid_items
        }

    def fetch_by_pmh_id(self, pmh_id: str) -> dict:
        """Fetch content by PMH ID"""
        html_response = self.html_table.query(
            IndexName='by_native_id',
            KeyConditionExpression='native_id = :pmh_id',
            ExpressionAttributeValues={':pmh_id': pmh_id}
        )

        pdf_response = self.pdf_table.query(
            IndexName='by_native_id',
            KeyConditionExpression='native_id = :pmh_id',
            ExpressionAttributeValues={':pmh_id': pmh_id}
        )

        grobid_response = self.grobid_table.query(
            IndexName='by_native_id',
            KeyConditionExpression='native_id = :pmh_id',
            ExpressionAttributeValues={':pmh_id': pmh_id}
        )

        html_items = [self._create_item_dict(item) for item in html_response.get('Items', [])]
        pdf_items = [self._create_item_dict(item) for item in pdf_response.get('Items', [])]
        grobid_items = [self._create_item_dict(item) for item in grobid_response.get('Items', [])]

        return {
            'html': html_items,
            'pdf': pdf_items,
            'grobid': grobid_items
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
            if native_id_namespace == 'doi':
                response = http_get(url, ask_slowly=True)
            else:
                response = requests.get(url)
        except tenacity.RetryError as e:
            # get status code from the last failed attempt
            last_attempt = e.last_attempt.result()
            return OrderedDict([
                ("id", None),
                ("url", url),
                ("status_code", last_attempt.status_code),
                ("resolved_url", last_attempt.url),
                ("native_id", native_id),
                ("native_id_namespace", native_id_namespace),
                ("s3_path", None),
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

        # skip if not valid content type
        if 'html' not in content_type and 'pdf' not in content_type:
            raise ValueError(f"Invalid content type from {url}, got {content_type}")

        # Only store successful responses with valid content
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
            ("status_code", status_code),
            ("resolved_url", resolved_url),
            ("native_id", native_id),
            ("native_id_namespace", native_id_namespace),
            ("s3_path", f"s3://{self.HTML_BUCKET}/{harvest_id}.html.gz" if content_type != 'pdf' else f"s3://{self.PDF_BUCKET}/{harvest_id}.pdf"),
            ("is_soft_block", is_soft_block),
            ("content_type", content_type),
            ("created_date", created_date),
        ])