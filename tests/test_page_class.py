"""Page classes: bot walls, login pages and empty app shells are not stored as successes (oxjob #1790).

Fixtures are minimal reconstructions of pages taxicab stored as 200s in Oct 2026 (#1790 EXPLORE § 3a)."""
import base64
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.modules.setdefault("unidecode", types.SimpleNamespace(unidecode=lambda value: value))
sys.modules.setdefault("magic", types.SimpleNamespace(Magic=lambda mime=True: types.SimpleNamespace(from_buffer=lambda content: "text/html")))

from openalex_taxicab import page_class
from openalex_taxicab.harvest import Harvester
from openalex_taxicab.http_cache import ResponseObject, http_get

ARTICLE = ("<html><head><title>Soil carbon in boreal forests | Journal of Soils</title>"
           "<meta name='citation_title' content='Soil carbon in boreal forests'></head><body>"
           + "<p>Abstract. Boreal soils store carbon.</p>" * 40 + "</body></html>")

BOT_WALLS = {
    "akamai bm-verify (MDPI)": "<html><head><meta http-equiv=\"refresh\" content=\"5; URL='/2073-4409/15/20/1889/pdf?bm-verify=AAQAAA'\" /><title>&nbsp;</title><script>var i = 1792222194;</script></head></html>",
    "cloudflare": "<html><head><title>Just a moment...</title></head><body><script>window._cf_chl_opt={cvId:'3'};</script></body></html>",
    "datadome": "<html><head><title>example.org</title></head><body><script src=\"https://ct.captcha-delivery.com/c.js\"></script></body></html>",
    "perimeterx": "<html><head><title>Access to this page has been denied</title></head><body><div id=\"px-captcha\"></div></body></html>",
    "imperva": "<html><head><title>Pardon Our Interruption</title></head><body>As you were browsing</body></html>",
    "bot detection (ucc.edu.co)": "<html><head><title>Bot Detection</title></head><body><h1>Please prove that you are Human before accessing this website</h1></body></html>",
    "incapsula block (SPIE)": "<html style=\"height:100%\"><head><META NAME=\"ROBOTS\" CONTENT=\"NOINDEX, NOFOLLOW\"><script src=\"/_Incapsula_Resource?SWJIYLWA=719d\"></script></head><body><iframe id=\"main-iframe\" src=\"/_Incapsula_Resource?SWUDNSAI=31&incident_id=1980\"></iframe></body></html>",
    "F5 TSPD challenge (ekb.eg)": "<!DOCTYPE html><html><head><script type=\"text/javascript\">(function(){ window[\"bobcmn\"] = \"1011111\"; })();</script></head><body></body></html>",
    "silverchair leastFactor (OUP)": "<html><head><script type=\"text/javascript\"><!-- function leastFactor(n) { if (isNaN(n)) return NaN; } function go() { document.cookie='KEY=1'; } --></script></head><body onload=\"go()\">Loading...</body></html>",
    "silverchair Validate User (ASH)": "<!DOCTYPE html><html lang=\"en\"><head><meta name=\"robots\" content=\"noindex, follow\" /><title>Validate User</title><link rel=\"icon\" href=\"//ash.silverchair-cdn.com/favicon.ico\"></head><body><div class=\"container\"><div id=\"captcha\"></div></div></body></html>",
}

# Chrome's PDF-viewer wrapper, byte for byte as stored (taxicab_id 06c7b772-59af-4ef2-8135-8ec37a6214e6, 271 bytes,
# cysticfibrosisjournal.com/article/<PII>/pdf): the URL served a PDF. Not a wall (125e840 got this wrong).
# Fastly's "Client Challenge", byte for byte as stored (taxicab_id 852b9cbe-6f03-42ac-a4fb-954efa9766ef,
# nature.com/articles/s44172-026-00794-2, 28 Oct 2026); the same 3,038 bytes on JSTOR, Springer, eLife, PyPI.
FASTLY_CHALLENGE = (Path(__file__).parent / "fixtures" / "soft_block" / "fastly_client_challenge.html").read_bytes()
# A normal page on a Fastly site loads /_fs-ch-<token>/ scripts too (every consultant360.com page, Oct 2026)
FASTLY_NORMAL_PAGE = ("<html><head><title>Acute Aortic Dissection | Consultant360</title>"
                      "<script src=\"/_fs-ch-1T1wmsGaOgGaSxcX/errors.js\"></script></head><body>"
                      + "<p>Case report text.</p>" * 40 + "</body></html>")

