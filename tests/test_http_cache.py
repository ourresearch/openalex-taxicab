import base64
import sys
import types
import unittest
from unittest.mock import patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

from openalex_taxicab.http_cache import (
    _should_use_landing_page_rewrite,
    _is_sciencedirect_pdf_url,
    _sciencedirect_am_pii,
    _ssrn_abstract_id,
    elsevier_journal_fulltext_url_from_pdf_viewer,
    http_get,
    jbc_fulltext_url_from_url,
    upgrade_cairn_legacy_pdf_url,
    sciencedirect_article_url_from_pdf_asset,
)


_EXFIL_BLOCKED_HTML = (
    '<html><body><div id="__pdfout" data-status="403" '
    'data-ct="text/html;charset=UTF-8"></div></body></html>'
)


class ScienceDirectUrlTests(unittest.TestCase):
    PDF_BYTES = b"%PDF-1.7\n" + b"x" * 30_000 + b"\n%%EOF"

    @staticmethod
    def _exfil_html(b64="", attrs=""):
        return f'<html><body><div id="__pdfout"{attrs}>{b64}</div></body></html>'

    def test_http_get_uses_browser_exfil_for_wiley_pdf(self):
        """Wiley PDF URLs go through the in-page browser exfil, not a body fetch."""
        pdf_url = "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ijsw.12017"
        captured = []
        encoded = base64.b64encode(self.PDF_BYTES).decode()

        class FakeResponse:
            status_code = 200

            def json(self):
                return {"browserHtml": ScienceDirectUrlTests._exfil_html(
                    encoded, ' data-status="200" data-ct="application/pdf"')}

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1111/ijsw.12017")

        self.assertEqual(len(captured), 1)
        self.assertTrue(captured[0]["browserHtml"])
        self.assertNotIn("httpResponseBody", captured[0])
        # the article page is rendered, and the PDF is fetched RELATIVE to it so
        # the request stays same-origin on the journal subdomain
        self.assertEqual(captured[0]["url"],
                         "https://onlinelibrary.wiley.com/doi/10.1111/ijsw.12017")
        self.assertIn('"/doi/pdfdirect/10.1111/ijsw.12017"',
                      captured[0]["actions"][0]["source"])
        self.assertEqual(response.content, self.PDF_BYTES)

    def test_wiley_browser_exfil_retries_403_then_falls_back_to_body_strategies(self):
        """403 is Wiley rate limiting, not entitlement: retry, then try body fetches."""
        pdf_url = "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/jols.12117"
        captured = []
        blocked = {"browserHtml": _EXFIL_BLOCKED_HTML}
        body_responses = [
            {"status": 520, "detail": "ban-free response unavailable"},
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>not pdf</html>").decode(),
            },
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(self.PDF_BYTES).decode(),
            },
        ]

        class FakeResponse:
            status_code = 200

            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            # first three calls are browser-exfil attempts, then the body strategies
            if len(captured) <= 3:
                return FakeResponse(blocked)
            return FakeResponse(body_responses[len(captured) - 4])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post), \
                patch("openalex_taxicab.http_cache.sleep"):
            response = http_get(pdf_url, doi="10.1111/jols.12117")

        self.assertEqual(len(captured), 6)
        # 403 was retried rather than reported as a paywall
        for payload in captured[:3]:
            self.assertTrue(payload["browserHtml"])
        # then the three body strategies, in order
        self.assertNotIn("customHttpRequestHeaders", captured[3])
        self.assertEqual(
            captured[4]["customHttpRequestHeaders"],
            [{"name": "Accept", "value": "application/pdf,*/*"}],
        )
        self.assertEqual(
            captured[5]["customHttpRequestHeaders"],
            [
                {"name": "Accept", "value": "application/pdf,*/*"},
                {"name": "Referer", "value": "https://www.google.com/"},
            ],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_wiley_browser_exfil_404_is_terminal(self):
        """A 404 means no PDF at this DOI: one attempt, and no body-strategy fallback."""
        pdf_url = "https://nph.onlinelibrary.wiley.com/doi/pdfdirect/10.1111/nph.99999"
        captured = []

        class FakeResponse:
            status_code = 200

            def json(self):
                return {"browserHtml": ScienceDirectUrlTests._exfil_html(
                    "", ' data-status="404" data-ct="text/html"')}

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post), \
                patch("openalex_taxicab.http_cache.sleep"):
            response = http_get(pdf_url, doi="10.1111/nph.99999")

        self.assertEqual(len(captured), 1)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content, b"")

    def test_wiley_browser_exfil_rejects_truncated_pdf(self):
        """PDF-looking but incomplete bytes must never be stored as a PDF."""
        pdf_url = "https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ijsw.12018"
        # header present, no %%EOF, far under the size floor: the 174-byte
        # viewer shell / corrupt-xref shape from the Wiley public-TRUE probe
        encoded = base64.b64encode(b"%PDF-1.7\nviewer shell").decode()

        class FakeResponse:
            status_code = 200

            def json(self):
                return {"browserHtml": ScienceDirectUrlTests._exfil_html(
                    encoded, ' data-status="200" data-ct="application/pdf"')}

        with patch("openalex_taxicab.http_cache.requests.post", return_value=FakeResponse()), \
                patch("openalex_taxicab.http_cache.sleep"):
            response = http_get(pdf_url, doi="10.1111/ijsw.12018")

        self.assertFalse(response.content.startswith(b"%PDF-"))

    def test_is_sciencedirect_pdf_url_matching(self):
        self.assertTrue(_is_sciencedirect_pdf_url(
            "https://www.sciencedirect.com/science/article/pii/S0022247X18302294/pdf"))
        self.assertTrue(_is_sciencedirect_pdf_url(
            "https://www.sciencedirect.com/science/article/pii/055032139290256B/pdf/"))
        self.assertTrue(_is_sciencedirect_pdf_url(
            "https://sciencedirect.com/science/article/abs/pii/S0022247X18302294/pdf"))
        # landing/abstract (no /pdf suffix), non-SD hosts, and signed asset URLs must NOT match
        self.assertFalse(_is_sciencedirect_pdf_url(
            "https://www.sciencedirect.com/science/article/pii/S0022247X18302294"))
        self.assertFalse(_is_sciencedirect_pdf_url(
            "https://www.sciencedirect.com/science/article/pii/S0022247X18302294/abstract"))
        self.assertFalse(_is_sciencedirect_pdf_url(
            "https://pdf.sciencedirectassets.com/271610/1-s2.0-S0022247X18302294/main.pdf"))
        self.assertFalse(_is_sciencedirect_pdf_url("https://doi.org/10.1016/j.jmaa.2018.03.023"))

    def test_sciencedirect_two_step_session_returns_pdf(self):
        pdf_url = "https://www.sciencedirect.com/science/article/pii/S0022247X18302294/pdf"
        signed_url = "https://pdf.sciencedirectassets.com/271610/1-s2.0-S0022247X18302294/main.pdf?tk=fake-test-token"
        captured = []
        responses = [
            {  # step 1: browser render with a main.pdf capture (response body is the stub)
                "url": pdf_url,
                "browserHtml": "<html>viewer</html>",
                "networkCapture": [{
                    "url": signed_url,
                    "httpResponseBody": base64.b64encode(b"<!doctype html>stub").decode(),
                    "request": {"headers": {"referer": pdf_url, "user-agent": "Zyte"}},
                }],
            },
            {  # step 2: replay yields real PDF bytes
                "statusCode": 200,
                "url": signed_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1016/j.jmaa.2018.03.023")

        self.assertEqual(len(captured), 2)
        self.assertTrue(captured[0]["browserHtml"])
        # both calls share the same session id
        self.assertEqual(captured[0]["session"]["id"], captured[1]["session"]["id"])
        # step 2 replays the signed url + captured headers (map -> list shape)
        self.assertEqual(captured[1]["url"], signed_url)
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "referer", "value": pdf_url}, {"name": "user-agent", "value": "Zyte"}],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertEqual(response.status_code, 200)

    def test_sciencedirect_retry_on_520_uses_fresh_session(self):
        pdf_url = "https://www.sciencedirect.com/science/article/pii/S0022247X18302294/pdf"
        signed_url = "https://pdf.sciencedirectassets.com/271610/1-s2.0-S0022247X18302294/main.pdf?tk=fake-test-token"
        captured = []
        responses = [
            {"status": 520, "detail": "ban-free response unavailable"},  # attempt 1 step1
            {  # attempt 2 step1 with capture
                "url": pdf_url,
                "browserHtml": "<html>viewer</html>",
                "networkCapture": [{
                    "url": signed_url,
                    "httpResponseBody": base64.b64encode(b"stub").decode(),
                    "request": {"headers": {"referer": pdf_url}},
                }],
            },
            {  # attempt 2 step2 -> PDF
                "statusCode": 200,
                "url": signed_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1016/j.jmaa.2018.03.023")

        self.assertEqual(len(captured), 3)
        # the failed first attempt used a different session id than the successful retry
        self.assertNotEqual(captured[0]["session"]["id"], captured[1]["session"]["id"])
        self.assertEqual(captured[1]["session"]["id"], captured[2]["session"]["id"])
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_sciencedirect_paywall_html_passes_through(self):
        pdf_url = "https://www.sciencedirect.com/science/article/pii/S0022247X18302294/pdf"
        captured = []

        class FakeResponse:
            def json(self):
                return {
                    "url": pdf_url,
                    "browserHtml": "<html><body>Purchase PDF or Sign in</body></html>",
                    "networkCapture": [],
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1016/j.jmaa.2018.03.023")

        # no step 2, single browser call; returns HTML, not a PDF, at status 200
        self.assertEqual(len(captured), 1)
        self.assertEqual(response.status_code, 200)
        self.assertNotIsInstance(response.content, bytes)
        self.assertIn("Purchase PDF", response.content)

    def test_sciencedirect_am_pii_matching(self):
        # accepted-manuscript URLs (with/without /pdf, with query) yield the PII
        self.assertEqual(
            _sciencedirect_am_pii("https://www.sciencedirect.com/science/article/am/pii/S0242649820300316"),
            "S0242649820300316")
        self.assertEqual(
            _sciencedirect_am_pii("https://www.sciencedirect.com/science/article/am/pii/S0242649820300316?via%3Dihub"),
            "S0242649820300316")
        self.assertEqual(
            _sciencedirect_am_pii("https://www.sciencedirect.com/science/article/am/pii/S0242649820300316/pdf"),
            "S0242649820300316")
        # published viewer, abstract, and non-SD hosts are NOT accepted-manuscript URLs
        self.assertIsNone(
            _sciencedirect_am_pii("https://www.sciencedirect.com/science/article/pii/S0242649820300316/pdf"))
        self.assertIsNone(
            _sciencedirect_am_pii("https://www.sciencedirect.com/science/article/abs/pii/S0242649820300316"))
        self.assertIsNone(
            _sciencedirect_am_pii("https://example.com/science/article/am/pii/S0242649820300316"))

    def test_sciencedirect_am_three_step_session_returns_pdf(self):
        am_url = "https://www.sciencedirect.com/science/article/am/pii/S0242649820300316?via%3Dihub"
        signed_url = "https://pdf.sciencedirectassets.com/276851/1-s2.0-S0242649820300316/am.pdf?tk=fake-test-token"
        captured = []
        responses = [
            {  # step 1: landing page render exposes the AM manuscript link
                "url": "https://www.sciencedirect.com/science/article/abs/pii/S0242649820300316",
                "browserHtml": '<html><a href="/science/article/am/pii/S0242649820300316">View open manuscript</a></html>',
            },
            {  # step 2: AM viewer render captures the signed am.pdf request (body is the stub)
                "url": "https://www.sciencedirect.com/science/article/am/pii/S0242649820300316",
                "browserHtml": "<html>viewer</html>",
                "networkCapture": [{
                    "url": signed_url,
                    "httpResponseBody": base64.b64encode(b"<!doctype html>stub").decode(),
                    "request": {"headers": {"referer": am_url, "user-agent": "Zyte"}},
                }],
            },
            {  # step 3: replay yields real PDF bytes
                "statusCode": 200,
                "url": signed_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(am_url, doi="10.1016/j.annpat.2020.01.006")

        self.assertEqual(len(captured), 3)
        # all three calls share one session id so the signed asset stays valid
        self.assertEqual(captured[0]["session"]["id"], captured[1]["session"]["id"])
        self.assertEqual(captured[1]["session"]["id"], captured[2]["session"]["id"])
        # step 2 captures am.pdf (not main.pdf); step 3 replays the signed url + headers
        self.assertEqual(captured[1]["networkCapture"][0]["value"], "am.pdf")
        self.assertEqual(captured[2]["url"], signed_url)
        self.assertEqual(
            captured[2]["customHttpRequestHeaders"],
            [{"name": "referer", "value": am_url}, {"name": "user-agent", "value": "Zyte"}],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertEqual(response.status_code, 200)

    def test_sciencedirect_am_no_manuscript_link_returns_landing_html(self):
        am_url = "https://www.sciencedirect.com/science/article/am/pii/S0242649820300316?via%3Dihub"
        captured = []

        class FakeResponse:
            def json(self):
                # landing render with no /am/pii/ link => no open manuscript
                return {
                    "url": "https://www.sciencedirect.com/science/article/abs/pii/S0242649820300316",
                    "browserHtml": "<html><body>Purchase PDF or Sign in</body></html>",
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(am_url, doi="10.1016/j.annpat.2020.01.006")

        # only landing renders (one per attempt), never a viewer/replay; HTML at 200
        self.assertEqual(len(captured), 3)
        self.assertTrue(all("networkCapture" not in call for call in captured))
        self.assertEqual(response.status_code, 200)
        self.assertNotIsInstance(response.content, bytes)
        self.assertIn("Purchase PDF", response.content)

    def test_sciencedirect_exhausted_returns_520_no_pdf(self):
        pdf_url = "https://www.sciencedirect.com/science/article/pii/S0022247X18302294/pdf"
        signed_url = "https://pdf.sciencedirectassets.com/271610/1-s2.0-S0022247X18302294/main.pdf?tk=fake-test-token"
        captured = []

        class FakeResponse:
            def json(self):
                # step1 always captures; step2 always returns non-PDF HTML
                if len(captured) % 2 == 1:
                    return {
                        "url": pdf_url,
                        "browserHtml": "<html>viewer</html>",
                        "networkCapture": [{
                            "url": signed_url,
                            "httpResponseBody": base64.b64encode(b"stub").decode(),
                            "request": {"headers": {"referer": pdf_url}},
                        }],
                    }
                return {
                    "statusCode": 200,
                    "url": signed_url,
                    "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                    "httpResponseBody": base64.b64encode(b"<html>60kb not pdf</html>").decode(),
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1016/j.jmaa.2018.03.023")

        # 3 attempts x 2 calls each; exhausted -> 520 (NOT a retryable status), empty content
        self.assertEqual(len(captured), 6)
        self.assertEqual(response.status_code, 520)
        self.assertEqual(response.content, b"")

    def test_ssrn_abstract_id_matching(self):
        self.assertEqual(_ssrn_abstract_id("https://doi.org/10.2139/ssrn.6239931",
                                           "10.2139/ssrn.6239931"), "6239931")
        self.assertEqual(_ssrn_abstract_id(
            "https://papers.ssrn.com/sol3/Delivery.cfm?abstractid=6239931&mirid=1", None), "6239931")
        self.assertEqual(_ssrn_abstract_id(
            "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6239931", None), "6239931")
        self.assertIsNone(_ssrn_abstract_id("https://www.sciencedirect.com/x", "10.1016/j.x"))
        self.assertIsNone(_ssrn_abstract_id("https://example.com/a", None))

    def test_ssrn_two_step_session_returns_pdf(self):
        signed_url = "https://papers.ssrn.com/sol3/Delivery.cfm/abc-MECA.pdf?abstractid=6239931&mirid=1"
        captured = []
        responses = [
            {  # step 1: browser render, click, capture a .pdf request (0-byte body)
                "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6239931",
                "browserHtml": "<html>abstract</html>",
                "networkCapture": [{
                    "url": signed_url,
                    "httpResponseBody": base64.b64encode(b"").decode(),
                    "request": {"headers": {"referer": "https://papers.ssrn.com/", "user-agent": "Zyte"}},
                }],
            },
            {  # step 2: replay yields real PDF bytes
                "statusCode": 200,
                "url": signed_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get("https://doi.org/10.2139/ssrn.6239931", doi="10.2139/ssrn.6239931")

        self.assertEqual(len(captured), 2)
        self.assertTrue(captured[0]["browserHtml"])
        self.assertEqual(captured[0]["session"]["id"], captured[1]["session"]["id"])
        self.assertEqual(captured[1]["url"], signed_url)
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "referer", "value": "https://papers.ssrn.com/"}, {"name": "user-agent", "value": "Zyte"}],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertEqual(response.status_code, 200)

    def test_ssrn_no_capture_returns_html(self):
        captured = []

        class FakeResponse:
            def json(self):
                return {
                    "url": "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6239931",
                    "browserHtml": "<html><body>This paper has been removed from SSRN</body></html>",
                    "networkCapture": [],
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get("https://doi.org/10.2139/ssrn.6239931", doi="10.2139/ssrn.6239931")

        self.assertEqual(len(captured), 1)
        self.assertEqual(response.status_code, 200)
        self.assertNotIsInstance(response.content, bytes)
        self.assertIn("removed", response.content)

    def test_http_get_uses_pdf_body_strategy_for_scholarhub_viewcontent(self):
        pdf_url = "https://scholarhub.ui.ac.id/cgi/viewcontent.cgi?article=1201&context=journal"
        captured = []

        class FakeResponse:
            def json(self):
                return {
                    "statusCode": 200,
                    "url": pdf_url,
                    "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                    "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url)

        self.assertEqual(len(captured), 1)
        self.assertTrue(captured[0]["httpResponseBody"])
        self.assertTrue(captured[0]["httpResponseHeaders"])
        self.assertNotIn("browserHtml", captured[0])
        self.assertEqual(response.url, pdf_url)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_falls_back_for_scholarhub_viewcontent_strategies(self):
        pdf_url = "https://scholarhub.ui.ac.id/cgi/viewcontent.cgi?article=1201&context=journal"
        captured = []
        responses = [
            {
                "statusCode": 202,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<script>window.location='download'</script>").decode(),
            },
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": "",
            },
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url)

        self.assertEqual(len(captured), 3)
        self.assertNotIn("customHttpRequestHeaders", captured[0])
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "Accept", "value": "application/pdf,*/*"}],
        )
        self.assertEqual(
            captured[2]["customHttpRequestHeaders"],
            [
                {"name": "Accept", "value": "application/pdf,*/*"},
                {"name": "Referer", "value": "https://www.google.com/"},
            ],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_does_not_scholarhub_route_non_viewcontent(self):
        article_url = "https://scholarhub.ui.ac.id/article/view/1201"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>Scholarhub article shell</html>").decode(),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertNotIn("customHttpRequestHeaders", captured["params"])
        self.assertIsInstance(response.content, str)
        self.assertIn("Scholarhub article shell", response.content)

    def test_http_get_fetches_sba_ojs_pdf_directly(self):
        pdf_url = "https://www.sba.org.br/open_journal_systems/index.php/cba/article/download/4194/3678"
        captured = {}

        class FakeResponse:
            content = b"%PDF-1.5\nbody\n%%EOF"
            headers = {"Content-Type": "application/pdf"}
            status_code = 200
            url = pdf_url

        def fake_get(url, **kwargs):
            captured["url"] = url
            captured["headers"] = kwargs.get("headers")
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.get", side_effect=fake_get):
            with patch("openalex_taxicab.http_cache.call_with_zyte_api") as fake_zyte:
                response = http_get(pdf_url)

        self.assertEqual(captured["url"], pdf_url)
        self.assertEqual(captured["headers"], {"Accept": "application/pdf,*/*"})
        fake_zyte.assert_not_called()
        self.assertEqual(response.url, pdf_url)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_does_not_sba_route_article_html(self):
        article_url = "https://www.sba.org.br/open_journal_systems/index.php/cba/article/view/4194"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>SBA article page</html>").decode(),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertNotIn("customHttpRequestHeaders", captured["params"])
        self.assertIsInstance(response.content, str)
        self.assertIn("SBA article page", response.content)

    def test_http_get_uses_pdf_body_strategy_for_iop_article_pdf(self):
        pdf_url = "https://iopscience.iop.org/article/10.1088/0951-7715/7/1/008/pdf"
        captured = []

        class FakeResponse:
            def json(self):
                return {
                    "statusCode": 200,
                    "url": pdf_url,
                    "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                    "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1088/0951-7715/7/1/008")

        self.assertEqual(len(captured), 1)
        self.assertTrue(captured[0]["httpResponseBody"])
        self.assertTrue(captured[0]["httpResponseHeaders"])
        self.assertNotIn("browserHtml", captured[0])
        self.assertEqual(response.url, pdf_url)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_falls_back_for_iop_article_pdf_strategies(self):
        pdf_url = "https://iopscience.iop.org/article/10.1088/0953-4075/42/12/125102/pdf"
        captured = []
        responses = [
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>not pdf</html>").decode(),
            },
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1088/0953-4075/42/12/125102")

        self.assertEqual(len(captured), 2)
        self.assertNotIn("customHttpRequestHeaders", captured[0])
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "Accept", "value": "application/pdf,*/*"}],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_does_not_iop_route_book_chapter_pdf(self):
        pdf_url = "https://iopscience.iop.org/book/978-1-6817-4465-0/chapter/bk978-1-6817-4465-0ch14/pdf"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>Paywall</html>").decode(),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(pdf_url, doi="10.1088/978-1-6817-4465-0ch14")

        self.assertEqual(captured["url"], pdf_url)
        self.assertEqual(captured["params"]["url"], pdf_url)
        self.assertNotIn("customHttpRequestHeaders", captured["params"])
        self.assertIsInstance(response.content, str)
        self.assertIn("Paywall", response.content)

    def test_http_get_uses_pdf_body_strategy_for_acm_pdf(self):
        pdf_url = "https://dl.acm.org/doi/pdf/10.1145/2462197.2462198"
        captured = []

        class FakeResponse:
            def json(self):
                return {
                    "statusCode": 200,
                    "url": pdf_url,
                    "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                    "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1145/2462197.2462198")

        self.assertEqual(len(captured), 1)
        self.assertTrue(captured[0]["httpResponseBody"])
        self.assertTrue(captured[0]["httpResponseHeaders"])
        self.assertNotIn("browserHtml", captured[0])
        self.assertEqual(response.url, pdf_url)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_falls_back_for_acm_pdf_strategies(self):
        pdf_url = "https://dl.acm.org/doi/pdf/10.1145/3373477.3373494"
        captured = []
        responses = [
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"<html>not pdf</html>").decode(),
            },
            {"status": 520, "detail": "ban-free response unavailable"},
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1145/3373477.3373494")

        self.assertEqual(len(captured), 3)
        self.assertNotIn("customHttpRequestHeaders", captured[0])
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "Accept", "value": "application/pdf,*/*"}],
        )
        self.assertEqual(
            captured[2]["customHttpRequestHeaders"],
            [
                {"name": "Accept", "value": "application/pdf,*/*"},
                {"name": "Referer", "value": "https://www.google.com/"},
            ],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_does_not_acm_route_epdf_or_showfmpdf(self):
        urls = [
            "https://dl.acm.org/doi/epdf/10.1145/2462197.2462198",
            "https://dl.acm.org/action/showFmPdf?doi=10.1145%2F2462197.2462198",
        ]

        for acm_url in urls:
            with self.subTest(url=acm_url):
                captured = {}

                def fake_call_with_zyte_api(url, params=None):
                    captured["url"] = url
                    captured["params"] = params
                    return {
                        "statusCode": 200,
                        "url": acm_url,
                        "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                        "httpResponseBody": base64.b64encode(b"<html>ACM shell</html>").decode(),
                    }

                with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
                    response = http_get(acm_url, doi="10.1145/2462197.2462198")

                self.assertEqual(captured["url"], acm_url)
                self.assertEqual(captured["params"]["url"], acm_url)
                self.assertNotIn("customHttpRequestHeaders", captured["params"])
                self.assertIsInstance(response.content, str)
                self.assertIn("ACM shell", response.content)

    def test_http_get_uses_pdf_body_strategy_for_acs_pdf(self):
        pdf_url = "https://pubs.acs.org/doi/pdf/10.1021/example"
        captured = []

        class FakeResponse:
            def json(self):
                return {
                    "statusCode": 200,
                    "url": pdf_url,
                    "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                    "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
                }

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1021/example")

        self.assertEqual(len(captured), 1)
        self.assertTrue(captured[0]["httpResponseBody"])
        self.assertTrue(captured[0]["httpResponseHeaders"])
        self.assertNotIn("browserHtml", captured[0])
        self.assertEqual(response.url, pdf_url)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_falls_back_for_acs_pdf_strategies(self):
        pdf_url = "https://pubs.acs.org/doi/pdf/10.1021/example"
        captured = []
        responses = [
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"<html>not pdf</html>").decode(),
            },
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.1021/example")

        self.assertEqual(len(captured), 2)
        self.assertNotIn("customHttpRequestHeaders", captured[0])
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "Accept", "value": "application/pdf,*/*"}],
        )
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_does_not_acs_route_epdf(self):
        epdf_url = "https://pubs.acs.org/doi/epdf/10.1021/example"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": epdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>ACS shell</html>").decode(),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(epdf_url, doi="10.1021/example")

        self.assertEqual(captured["url"], epdf_url)
        self.assertEqual(captured["params"]["url"], epdf_url)
        self.assertNotIn("customHttpRequestHeaders", captured["params"])
        self.assertIsInstance(response.content, str)
        self.assertIn("ACS shell", response.content)

    def test_http_get_falls_back_for_peerj_pdf_strategies(self):
        pdf_url = "https://peerj.com/articles/7168.pdf"
        captured = []
        responses = [
            {
                "statusCode": 400,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>not pdf</html>").decode(),
            },
            {
                "statusCode": 400,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(b"<html>still not pdf</html>").decode(),
            },
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi="10.7717/peerj.7168")

        self.assertEqual(len(captured), 3)
        self.assertNotIn("customHttpRequestHeaders", captured[0])
        self.assertEqual(
            captured[1]["customHttpRequestHeaders"],
            [{"name": "Accept", "value": "application/pdf,*/*"}],
        )
        self.assertEqual(
            captured[2]["customHttpRequestHeaders"],
            [
                {"name": "Accept", "value": "application/pdf,*/*"},
                {"name": "Referer", "value": "https://www.google.com/"},
            ],
        )
        self.assertEqual(response.url, pdf_url)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_rewrites_jbc_pdf_url_to_fulltext(self):
        self.assertEqual(
            jbc_fulltext_url_from_url("https://www.jbc.org/article/S0021-9258(17)43626-X/pdf"),
            "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext",
        )

    def test_rewrites_jbc_linkinghub_url_to_fulltext(self):
        self.assertEqual(
            jbc_fulltext_url_from_url("https://linkinghub.elsevier.com/retrieve/pii/S002192581743626X"),
            "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext",
        )

    def test_rewrites_jbc_doi_url_to_fulltext(self):
        self.assertEqual(
            jbc_fulltext_url_from_url("https://doi.org/10.1016/s0021-9258(17)43626-x"),
            "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext",
        )

    def test_does_not_rewrite_non_jbc_linkinghub_url(self):
        self.assertIsNone(
            jbc_fulltext_url_from_url("https://linkinghub.elsevier.com/retrieve/pii/S0140673624000012")
        )

    def test_rewrites_elsevier_journal_pdf_viewer_to_fulltext(self):
        self.assertEqual(
            elsevier_journal_fulltext_url_from_pdf_viewer(
                "https://www.gastrojournal.org/article/0016-5085(95)22767-9/pdf"
            ),
            "https://www.gastrojournal.org/article/0016-5085(95)22767-9/fulltext",
        )

    def test_ignores_non_elsevier_journal_pdf_viewer_url(self):
        self.assertIsNone(
            elsevier_journal_fulltext_url_from_pdf_viewer(
                "https://www.cell.com/cell-reports/pdf/S2211-1247(18)31646-2.pdf"
            )
        )

    def test_extracts_sciencedirect_article_url_from_query_pii(self):
        url = (
            "https://pdf.sciencedirectassets.com/286905/1-s2.0-S2238785424X00034/"
            "1-s2.0-S2238785424010007/main.pdf?hash=abc&pii=S2238785424010007"
        )

        self.assertEqual(
            sciencedirect_article_url_from_pdf_asset(url),
            "https://www.sciencedirect.com/science/article/pii/S2238785424010007",
        )

    def test_extracts_sciencedirect_article_url_from_pdf_path(self):
        url = (
            "https://pdf.sciencedirectassets.com/784962/3-s2.0-C20210009482/"
            "3-s2.0-B9780323999717050013/main.pdf?hash=abc"
        )

        self.assertEqual(
            sciencedirect_article_url_from_pdf_asset(url),
            "https://www.sciencedirect.com/science/article/pii/B9780323999717050013",
        )

    def test_ignores_non_sciencedirect_pdf_url(self):
        self.assertIsNone(sciencedirect_article_url_from_pdf_asset("https://example.org/article.pdf?pii=S123"))

    def test_http_get_rewrites_sciencedirect_pdf_asset_before_zyte(self):
        pdf_asset_url = (
            "https://pdf.sciencedirectassets.com/271370/1-s2.0-S0011916424X00132/"
            "1-s2.0-S0011916424005289/main.pdf?hash=abc&pii=S0011916424005289"
        )
        article_url = "https://www.sciencedirect.com/science/article/pii/S0011916424005289"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>ScienceDirect article</title>"
                    "<meta name=\"citation_title\" content=\"ScienceDirect article\"></head>"
                    "<body><article>Article landing page HTML.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(pdf_asset_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertEqual(response.url, article_url)
        self.assertIn("ScienceDirect article", response.content)

    def test_http_get_uses_browser_html_for_asme(self):
        article_url = "https://asmedigitalcollection.asme.org/PVP/proceedings/PVP2007/42878/379/324449"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": "https://asmedigitalcollection.asme.org/PVP/proceedings-abstract/PVP2007/42878/379/324449",
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>ASME article</title>"
                    "<meta name=\"citation_title\" content=\"ASME article\"></head>"
                    "<body><article>Article landing page HTML.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(
            response.url,
            "https://asmedigitalcollection.asme.org/PVP/proceedings-abstract/PVP2007/42878/379/324449",
        )
        self.assertIn("ASME article", response.content)

    def test_http_get_uses_browser_html_for_uq_espace(self):
        article_url = "https://espace.library.uq.edu.au/view/UQ:352154"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>UQ eSpace article</title>"
                    "<meta name=\"citation_title\" content=\"UQ eSpace article\"></head>"
                    "<body><article>Rendered repository item.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("UQ eSpace article", response.content)

    def test_http_get_uses_browser_html_for_preprints(self):
        article_url = "https://www.preprints.org/manuscript/202005.0515/v1"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>Preprints article</title>"
                    "<meta name=\"citation_title\" content=\"Preprints article\"></head>"
                    "<body><article>Rendered preprint landing page.</article></body></html>"
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(article_url)

        self.assertEqual(captured["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("Preprints article", response.content)

    def test_http_get_rewrites_jbc_linkinghub_to_fulltext_before_zyte(self):
        linkinghub_url = "https://linkinghub.elsevier.com/retrieve/pii/S002192581743626X"
        article_url = "https://www.jbc.org/article/S0021-9258(17)43626-X/fulltext"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": (
                    "PGh0bWw+PGhlYWQ+PHRpdGxlPkpCQyBhcnRpY2xlPC90aXRsZT48L2hlYWQ+"
                    "PGJvZHk+PGFydGljbGU+Sm91cm5hbCBvZiBCaW9sb2dpY2FsIENoZW1pc3RyeTwvYXJ0aWNsZT48L2JvZHk+PC9odG1sPg=="
                ),
            }

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(linkinghub_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertNotIn("browserHtml", captured["params"])
        self.assertEqual(response.url, article_url)
        self.assertIn("JBC article", str(response.content))

    def test_http_get_rewrites_elsevier_pdf_viewer_shell_to_fulltext(self):
        pdf_url = "https://www.gastrojournal.org/article/0016-5085(95)22767-9/pdf"
        fulltext_url = "https://www.gastrojournal.org/article/0016-5085(95)22767-9/fulltext"
        captured = []
        responses = [
            {
                "statusCode": 200,
                "url": pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    '<!DOCTYPE html><html><head><link rel="stylesheet" '
                    'href="chrome-extension://mhjfbmdgcfjbbpaeojofohoefgiehjai/pdf_embedder.css">'
                    "</head><body></body></html>"
                ),
            },
            {
                "statusCode": 200,
                "url": fulltext_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "httpResponseBody": base64.b64encode(
                    b"<html><head><title>Gastroenterology article</title></head>"
                    b"<body><article>Full article landing page text.</article></body></html>"
                ).decode(),
            },
        ]

        def fake_call_with_zyte_api(url, params=None):
            captured.append((url, params))
            return responses[len(captured) - 1]

        with patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(pdf_url, doi="10.1016/0016-5085(95)22767-9")

        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0][0], pdf_url)
        self.assertEqual(captured[1][0], fulltext_url)
        self.assertEqual(response.url, fulltext_url)
        self.assertIn("Gastroenterology article", str(response.content))

    def test_http_get_uses_browser_html_after_preprints_doi_redirect_even_when_head_403(self):
        doi_url = "https://doi.org/10.20944/preprints202005.0515.v1"
        article_url = "https://www.preprints.org/manuscript/202005.0515/v1"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>Preprints article</title>"
                    "<meta name=\"citation_title\" content=\"Preprints article\"></head>"
                    "<body><article>Rendered preprint landing page.</article></body></html>"
                ),
            }

        with patch(
            "openalex_taxicab.http_cache.resolve_doi_redirects",
            return_value={
                "final_url": article_url,
                "redirect_chain": [doi_url, article_url],
                "status_code": 403,
            },
        ), patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(doi_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("Preprints article", response.content)

    def test_http_get_uses_browser_html_after_mdpi_doi_redirect_even_when_head_403(self):
        doi_url = "https://doi.org/10.3390/app8030428"
        article_url = "https://www.mdpi.com/2076-3417/8/3/428"
        captured = {}

        def fake_call_with_zyte_api(url, params=None):
            captured["url"] = url
            captured["params"] = params
            return {
                "statusCode": 200,
                "url": article_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "text/html"}],
                "browserHtml": (
                    "<html><head><title>MDPI article</title>"
                    "<meta name=\"citation_title\" content=\"MDPI article\"></head>"
                    "<body><article>Rendered MDPI article with abstract.</article></body></html>"
                ),
            }

        with patch(
            "openalex_taxicab.http_cache.resolve_doi_redirects",
            return_value={
                "final_url": article_url,
                "redirect_chain": [doi_url, article_url],
                "status_code": 403,
            },
        ), patch("openalex_taxicab.http_cache.call_with_zyte_api", side_effect=fake_call_with_zyte_api):
            response = http_get(doi_url)

        self.assertEqual(captured["url"], article_url)
        self.assertEqual(captured["params"]["url"], article_url)
        self.assertTrue(captured["params"]["browserHtml"])
        self.assertTrue(captured["params"]["javascript"])
        self.assertFalse(captured["params"]["httpResponseBody"])
        self.assertEqual(response.url, article_url)
        self.assertIn("MDPI article", response.content)

    def test_http_get_uses_landing_page_session_for_journalajess_pdf_download(self):
        pdf_url = "https://journalajess.com/index.php/AJESS/article/download/1023/1998/1621"
        citation_pdf_url = "https://journalajess.com/index.php/AJESS/article/download/1023/1998"
        doi = "10.9734/ajess/2023/v47i31023"
        captured = []

        class FakeResponse:
            def __init__(self, data):
                self._data = data

            def json(self):
                return self._data

        responses = [
            {
                "url": "https://journalajess.com/index.php/AJESS/article/view/1023",
                "browserHtml": (
                    "<html><head>"
                    f"<meta name=\"citation_pdf_url\" content=\"{citation_pdf_url}\">"
                    "</head><body>AJESS article</body></html>"
                ),
            },
            {
                "statusCode": 200,
                "url": citation_pdf_url,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            },
        ]

        def fake_post(*args, **kwargs):
            captured.append(kwargs["json"])
            return FakeResponse(responses[len(captured) - 1])

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(pdf_url, doi=doi)

        self.assertEqual(len(captured), 2)
        self.assertEqual(captured[0]["url"], f"https://doi.org/{doi}")
        self.assertTrue(captured[0]["browserHtml"])
        self.assertTrue(captured[0]["javascript"])
        self.assertIn("session", captured[0])
        self.assertEqual(captured[1]["url"], citation_pdf_url)
        self.assertTrue(captured[1]["httpResponseBody"])
        self.assertEqual(captured[0]["session"], captured[1]["session"])
        self.assertEqual(response.url, citation_pdf_url)
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_http_get_fetches_erudit_pdf_directly(self):
        pdf_url = "https://www.erudit.org/en/journals/alterstice/2022-v11-n1-alterstice07243/1091893ar.pdf"
        captured = {}

        class FakeResponse:
            status_code = 200
            url = pdf_url
            content = b"%PDF-1.4\nbody\n%%EOF"
            headers = {"Content-Type": "application/pdf"}

        def fake_get(*args, **kwargs):
            captured["url"] = args[0]
            captured["headers"] = kwargs.get("headers")
            return FakeResponse()

        with patch("openalex_taxicab.http_cache.requests.get", side_effect=fake_get), patch(
            "openalex_taxicab.http_cache.requests.post",
            side_effect=AssertionError("Erudit PDF route should not call Zyte"),
        ):
            response = http_get(pdf_url, doi="10.7202/1091893ar")

        self.assertEqual(captured["url"], pdf_url)
        self.assertEqual(captured["headers"], {"Accept": "application/pdf,*/*"})
        self.assertEqual(response.url, pdf_url)
        self.assertEqual(response.headers["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF-"))


