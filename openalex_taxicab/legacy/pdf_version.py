from enum import Enum
from urllib.parse import quote

from openalex_taxicab.const import LEGACY_PUBLISHER_PDF_BUCKET, GROBID_XML_BUCKET
from openalex_taxicab.s3_util import get_object, check_exists


class PDFVersion(Enum):
    PUBLISHED = 'published'
    ACCEPTED = 'accepted'
    SUBMITTED = 'submitted'

    @property
    def full_version_str(self) -> str:
        return f'{self.value}Version'

    def s3_key(self, doi):
        return f"{self.s3_prefix}{quote(doi, safe='')}.pdf"

    def grobid_s3_key(self, doi):
        return f'{self.s3_prefix}{quote(doi, safe="")}.xml'

    @property
    def s3_prefix(self):
        if not self == PDFVersion.PUBLISHED:
            return f'{self.value}_'
        return ''

    def s3_url(self, doi):
        return f's3://{LEGACY_PUBLISHER_PDF_BUCKET}/{self.s3_key(doi)}'

    @classmethod
    def from_version_str(cls, version_str: str):
        for version in cls:
            if version.value in version_str.lower():
                return version
        return None

    def valid_in_s3(self, doi) -> bool:
        return check_valid_pdf(LEGACY_PUBLISHER_PDF_BUCKET, self.s3_key(doi))

    def in_s3(self, doi) -> bool:
        return check_exists(LEGACY_PUBLISHER_PDF_BUCKET, self.s3_key(doi))

    def grobid_in_s3(self, doi):
        return check_exists(GROBID_XML_BUCKET, self.grobid_s3_key(doi))

    def get_grobid_xml_obj(self, doi):
        return get_object(GROBID_XML_BUCKET, self.grobid_s3_key(doi))

    def get_pdf_obj(self, doi):
        return get_object(LEGACY_PUBLISHER_PDF_BUCKET, self.s3_key(doi))

def check_valid_pdf(bucket, key, s3=None, _raise=False):
    obj = get_object(bucket, key, s3=s3, _raise=_raise)
    if not obj:
        return False
    contents = obj['Body'].read()
    if contents is not None:
        return is_pdf(contents)
    return False


def is_pdf(contents: bytes) -> bool:
    return contents.startswith(b"%PDF-")