PDF_VIEWER = ("<!DOCTYPE html><html style=\"height:100%;width:100%\"><!-- the placeholder in the body style is for an "
              "optional background-color --><head></head><body style=\"height:100%;width:100%;overflow:hidden;margin:0;"
              "padding:0;background-color:rgb(40,40,40);\">\n    \n  \n\n</body></html>")

LOGINS = {
    "OJS login": "<html><head><title>Login</title></head><body><form action=\"https://journal.example.ma/index.php/x/login/signIn\"><input type=\"password\" name=\"password\"></form></body></html>",
    "Cairn": "<html><head><title>Connectez-vous ou créez un compte. | Cairn.info</title></head><body>" + "x" * 3000 + "</body></html>",
    "sign in with separator": "<html><head><title>Sign in - Example Press</title></head><body>Sign in to continue</body></html>",
    "J-STAGE": "<html><head><title>Sign in with subscription number</title></head><body><form>Subscription number</form></body></html>",
    "Bloomsbury": ("<html><head><title>collections-62</title><meta property=\"og:title\" content=\"A monograph\"></head><body>"
                   "<h1 aria-label=\"Log in to collections\" class=\"page-content-start\" id=\"pageStart\">Log in to Bloomsbury Collections</h1>"
                   + "<p>menu</p>" * 50 + "</body></html>"),
    # RSC's auto-posting OIDC sign-in form, as stored (994 bytes; state values shortened)
    "RSC OIDC login_required": ("<html><head><meta http-equiv='X-UA-Compatible' content='IE=edge' /><base target='_self'/></head>"
                                "<body><form method='post' action='https://pubs.rsc.org/ExternalAuthentication/OIDCLogin'>"
                                "<input type='hidden' name='error' value='login_required' /> <input type='hidden' name='state' "
                                "value='OpenIdConnect.AuthenticationProperties=6v_UJ' /><noscript><button>Click to continue"
                                "</button></noscript></form><script>window.addEventListener('load', function(){document.forms[0]"
                                ".submit();});</script></body></html>"),
}

SHELLS = {
    "DSpace 7": "<!DOCTYPE html><html><head><base href=\"/\"><title>DSpace</title></head><body><ds-app></ds-app><script src=\"main.js\" type=\"module\"></script></body></html>",
    "Primo VE": "<!doctype html><html><head><title>PrimoVeNde</title></head><body><script type=\"application/ld+json\"> </script><nde-app-root> </nde-app-root><script src=\"polyfills.js\"></script></body></html>",
    "Web of Science": "<!DOCTYPE html><html><head><title>Web of Science</title><script>window.x=1</script></head><body class=\"new-wos-style\"><app-wos class=\"mat-typography\"></app-wos><script src=\"main.js\"></script></body></html>",
    "TRDizin": "<!doctype html><html><head><title>TRDizin</title><noscript><link rel=\"stylesheet\" href=\"a.css\"></noscript></head><body><app-root></app-root></body></html>",
}