class NeurologyLandingPageRouteTests(unittest.TestCase):
    def test_neurology_pdf_urls_route_through_landing_page(self):
        for url in (
            "https://www.neurology.org/doi/pdfdirect/10.1212/WN9.0000000000000152",
            "https://www.neurology.org/doi/pdf/10.1212/WN9.0000000000000152",
            "https://n.neurology.org/content/94/15/e1620.full.pdf",
        ):
            with self.subTest(url=url):
                self.assertTrue(_should_use_landing_page_rewrite(url))

    def test_neurology_landing_pages_do_not_route(self):
        self.assertFalse(
            _should_use_landing_page_rewrite(
                "https://www.neurology.org/doi/10.1212/WN9.0000000000000152"
            )
        )

    def test_citation_pdf_url_upgraded_to_pdfdirect(self):
        # n.neurology.org/content/*.full.pdf -> landing page advertises /doi/pdf/,
        # which serves HTML; the session fetch must ask for /doi/pdfdirect/ instead.
        caller_url = "https://n.neurology.org/content/neurology/99/12/531.full.pdf"
        doi = "10.1212/wnl.0000000000201015"
        meta = f'<meta name="citation_pdf_url" content="https://www.neurology.org/doi/pdf/{doi}">'
        requested = []

        class FakeResponse:
            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        def fake_post(*args, **kwargs):
            body = kwargs["json"]
            requested.append(body["url"])
            if body.get("browserHtml"):
                return FakeResponse({"url": caller_url, "browserHtml": meta})
            return FakeResponse({
                "url": body["url"],
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            })

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(caller_url, doi=doi)

        self.assertEqual(requested[0], f"https://doi.org/{doi}")
        self.assertEqual(requested[1], f"https://www.neurology.org/doi/pdfdirect/{doi}")
        self.assertTrue(response.content.startswith(b"%PDF-"))

    def test_unlisted_host_pdf_url_does_not_route(self):
        self.assertFalse(
            _should_use_landing_page_rewrite(
                "https://www.frontiersin.org/articles/10.3389/fviro.2022.994843/pdf"
            )
        )


