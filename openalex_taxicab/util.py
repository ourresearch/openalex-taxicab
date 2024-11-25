import re
import time
from urllib.parse import urljoin

from unidecode import unidecode
from requests.adapters import HTTPAdapter

import magic


class NoDoiException(Exception):
    pass

def to_unicode_or_bust(obj, encoding='utf-8'):
    if isinstance(obj, bytes):
        obj = str(obj, encoding)
    return obj


def normalize_doi(doi, return_none_if_error=False):
    if not doi:
        if return_none_if_error:
            return None
        else:
            raise NoDoiException("There's no DOI at all.")

    doi = doi.strip().lower()

    # test cases for this regex are at https://regex101.com/r/zS4hA0/4
    p = re.compile(r'(10\.\d+/[^\s]+)')
    matches = re.findall(p, doi)

    if len(matches) == 0:
        if return_none_if_error:
            return None
        else:
            raise NoDoiException("There's no valid DOI.")

    doi = matches[0]

    # clean_doi has error handling for non-utf-8
    # but it's preceded by a call to remove_nonprinting_characters
    # which calls to_unicode_or_bust with no error handling
    # clean/normalize_doi takes a unicode object or utf-8 basestring or dies
    doi = to_unicode_or_bust(doi)

    return doi.replace('\0', '')


def guess_mime_type(content):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_buffer(content)
    if 'html' in mime_type or 'javascript' in mime_type:
        return 'html'
    elif 'pdf' in mime_type:
        return 'pdf'
    elif 'vnd.openxmlformats-officedocument.wordprocessingml.document' in mime_type:
        return 'docx'
    elif 'msword' in mime_type:
        return 'doc'
    else:
        return 'other'


class DelayedAdapter(HTTPAdapter):
    def send(self, request, stream=False, timeout=None, verify=True, cert=None,
             proxies=None):
        # logger.info(u"in DelayedAdapter getting {}, sleeping for 2 seconds".format(request.url))
        # sleep(2)
        start_time = time.time()
        response = super(DelayedAdapter, self).send(request, stream, timeout,
                                                    verify, cert, proxies)
        # logger.info(u"   HTTPAdapter.send for {} took {} seconds".format(request.url, elapsed(start_time, 2)))
        return response


def elapsed(since, round_places=2):
    return round(time.time() - since, round_places)


def clean_html(raw_html):
    cleanr = re.compile('<\w+.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def remove_punctuation(input_string):
    # from http://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string-in-python
    no_punc = input_string
    if input_string:
        no_punc = "".join(
            e for e in input_string if (e.isalnum() or e.isspace()))
    return no_punc

# good for deduping strings.  warning: output removes spaces so isn't readable.
def normalize(text):
    if isinstance(text, bytes):
        text = str(text, 'ascii')
    response = text.lower()
    response = unidecode(response)
    response = clean_html(response)  # has to be before remove_punctuation
    response = remove_punctuation(response)
    response = re.sub(r"\b(a|an|the)\b", "", response)
    response = re.sub(r"\b(and)\b", "", response)
    response = re.sub(r"\s+", "", response)
    return response

def is_same_publisher(publisher1, publisher2):
    if publisher1 and publisher2:
        return normalize(publisher1) == normalize(publisher2)
    return False

def strip_jsessionid_from_url(url):
    url = re.sub(r";jsessionid=\w+", "", url)
    return url


def get_link_target(url, base_url, strip_jsessionid=True):
    if strip_jsessionid:
        url = strip_jsessionid_from_url(url)
    if base_url:
        url = urljoin(base_url, url)
    return url