class ClassifyTests(unittest.TestCase):
    def test_article_page_is_html(self):
        self.assertEqual(page_class.classify(ARTICLE, "html", 200), "html")

    def test_pdf(self):
        self.assertEqual(page_class.classify(b"%PDF-1.7 ...", "pdf", 200), "pdf")

    def test_bot_walls(self):
        for name, body in BOT_WALLS.items():
            with self.subTest(name):
                self.assertEqual(page_class.classify(body, "html", 200), "bot_wall")
                self.assertTrue(page_class.is_bot_wall(body.encode()))

    def test_chrome_pdf_viewer_is_a_served_pdf_not_a_wall(self):
        self.assertEqual(len(PDF_VIEWER.encode()), 271)
        self.assertEqual(page_class.classify(PDF_VIEWER, "html", 200), "pdf_viewer")
        self.assertFalse(page_class.is_bot_wall(PDF_VIEWER))
        self.assertNotIn("pdf_viewer", page_class.NOT_STORED)

    def test_fastly_client_challenge_is_a_wall(self):
        self.assertEqual(len(FASTLY_CHALLENGE), 3038)
        self.assertEqual(page_class.classify(FASTLY_CHALLENGE, "html", 200), "bot_wall")
        self.assertTrue(page_class.is_bot_wall(FASTLY_CHALLENGE.decode("utf-8")))
        self.assertTrue(Harvester.__new__(Harvester)._check_soft_block(FASTLY_CHALLENGE))

    def test_fastly_strings_alone_are_not_walls(self):
        self.assertEqual(page_class.classify(FASTLY_NORMAL_PAGE, "html", 200), "html")
        titled = ARTICLE.replace("<title>Soil carbon in boreal forests | Journal of Soils</title>",
                                 "<title>Client Challenge</title>")
        self.assertEqual(page_class.classify(titled, "html", 200), "html")

    def test_wall_marker_counts_on_any_status_as_before(self):
        self.assertEqual(page_class.classify(BOT_WALLS["cloudflare"], "html", 403), "bot_wall")

    def test_akamai_202_and_redirect_walls(self):
        self.assertEqual(page_class.classify("<html></html>", "html", 202), "bot_wall")
        self.assertEqual(page_class.classify(ARTICLE, "html", 200, "https://www.fbi.gov/investigate"), "bot_wall")
        self.assertEqual(page_class.classify(ARTICLE, "html", 200, "https://muse.jhu.edu/verify?url=x"), "bot_wall")
        hangup = "https://scholarlypublications.universiteitleiden.nl/vdesk/hangup.php3"
        self.assertEqual(page_class.classify(ARTICLE, "html", 200, hangup), "bot_wall")

    def test_f5_big_ip_logout_page_is_a_wall(self):
        body = ("<html><head><meta name=\"robots\" content=\"noindex,nofollow\"><title>BIG-IP logout page</title>"
                "<link rel=\"stylesheet\" href=\"/public/include/css/apm.css\"></head><body>Your session could not "
                "be established.</body></html>")
        self.assertEqual(page_class.classify(body, "html", 200), "bot_wall")

    def test_other_statuses_are_errors(self):
        for status in (404, 410, 500, 503):
            self.assertEqual(page_class.classify("<html>gone</html>", "html", status), "error")

    def test_logins(self):
        for name, body in LOGINS.items():
            with self.subTest(name):
                self.assertEqual(page_class.classify(body, "html", 200), "login")

    def test_article_titles_that_start_like_logins_are_not_logins(self):
        for title in ("Login-free authentication for IoT devices", "Sign language acquisition in deaf children",
                      "Logistics of vaccine delivery"):
            with self.subTest(title):
                body = ARTICLE.replace("Soil carbon in boreal forests | Journal of Soils", title)
                self.assertEqual(page_class.classify(body, "html", 200), "html")

    def test_page_with_a_password_form_but_an_ordinary_title_is_html(self):
        body = ("<html><head><title>collections-62</title></head><body>Sign in to Your Personal Account"
                "<input type=\"password\">" + "<p>Chapter text.</p>" * 50 + "</body></html>")
        self.assertEqual(page_class.classify(body, "html", 200), "html")

    def test_shells(self):
        for name, body in SHELLS.items():
            with self.subTest(name):
                self.assertEqual(page_class.classify(body, "html", 200), "shell")

    def test_rendered_app_with_citation_meta_is_html(self):
        body = ARTICLE.replace("<body>", "<body><app-root></app-root>")
        self.assertEqual(page_class.classify(body, "html", 200), "html")

    def test_angular_page_with_metadata_in_og_and_json_ld_is_html(self):
        # taylorfrancis.com chapter page (25 Oct 2026): ~90 characters of visible text, an empty <router-outlet>,
        # no citation meta; title, authors and abstract sit in Open Graph, JSON-LD and the page-state JSON
        ld = ('{"@context":"https://schema.org","@type":"Chapter","name":"Getting to Know You",'
              '"author":[{"@type":"Person","name":"Nicki Newton"}],"description":"' + "Coaching math. " * 10 + '"}')
        og = '<meta property="og:title" content="Getting to Know You">'
        body = ("<html><head><title>Getting to Know You | 2 | Coaching Math Workshop | Nicki Newton | Taylor</title>"
                + og + "</head><body><a href=\"#main\">Skip to main content</a>"
                "<router-outlet _ngcontent-sc164=\"\"></router-outlet>"
                "<script type=\"application/ld+json\" id=\"jsonld\">" + ld + "</script>"
                "<script id=\"product-detail-page-state\" type=\"application/json\">{\"x\":1}</script></body></html>")
        self.assertEqual(page_class.classify(body, "html", 200), "html")
        # each signal is enough on its own, even next to a real app root
        with_root = body.replace("<router-outlet", "<app-root></app-root><router-outlet")
        self.assertEqual(page_class.classify(with_root.replace(og, ""), "html", 200), "html")       # JSON-LD
        self.assertEqual(page_class.classify(with_root.replace(ld, " "), "html", 200), "html")      # og:title
        self.assertEqual(page_class.classify(with_root.replace(og, "").replace(ld, " "), "html", 200), "shell")

    def test_router_outlet_alone_is_not_an_app_root(self):
        body = ("<html><head><title>Chapter</title></head><body><router-outlet></router-outlet>"
                "<script>window.state={}</script></body></html>")
        self.assertEqual(page_class.classify(body, "html", 200), "html")

    def test_empty_custom_element_inside_a_full_page_is_html(self):
        body = ("<html><head><title>A paper</title></head><body><mjx-assistive-mml></mjx-assistive-mml>"
                + "<p>Results and discussion of the experiment.</p>" * 20 + "</body></html>")
        self.assertEqual(page_class.classify(body, "html", 200), "html")


