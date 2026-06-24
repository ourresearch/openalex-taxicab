import json
import tempfile
import unittest
from pathlib import Path

from openalex_taxicab.eval_harness import (
    CATEGORIES,
    CATEGORY_BOT_BLOCK_403,
    CATEGORY_DOWNLOAD_404,
    CATEGORY_EMPTY_RESPONSE,
    CATEGORY_GOOD_HTML,
    CATEGORY_INVALID_CONTENT,
    CATEGORY_JS_REQUIRED,
    CATEGORY_MISSING_HARVEST,
    CATEGORY_PDF_INSTEAD_OF_HTML,
    CATEGORY_ROUTER_ONLY,
    CATEGORY_TAXICAB_ERROR,
    CATEGORY_TIMEOUT,
    ContentEvidence,
    classify_content,
    classify_lookup_payload,
    classify_reharvest_post,
    classify_uuid_download_error,
    make_transport_row,
    assess_browserbase_html,
    summarize_rows,
    write_artifacts,
)


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "eval"


class ClassifierTests(unittest.TestCase):
    def classify_fixture(self, name, content_type="text/html"):
        return classify_content(
            ContentEvidence(
                doi=f"fixture/{name}",
                publisher="fixture",
                resolved_url=f"https://example.org/{name}",
                content_type=content_type,
                body=(FIXTURE_DIR / name).read_bytes(),
            ),
            run_id="test",
        )

    def test_manifest_fixtures_match_expected_categories(self):
        manifest = json.loads((FIXTURE_DIR / "manifest.json").read_text())
        for item in manifest["fixtures"]:
            with self.subTest(item=item["file"]):
                row = self.classify_fixture(item["file"], item["content_type"])
                self.assertEqual(row.category, item["expected"])

    def test_weak_cloudflare_reference_is_not_bot_block(self):
        body = """
        <html><head><title>Real article</title>
        <meta name="citation_title" content="Real article"></head>
        <body><article><p>This is a real article page with enough text for extraction.
        It mentions a Cloudflare CDN URL in a script tag but it is not a challenge page.
        The rest of this paragraph is normal article content with authors, abstract-like
        text, and scholarly landing-page context.</p></article>
        <script src="https://static.cloudflareinsights.com/beacon.min.js"></script></body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_GOOD_HTML)

    def test_article_page_with_dx_doi_reference_is_not_router_only(self):
        body = """
        <html><head><title>Approach to the patient: reninoma</title>
        <meta name="citation_title" content="Approach to the patient: reninoma">
        <meta name="citation_author" content="Example Author">
        <meta name="citation_doi" content="10.1210/clinem/dgad516">
        </head><body><article><h1>Approach to the patient: reninoma</h1>
        <p>This Oxford Academic landing page contains real article content and references
        https://dx.doi.org/10.1210/clinem/dgad516 in metadata. The DOI link is a normal
        article identifier, not evidence that the response is a router stub.</p>
        <p>The article page has enough visible content for downstream extraction and should
        remain good HTML.</p></article></body></html>
        """
        row = classify_content(
            ContentEvidence(
                content_type="text/html",
                body=body,
                resolved_url="https://academic.oup.com/jcem/advance-article/doi/10.1210/clinem/dgad516/7255998",
            ),
            run_id="test",
        )
        self.assertEqual(row.category, CATEGORY_GOOD_HTML)

    def test_article_page_with_login_recaptcha_widget_is_not_bot_block(self):
        body = """
        <html><head><title>Megavoltage Irradiation in the Treatment of Carcinoma</title>
        <meta name="citation_title" content="Megavoltage Irradiation in the Treatment of Carcinoma">
        <meta name="citation_author" content="Example Author">
        </head><body><main><h1>Megavoltage Irradiation in the Treatment of Carcinoma</h1>
        <p>This landing page has article-level title, author metadata, and visible scholarly
        content. It also has a login widget that references recaptcha, but the page itself is
        not a captcha interstitial and remains usable for Taxicab retrieval evaluation.</p>
        <form><div class="g-recaptcha"></div></form></main></body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_GOOD_HTML)

    def test_article_page_with_perfdrive_reference_is_not_bot_block(self):
        body = """
        <html><head><title>The Electronic and Lattice Structures - IOPscience</title>
        <meta name="citation_title" content="The Electronic and Lattice Structures">
        <meta name="citation_author" content="Example Author">
        <meta name="citation_doi" content="10.1088/0253-6102/36/1/109">
        </head><body><article><h1>The Electronic and Lattice Structures</h1>
        <p>Abstract. This article page contains useful publisher landing-page content,
        citation metadata, authors, and enough visible scholarly text for downstream
        extraction. A bot-protection script reference appears in the returned page,
        but the article itself is present and usable.</p></article>
        <script src="https://validate.perfdrive.com/static/challenge.js"></script>
        </body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_GOOD_HTML)

    def test_article_page_with_enable_javascript_widget_is_not_js_required(self):
        body = """
        <html><head><title>Internalization choices under competition</title>
        <meta name="citation_title" content="Internalization choices under competition">
        <meta name="citation_author" content="Example Author">
        </head><body><main><h1>Internalization choices under competition</h1>
        <p>This publisher landing page contains article-level title, author metadata, and
        enough visible scholarly text for downstream extraction. It includes reader-widget
        copy that says enable JavaScript, but the returned HTML itself still exposes usable
        article metadata and content.</p>
        <aside>Please enable JavaScript for the enhanced reader experience.</aside>
        </main></body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_GOOD_HTML)

    def test_generic_404_page_is_not_good_html(self):
        filler = " ".join(["navigation search menu login"] * 80)
        body = """
        <html><head><title>Not Found | American Diabetes Association</title></head>
        <body><h1>404: This page could not be found.</h1>
        <p>The requested publisher page is unavailable.</p><p>{filler}</p></body></html>
        """.format(filler=filler)
        row = classify_content(
            ContentEvidence(content_type="text/html", body=body, resolved_url="https://diabetesjournals.org/CustomError"),
            run_id="test",
        )
        self.assertEqual(row.category, CATEGORY_INVALID_CONTENT)

    def test_cloudflare_520_page_is_not_browserbase_available(self):
        filler = " ".join(["browser working cloudflare working host error"] * 80)
        body = """
        <html><head><title>jaypeedigital.com | 520: Web server is returning an unknown error</title></head>
        <body><h1>Web server is returning an unknown error</h1>
        <p>Error code 520. Browser Working. Cloudflare Working. Host Error.</p>
        <p>{filler}</p></body></html>
        """.format(filler=filler)
        verdict = assess_browserbase_html(body, final_url="http://www.jaypeedigital.com/login.aspx")
        self.assertFalse(verdict["available"])
        self.assertEqual(verdict["verdict"], CATEGORY_INVALID_CONTENT)

    def test_article_page_that_mentions_404_is_still_good_html(self):
        body = """
        <html><head><title>HTTP failures in scholarly infrastructure</title>
        <meta name="citation_title" content="HTTP failures in scholarly infrastructure">
        <meta name="citation_author" content="Example Author"></head>
        <body><article><h1>HTTP failures in scholarly infrastructure</h1>
        <p>This real article discusses 404 Not Found and 520 errors as research objects.
        The returned landing page has article metadata, authors, and enough visible text
        for downstream extraction, so the error terminology is not itself a publisher
        error page.</p></article></body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_GOOD_HTML)

    def test_wolterskluwer_page_expired_is_not_browserbase_available(self):
        filler = " ".join(["product login expired session"] * 80)
        body = """
        <html><head><title>Page Expired</title>
        <meta name="robots" content="noindex, nofollow"></head>
        <body><h1>Page Expired</h1>
        <p>The page you are trying to access is no longer available.
        Please close the tab and open a new product Login page.</p>
        <p>{filler}</p></body></html>
        """.format(filler=filler)
        verdict = assess_browserbase_html(
            body,
            final_url="https://login.wolterskluwer.com/as/example/resume/as/authorization.ping",
        )
        self.assertFalse(verdict["available"])
        self.assertEqual(verdict["verdict"], CATEGORY_INVALID_CONTENT)

    def test_article_page_that_mentions_page_expired_is_still_good_html(self):
        body = """
        <html><head><title>Page expired errors in web archives</title>
        <meta name="citation_title" content="Page expired errors in web archives">
        <meta name="citation_author" content="Example Author"></head>
        <body><article><h1>Page expired errors in web archives</h1>
        <p>This real article discusses page expired errors as a research topic.
        The publisher landing page exposes citation metadata, authors, and enough
        visible article content for downstream extraction.</p></article></body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_GOOD_HTML)

    def test_anubis_enable_javascript_page_is_bot_block(self):
        body = """
        <html><head><title>Making sure you're not a bot!</title></head>
        <body><h1>Making sure you're not a bot!</h1>
        <p>Loading... You are seeing this because the administrator of this website
        has set up Anubis to protect the server against automated traffic. Please
        enable JavaScript to continue.</p></body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_BOT_BLOCK_403)

    def test_powered_and_protected_privacy_page_is_strong_bot_block(self):
        body = """
        <html><head><title></title><meta http-equiv="refresh" content="5"></head>
        <body><p>Powered and protected by Privacy</p></body></html>
        """
        row = classify_content(ContentEvidence(content_type="text/html", body=body), run_id="test")
        self.assertEqual(row.category, CATEGORY_BOT_BLOCK_403)

    def test_lookup_empty_is_missing_harvest(self):
        row, record = classify_lookup_payload(run_id="test", doi="10.1/a", lookup_json={"html": [], "pdf": [], "grobid": []})
        self.assertIsNone(record)
        self.assertEqual(row.category, CATEGORY_MISSING_HARVEST)

    def test_lookup_pdf_without_html_is_pdf_instead_of_html(self):
        row, record = classify_lookup_payload(run_id="test", doi="10.1/a", lookup_json={"html": [], "pdf": [{"id": "p"}], "grobid": []})
        self.assertIsNone(record)
        self.assertEqual(row.category, CATEGORY_PDF_INSTEAD_OF_HTML)

    def test_uuid_404_is_download_404(self):
        row = classify_uuid_download_error(run_id="test", doi="10.1/a", status_code=404)
        self.assertEqual(row.category, CATEGORY_DOWNLOAD_404)

    def test_reharvest_overlay_categories(self):
        self.assertEqual(
            classify_reharvest_post(run_id="test", doi="10.1/a", status_code=429).category,
            CATEGORY_BOT_BLOCK_403,
        )
        self.assertEqual(
            classify_reharvest_post(run_id="test", doi="10.1/a", status_code=None).category,
            CATEGORY_TIMEOUT,
        )
        self.assertEqual(
            classify_reharvest_post(run_id="test", doi="10.1/a", status_code=400).category,
            CATEGORY_INVALID_CONTENT,
        )
        self.assertEqual(
            classify_reharvest_post(run_id="test", doi="10.1/a", status_code=500).category,
            CATEGORY_TAXICAB_ERROR,
        )
        self.assertEqual(
            classify_reharvest_post(run_id="test", doi="10.1/a", status_code=200, payload={"is_soft_block": True}).category,
            CATEGORY_BOT_BLOCK_403,
        )

    def test_summary_invariant_and_artifacts(self):
        rows = [
            self.classify_fixture("good_article.html"),
            make_transport_row(run_id="test", doi="10.1/missing", category=CATEGORY_MISSING_HARVEST),
            make_transport_row(run_id="test", doi="10.1/timeout", category=CATEGORY_TIMEOUT),
        ]
        summary = summarize_rows(rows, run_id="test")
        self.assertEqual(summary["total"], 3)
        self.assertEqual(sum(summary["category_counts"].values()), 3)
        self.assertEqual(summary["good_html"], 1)
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_artifacts(rows, Path(tmp), run_id="test")
            for path in paths.values():
                self.assertTrue(path.exists())

    def test_all_categories_are_representable(self):
        represented = set(CATEGORIES)
        self.assertIn(CATEGORY_EMPTY_RESPONSE, represented)
        self.assertIn(CATEGORY_JS_REQUIRED, represented)
        self.assertIn(CATEGORY_ROUTER_ONLY, represented)


if __name__ == "__main__":
    unittest.main()
