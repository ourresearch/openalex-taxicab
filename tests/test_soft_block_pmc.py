"""PMC bot checks must count as soft blocks. From 2026-04-17 to 2026-08-30 PMC served a Google
reCAPTCHA page (HTTP 200) in place of ~319K landing pages; each was stored as a clean fetch,
parsed to nothing, and never fetched again. PMC's PDF route can also answer with a
"Preparing to download" proof-of-work page."""
from pathlib import Path

from openalex_taxicab import harvest as harvest_mod
from openalex_taxicab.harvest import Harvester

FIXTURES = Path(__file__).parent / "fixtures" / "soft_block"


def _fixture(name):
    return (FIXTURES / name).read_bytes()


def _harvester():
    return Harvester.__new__(Harvester)


def test_pmc_recaptcha_page_is_soft_block():
    assert _harvester()._check_soft_block(_fixture("pmc_recaptcha_challenge.html"))


def test_pmc_recaptcha_page_as_str_is_soft_block():
    # http_get hands back decoded str for non-PDF bodies
    assert _harvester()._check_soft_block(_fixture("pmc_recaptcha_challenge.html").decode("utf-8"))


def test_pmc_pow_page_is_soft_block():
    assert _harvester()._check_soft_block(_fixture("pmc_pow_interstitial.html"))


def test_pmc_article_page_is_not_soft_block():
    assert not _harvester()._check_soft_block(_fixture("pmc_article_page.html"))


class _Resp:
    def __init__(self, content, url):
        self.content = content
        self.status_code = 200
        self.url = url


def test_harvest_does_not_store_pmc_recaptcha_page(monkeypatch):
    url = "https://pmc.ncbi.nlm.nih.gov/articles/PMC11883439/pdf/"
    body = _fixture("pmc_recaptcha_challenge.html").decode("utf-8")
    monkeypatch.setattr(harvest_mod, "http_get", lambda *a, **k: _Resp(body, url))
    h = _harvester()
    stored = []
    h._store_content = lambda *a, **k: stored.append(a)

    result = h.harvest(url, "oai:pubmedcentral.nih.gov:11883439", "pmh")

    assert result["is_soft_block"] is True
    assert result["status_code"] == 200
    assert stored == []
