"""oxjob #1402: HAL serves an Anubis proof-of-work page; it must count as a soft block so an
empty parse of it can never overwrite stored authors and affiliations."""
from openalex_taxicab.harvest import Harvester

ANUBIS = (
    b'<!doctype html><html lang="en"><head><title>Making sure you&#39;re not a bot!</title>'
    b'<script id="anubis_version" type="application/json">"devel"</script>'
    b'<script id="anubis_challenge" type="application/json">{"rules":{"algorithm":"fast"}}</script>'
)


def test_anubis_challenge_is_soft_block():
    h = Harvester.__new__(Harvester)
    assert h._check_soft_block(ANUBIS)


def test_ordinary_page_is_not_soft_block():
    h = Harvester.__new__(Harvester)
    assert not h._check_soft_block(b"<html><head><title>A paper</title></head><body>Anubis, god of the dead</body></html>")