if __name__ == "__main__":
    unittest.main()


class CairnLegacyPdfUrlTests(unittest.TestCase):
    def test_legacy_load_pdf_urls_upgrade_to_shs_route(self):
        cases = {
            "https://www.cairn.info/load_pdf.php?ID_ARTICLE=CEP_043_0069&download=1":
                "https://shs.cairn.info/article/CEP_043_0069/pdf?lang=fr",
            "http://www.cairn.info/load_pdf.php?ID_ARTICLE=ENTIN_035_0051":
                "https://shs.cairn.info/article/ENTIN_035_0051/pdf?lang=fr",
            "https://cairn.info/load_pdf.php?download=1&ID_ARTICLE=E_A999_TI_43804210_c910":
                "https://shs.cairn.info/article/E_A999_TI_43804210_c910/pdf?lang=fr",
        }
        for legacy, expected in cases.items():
            with self.subTest(url=legacy):
                self.assertEqual(upgrade_cairn_legacy_pdf_url(legacy), expected)

    def test_other_cairn_urls_untouched(self):
        for url in (
            "https://shs.cairn.info/article/CEP_043_0069/pdf?lang=fr",
            "https://shs.cairn.info/revue-cahiers-d-economie-politique-1-2002-2-page-69?lang=fr",
            "https://www.cairn.info/article.php?ID_ARTICLE=CEP_043_0069",
            "https://doi.org/10.3917/cep.043.0069",
            "",
            None,
        ):
            with self.subTest(url=url):
                self.assertEqual(upgrade_cairn_legacy_pdf_url(url), url)

    def test_http_get_fetches_upgraded_url(self):
        legacy = "https://www.cairn.info/load_pdf.php?ID_ARTICLE=CEP_043_0069&download=1"
        expected = "https://shs.cairn.info/article/CEP_043_0069/pdf?lang=fr"
        requested = []

        class FakeResponse:
            def __init__(self, payload):
                self._payload = payload

            def json(self):
                return self._payload

        def fake_post(*args, **kwargs):
            body = kwargs["json"]
            requested.append(body["url"])
            return FakeResponse({
                "url": body["url"],
                "statusCode": 200,
                "httpResponseHeaders": [{"name": "Content-Type", "value": "application/pdf"}],
                "httpResponseBody": base64.b64encode(b"%PDF-1.7\nbody\n%%EOF").decode(),
            })

        with patch("openalex_taxicab.http_cache.requests.post", side_effect=fake_post):
            response = http_get(legacy, doi="10.3917/cep.043.0069")

        self.assertEqual(requested, [expected])
        self.assertEqual(response.url, expected)
        self.assertTrue(response.content.startswith(b"%PDF-"))
