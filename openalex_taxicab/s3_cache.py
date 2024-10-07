import gzip
from abc import abstractmethod

from mypy_boto3_s3.client import S3Client
import abc

from mypy_boto3_s3.service_resource import Bucket

from openalex_taxicab.const import PDF_BUCKET, PUBLISHER_LANDING_PAGE_BUCKET
from openalex_taxicab.pdf_version import PDFVersion
from openalex_taxicab.s3_util import get_object, landing_page_key


class S3Cache(abc.ABC):

    BUCKET = None

    def __init__(self, s3: S3Client):
        self.s3 = s3

    @abstractmethod
    def get_key(self, *args):
        pass

    @abstractmethod
    def try_get_object(self, *args):
        pass

    @abstractmethod
    def read_object(self, obj):
        pass

    @abstractmethod
    def put_object(self, *args):
        pass



class PDFCache(S3Cache):

    BUCKET = PDF_BUCKET

    def get_key(self, doi, version):
        v = PDFVersion.from_version_str(version)
        return v.s3_key(doi)

    def try_get_object(self, doi, version):
        key = self.get_key(doi, version)
        return get_object(self.BUCKET, key, self.s3, _raise=False)

    def read_object(self, obj):
        return obj['Body'].read()

    def put_object(self, doi, version, content):
        self.s3.put_object(Bucket=self.BUCKET, Key=self.get_key(doi, version), Body=content)



class PublisherLandingPageCache(S3Cache):

    BUCKET = PUBLISHER_LANDING_PAGE_BUCKET

    def get_key(self, doi):
        return landing_page_key(doi)

    def try_get_object(self, doi):
        key = self.get_key(doi)
        return get_object(self.BUCKET, key, self.s3, _raise=False)

    def read_object(self, obj):
        body = obj['Body'].read()
        if body[:3] == b'\x1f\x8b\x08':
            body = gzip.decompress(body)
        return body


    def put_object(self, content, doi, resolved_url):
        self.s3.put_object(Bucket=self.BUCKET, Key=self.get_key(doi), Body=content, Metadata={
            'resolved_url': resolved_url,
        })