def fake_get(content, status=200, url="https://example.org/x"):
    def _get(u, **kwargs):
        return ResponseObject(content=content, headers=[{"name": "Content-Type", "value": "text/html"}],
                              status_code=status, url=url)
    return _get


class HarvestTests(unittest.TestCase):
    def setUp(self):
        self.h = Harvester(s3=MagicMock())
        self.h._store_content = MagicMock()

    def harvest(self, content, status=200, url="https://example.org/x"):
        with patch("openalex_taxicab.harvest.http_get", side_effect=fake_get(content, status, url)):
            return self.h.harvest(url, "10.1/x", "doi")

    def test_shell_is_reported_and_not_stored(self):
        r = self.harvest(SHELLS["Primo VE"])
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("shell", True))
        self.h._store_content.assert_not_called()

    def test_login_is_reported_and_not_stored(self):
        r = self.harvest(LOGINS["Cairn"])
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("login", True))
        self.h._store_content.assert_not_called()

    def test_article_is_stored(self):
        r = self.harvest(ARTICLE)
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("html", False))
        self.h._store_content.assert_called_once()

    def test_chrome_pdf_viewer_is_stored(self):
        r = self.harvest(PDF_VIEWER, url="https://www.cysticfibrosisjournal.com/article/S1569-1993(24)00001-0/pdf")
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("pdf_viewer", False))
        self.h._store_content.assert_called_once()

    def test_fastly_client_challenge_is_reported_and_not_stored(self):
        r = self.harvest(FASTLY_CHALLENGE, url="https://www.nature.com/articles/s44172-026-00794-2")
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("bot_wall", True))
        self.h._store_content.assert_not_called()

    NATURE = "https://www.nature.com/articles/s44172-026-00794-2"

    def harvest_zyte_then_direct(self, direct, fetch_mode=None):
        """Zyte answers Fastly's challenge; a direct fetch answers `direct` (a body, or an exception to raise)."""
        calls = []

        def _get(u, **kwargs):
            calls.append(kwargs.get("force_direct"))
            body = FASTLY_CHALLENGE if not kwargs.get("force_direct") else direct
            if isinstance(body, Exception):
                raise body
            return ResponseObject(content=body.decode() if isinstance(body, bytes) else body,
                                  headers=[{"name": "Content-Type", "value": "text/html"}], status_code=200, url=u)
        with patch("openalex_taxicab.harvest.http_get", side_effect=_get):
            return self.h.harvest(self.NATURE, "10.1038/s44172-026-00794-2", "doi", fetch_mode=fetch_mode), calls

    def test_fastly_challenge_on_zyte_is_fetched_directly(self):
        r, calls = self.harvest_zyte_then_direct(ARTICLE)
        self.assertEqual(calls, [False, True])
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("html", False))
        self.h._store_content.assert_called_once()

    def test_fastly_challenge_on_both_paths_is_a_soft_block(self):
        r, calls = self.harvest_zyte_then_direct(FASTLY_CHALLENGE)
        self.assertEqual(calls, [False, True])
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("bot_wall", True))
        self.h._store_content.assert_not_called()

    def test_failed_direct_fetch_keeps_the_soft_block(self):
        r, calls = self.harvest_zyte_then_direct(RuntimeError("connection reset"))
        self.assertEqual((r["page_class"], r["is_soft_block"]), ("bot_wall", True))
        self.h._store_content.assert_not_called()

    def test_direct_retry_is_not_fetched_twice(self):
        r, calls = self.harvest_zyte_then_direct(ARTICLE, fetch_mode="direct")
        self.assertEqual(calls, [True])

    def test_other_walls_are_not_fetched_directly(self):
        calls = []

        def _get(u, **kwargs):
            calls.append(kwargs.get("force_direct"))
            return ResponseObject(content=BOT_WALLS["cloudflare"], headers=[], status_code=200, url=u)
        with patch("openalex_taxicab.harvest.http_get", side_effect=_get):
            r = self.h.harvest(self.NATURE, "10.1038/x", "doi")
        self.assertEqual((calls, r["page_class"]), ([False], "bot_wall"))

    def test_akamai_202_is_a_soft_block(self):
        r = self.harvest("<html></html>", status=202)
        self.assertEqual((r["page_class"], r["is_soft_block"], r["status_code"]), ("bot_wall", True, 202))
        self.h._store_content.assert_not_called()


class DSpaceViaZyteTests(unittest.TestCase):
    URL = "https://repository.example.edu/handle/2440/13934"

    def zyte(self, body):
        return {"statusCode": 200, "url": self.URL, "httpResponseHeaders": [],
                "httpResponseBody": base64.b64encode(body.encode()).decode()}

    def test_dspace7_shell_from_zyte_gets_rest_api_metadata(self):
        synthesized = "<html><head><meta name=\"citation_title\" content=\"Tradition in Aspic\"></head></html>"
        with patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=self.zyte(SHELLS["DSpace 7"])), \
                patch("openalex_taxicab.http_cache._fetch_dspace7_metadata", return_value=synthesized) as rest:
            r = http_get(self.URL)
        rest.assert_called_once_with(self.URL)
        self.assertEqual(r.content, synthesized)
        self.assertEqual(page_class.classify(r.content, "html", r.status_code), "html")

    def test_dspace7_shell_without_rest_metadata_stays_a_shell(self):
        with patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=self.zyte(SHELLS["DSpace 7"])), \
                patch("openalex_taxicab.http_cache._fetch_dspace7_metadata", return_value=None):
            r = http_get(self.URL)
        self.assertEqual(page_class.classify(r.content, "html", r.status_code), "shell")

    def test_rendered_dspace_page_is_left_alone(self):
        rendered = "<html><body><ds-app><main>Item page " + "text " * 100 + "</main></ds-app></body></html>"
        with patch("openalex_taxicab.http_cache.call_with_zyte_api", return_value=self.zyte(rendered)), \
                patch("openalex_taxicab.http_cache._fetch_dspace7_metadata", side_effect=AssertionError("called")):
            r = http_get(self.URL)
        self.assertIn("Item page", r.content)


if __name__ == "__main__":
    unittest.main()
