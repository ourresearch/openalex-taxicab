# Taxicab next work for Codex and Claude

## Current Goal Update: 2026-06-28 Press Religacion Sidecar URL Correction

`/goal` is active for the 100-at-a-time Taxicab PDF/HTML improvement loop.
Use the correct repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
Do not use `/Users/shubh-trips/Documents/openalex-taxicab`.

Durable runner: `scripts/taxicab_batch_e2e.py`.

Latest residual sidecar URL check: one fresh `press.religacion.com` row was
tested from the current residual queue. The file had an old PDF-looking catalog
view URL that returned 404 HTML through Zyte and direct source checks. The DOI
landing page is live, and the matching chapter PDF viewer exposes a current
download URL that returns real PDF bytes. A bounded live Taxicab re-harvest with
that current download URL passed: Taxicab stored a real PDF and useful HTML,
and Parseland extracted useful article data. No Taxicab code changed. Treat
this as a sidecar URL correction, not a route-code candidate. Public oxjobs
artifact:
`evidence/report461-pressreligacion-sidecar-url-summary-20260628.json`.

Latest residual sidecar URL check: one fresh `qu.edu.iq` row was tested from
the current residual queue. The file had an old PDF-looking URL that returned
404 through every Zyte strategy. Direct source checks showed the DOI landing
page is live and exposes a current PDF link on `qjes.qu.edu.iq`. A bounded live
Taxicab re-harvest with that current PDF link passed: Taxicab stored a real PDF
and Parseland extracted useful article data. No Taxicab code changed. Treat
this as a sidecar URL correction, not a route-code candidate. Public oxjobs
artifact: `evidence/report461-qu-edu-iq-sidecar-url-summary-20260628.json`.

Latest residual broken-link review check: one fresh `ruslang.ru:81` row was
tested from the current residual queue. The file had a PDF-looking URL, but
Zyte no-storage probes returned 404 for every strategy. Direct source checks
showed the candidate PDF path and DOI landing path both return 404 HTML, and
the page did not expose a replacement PDF link. A bounded live Taxicab
re-harvest passed when treated as no public PDF expected: Taxicab did not store
a PDF. Parseland did not extract useful article data because the source path is
broken. No Taxicab code changed. Treat this as a sidecar/review correction, not
a route-code candidate. Public oxjobs artifact:
`evidence/report461-ruslang-broken-link-review-summary-20260628.json`.

Latest residual review check: one fresh `pulmonarychronicles.com` row was tested
from the current residual queue. The file had a PDF-looking download URL, but
Zyte no-storage probes, direct source checks, and Browserbase all reached HTML
instead of PDF bytes. A bounded live Taxicab re-harvest passed when treated as
no public PDF expected: Taxicab did not store a PDF. When the source URL was
also re-harvested, Taxicab stored useful HTML and Parseland extracted useful
article data. No Taxicab code changed. Treat this as a sidecar/review
correction, not a route-code candidate. Public oxjobs artifact:
`evidence/report461-pulmonarychronicles-review-summary-20260628.json`.

Latest residual provider/access check: one fresh `research.aota.org` public-PDF
row was tested from the current residual queue. Zyte no-storage provider probes
recovered 0/1 PDFs: PDF-byte strategies returned empty/provider 520 responses,
and browser HTML landed on sign-in/article HTML. Direct source checks hit
Cloudflare HTML instead of PDF bytes. Browserbase reached the article page and
reported a download-start signal, but captured 0/1 valid PDF bytes. No Taxicab
code changed. Treat this as provider/access evidence for Zyte support or a
future download-capture recipe, not a route-code candidate. Public oxjobs
artifact: `evidence/report461-aota-provider-access-summary-20260628.json`.

Latest residual PDF recovery: one fresh `sba.org.br` public-PDF row was tested
from the current residual queue. Zyte no-storage provider probes recovered
0/1 PDFs: every strategy ended as empty response, timeout, or provider 520.
Direct source checks showed the SBA OJS article-download path serves public PDF
bytes. Taxicab now fetches only SBA OJS article-download PDF URLs directly;
article HTML still uses the existing route. Deployed commit `794971b` passed a
bounded live one-row re-harvest: Taxicab stored a real PDF, stored useful HTML,
and Parseland extracted useful article data. This is a narrow Taxicab PDF
recovery, not a broad route change. Public oxjobs artifact:
`evidence/report461-sba-ojs-direct-pdf-recovery-summary-20260628.json`.

Latest residual broken-link review check: one fresh `platform.almanhal.com`
REVIEW row was tested from the current residual queue. The file had a
PDF-looking file URL, but no-storage Zyte saw a 404 for that file path and
direct source checks returned empty 202 responses instead of PDF bytes. A
bounded live Taxicab re-harvest passed when treated as no public PDF expected:
Taxicab did not store a PDF. Taxicab did store HTML, and Parseland extracted
useful data from that HTML, although the simple HTML guard did not mark the
page as useful. This is a broken-link review correction, not a Taxicab scraper
fix. Public oxjobs artifact:
`evidence/report461-platform-almanhal-broken-link-summary-20260628.json`.

Latest residual paywall/order review check: one fresh `poj.peeters-leuven.be`
REVIEW row was tested from the current residual queue. The file had an
article/download-style URL, but Zyte and direct source checks returned Peeters
article/order HTML instead of PDF bytes. A bounded live Taxicab re-harvest
passed when treated as no public PDF expected: Taxicab did not store a PDF, did
store useful HTML, and Parseland extracted useful data. This is a review
correction, not a Taxicab scraper fix. Public oxjobs artifact:
`evidence/report461-poj-peeters-paywall-review-summary-20260628.json`.

Latest residual login-only review check: one fresh
`revistaeclesiasticabrasileira.itf.edu.br` REVIEW row was tested from the
current residual queue. The file had a PDF-looking download URL, but both Zyte
and direct source checks reached a login page instead of PDF bytes. A bounded
live Taxicab re-harvest passed when treated as no public PDF expected: Taxicab
did not store a PDF, did store useful HTML, and Parseland extracted useful data.
This is a login-only review correction, not a Taxicab scraper fix. Public
oxjobs artifact:
`evidence/report461-revistaeclesiastica-login-review-summary-20260628.json`.

Latest residual sidecar URL check: one fresh `revistas.unisucre.edu.co` REVIEW
row was tested from the current residual queue. The file pointed at an article
view page that resolves to a BunkerWeb bot challenge, not PDF bytes. Direct
source checks showed the matching download URL returns a real PDF. A bounded
live Taxicab re-harvest with that download URL stored a valid PDF, but the HTML
record still landed on the challenge page and Parseland did not extract useful
article data. This is a sidecar URL correction for PDF plus a separate
HTML/provider challenge lane. Public oxjobs artifact:
`evidence/report461-revistas-unisucre-sidecar-url-summary-20260628.json`.

Latest residual sidecar URL check: one fresh `revistas.usp.br` REVIEW row was
tested from the current residual queue. The file pointed at an article view
page, not the real PDF download. Direct source checks showed the view page has a
working PDF download link. A bounded live Taxicab re-harvest with that download
link stored a valid PDF, and Parseland extracted useful article data. This is a
sidecar URL correction candidate, not a Taxicab PDF route-code candidate. Public
oxjobs artifact:
`evidence/report461-revistas-usp-sidecar-url-summary-20260628.json`.

Latest residual login-only review check: one fresh `revistas.uva.es` REVIEW row
was tested from the current residual queue. The file had an old PDF link that
now returns 404. Direct source checks showed the current article/download paths
resolve to a login page. A bounded live Taxicab re-harvest passed when treated
as no public PDF expected: Taxicab did not store a PDF and did store useful
HTML. This is a login-only review correction candidate, not a Taxicab PDF
route-code candidate. Public oxjobs artifact:
`evidence/report461-revistas-uva-login-review-summary-20260628.json`.

Latest residual sidecar review check: one fresh `scholarhub.ui.ac.id` REVIEW
row was tested from the current residual queue. The file has a public-looking
PDF link. A normal direct request hit 403, but the article page exposes the PDF
link and Zyte recovered valid PDF bytes through the existing ScholarHub
strategy. A bounded live Taxicab re-harvest stored a valid PDF, and Parseland
extracted useful article data. This is sidecar review evidence, not a Taxicab
PDF route-code candidate. Public oxjobs artifact:
`evidence/report461-scholarhub-sidecar-review-summary-20260628.json`.

Latest residual sidecar URL check: one fresh `qjes.qu.edu.iq` REVIEW row was
tested from the current residual queue. The file had an old PDF link that now
returns 404. Direct source checks showed the current DOI landing page exposes a
live PDF. A bounded live Taxicab re-harvest with the current PDF link stored a
valid PDF, and Parseland extracted useful article data. This is a sidecar URL
correction candidate, not a Taxicab PDF route-code candidate. Public oxjobs
artifact: `evidence/report461-qjes-sidecar-url-summary-20260628.json`.

Latest residual review check: one fresh `radab.uomosul.edu.iq` REVIEW row was
tested from the current residual queue. The no-storage Zyte provider probe
recovered `0/1` valid PDFs; every strategy returned `download_404` for the
guessed PDF-like URL. Direct source checks showed the DOI resolves to a live
article HTML page, but the page exposes no real PDF link; the only PDF wording
is a site metric. A bounded live Taxicab re-harvest stored useful HTML and found
no PDF. Parseland returned 200 but did not extract useful data from that HTML.
This is a review/label correction candidate, not a Taxicab PDF route-code
candidate. Public oxjobs artifact:
`evidence/report461-radab-review-summary-20260628.json`.

Latest residual provider check: one fresh `recordsofzsi.com` row was tested
from the current residual queue. The no-storage Zyte provider probe recovered
`0/1` valid PDFs: direct PDF-byte strategies returned Zyte 520 empty responses,
and browser HTML returned a Cloudflare-style security verification page.
Browserbase also recovered `0/1` valid PDFs; it saw the protected flow and the
download did not produce captured PDF bytes. A bounded live Taxicab re-harvest
found useful HTML and live Parseland extracted useful article data plus a
PDF-looking link, but the PDF harvest returned no stored PDF. This is provider
or access-flow evidence, not a Taxicab route-code candidate. Public oxjobs
artifact: `evidence/report461-recordsofzsi-provider-summary-20260628.json`.

Latest residual REVIEW check: `rfc-editor.org` was selected from the latest
fresh one-row residual queue. No-storage Zyte provider probe
`rfc-editor-provider-probe1-8638e7d` recovered `0/1` valid PDFs; every strategy
hit `download_404` on the guessed PDF link. Direct source checks showed the
guessed PDF and the obvious PDF variant both return 404, while the RFC text
record and DOI landing page return 200. A live one-row Taxicab -> Parseland
check, treating the row as no public PDF expected, passed: Taxicab found useful
HTML, found no PDF, and Parseland extracted useful data. This is a label/review
correction, not a Taxicab route-code candidate. Public oxjobs artifact:
`evidence/report461-rfc-editor-review-summary-20260628.json`.

Next exact command:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
python3 - <<'PY'
import csv
from pathlib import Path
p=Path('pdf_eval_runs/residual-clusters-after-roguescholar-consciousbeam-bbrc-15f0c0b/residual-subclusters.csv')
for row in csv.DictReader(p.open()):
    if row.get('priority_band') == 'probe_next':
        print(row['rank'], row['host'], row['path_pattern'])
PY
```

Batch 100 used:

```bash
python3 scripts/taxicab_batch_e2e.py \
  --batch-number 100 \
  --batch-size 100 \
  --out batch_e2e_runs \
  --workers 2 \
  --timeout 90 \
  --reharvest
```

Batch 100 result:

```text
total rows: 100
ready rows: 73
review rows: 27
passes: 68
failures: 5
score on ready rows: 93.15%
public PDF rows: 27/27 Taxicab found real PDFs
Taxicab found real PDFs: 36
useful Taxicab HTML rows: 78
useful Parseland rows: 92
```

Cumulative batches 001-100:

```text
total rows: 10,000
ready rows: 6,915
review rows: 3,085
passes: 6,451
failures: 464
score on ready rows: 93.29%
public PDF rows: 2,504/2,514 Taxicab found real PDFs
Taxicab found real PDFs: 3,119
useful Taxicab HTML rows: 7,841
useful Parseland rows: 8,569
```

The 10K batch loop is now covered end to end. Ten public-PDF attention rows
remain across all 10,000 rows. Batch 100 added zero public-PDF misses; its five
scored failures are label mismatches where Taxicab found real PDFs even though
the sidecar says no public PDF. Local row details are in
`batch_e2e_runs/batch-001/rows.csv` through `batch_e2e_runs/batch-100/rows.csv`.

Batch 100 had 100 Taxicab lookups return HTTP 200 and zero DNS errors. Parseland
returned HTTP 200 for 98 rows, one 500, and one blank response. Batch 097 had one
rejected first attempt after a local DNS burst caused 51 lookup failures; that
bad run was moved aside and not published.

The batch 088 unknown-host miss was inspected on 2026-06-26: the direct source
PDF returned 403 HTML locally, and Taxicab/Zyte `/test-zyte` returned a 520 empty
provider response. Treat it as provider/source evidence unless a later check
finds reachable PDF bytes. Public oxjobs gets aggregate counts only.

Next exact command:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/oxjobs
python3 scripts/publish-report.py 461
```

After publishing this final 10K batch summary, the next work is to inspect the
remaining public-PDF attention rows plus the label mismatches that Taxicab
already recovered. Do not publish raw DOI rows, raw URLs, cookies, signed URLs,
screenshots, or HTML.


Post-batch fix: the IJST/SciResOL public-PDF attention row was a real PDF with
harmless blank bytes before `%PDF-`. Taxicab now accepts that as real PDF bytes
in the eval helper, batch runner, provider probe, Browserbase evidence path, MIME
guessing, and harvest PDF validation. Commit `2886639` was pushed to `main`,
deployed through ECS, and verified with a one-row live `--reharvest` run against
the load balancer. The deployed service returned `good_pdf`, `application/pdf`,
504,015 bytes, and no validation errors. Treat this as a focused validator and
harvest PDF-byte fix, not a broad publisher route change. Public-PDF attention
rows move from 10 to 9 after this targeted check; rerun the relevant batch or
full loop if you need a refreshed batch-run snapshot.

Follow-up attention recheck on deployed commit `3e600ad`: a bounded 10-row live
`--reharvest` run recovered 5/10 current attention rows as `good_pdf`. Two more
rows pass when using the PDF links found from the Taxicab HTML through Parseland,
so those are sidecar URL fixes, not Taxicab scraper fixes. The remaining three
problem classes are: one ScienceDirect/JMRT row where the provider response is
non-PDF bytes, one OSF row where the download is a Word document rather than a
PDF, and one source-host row returning 403 HTML. Keep DOI/URL details local.

No-storage Zyte provider probe for the remaining three recovered 0/3 valid PDFs.
Best categories: ScienceDirect/JMRT returned Zyte ban/HTML responses, OSF returned
non-PDF Office bytes, and the remaining source host returned Zyte ban/empty
responses. Next action: prepare provider/source evidence for ScienceDirect and
the source host, and correct the OSF sidecar label so a Word document is not
counted as a public PDF.

<!-- TAXICAB_PDF_CURRENT_HANDOFF_START -->
## Current PDF Handoff: 2026-06-24 JPET Browserbase Gold Evidence

Active repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`. Do not use `/Users/shubh-trips/Documents/openalex-taxicab`. Active branch: `codex/taxicab-pdf-gold-availability`, pushed at `15486c5` before this JPET Browserbase handoff refresh. Taxicab `main` already contains the PDF Phase 2 lead merge at `8b364865525a904ba517c63da9aa91d413570075`; no production scraping behavior changed in this slice.

Latest accepted full 10K read-only gate remains `taxicab-pdf-after-cambridge-cache-6386430`: `2,464/6,293 good_pdf` (`39.15%`) on the legacy guessed-PDF denominator, `+1` versus the prior accepted gate, with `0` good-to-non-good regressions, `0` timeouts, and `0` Taxicab errors. The legacy raw 95% target is `5,979/6,293`, so the raw gap is `3,515` rows.

Denominator state: `6,293` is a legacy guessed-PDF-candidate denominator, not proof that every row has a public full-text PDF. Current full-corpus draft counts remain public TRUE `2,514`, public FALSE `4,407`, REVIEW `3,079`, and all-known-PDF TRUE `3,185`. Draft public TRUE rows score `2,464/2,514` (`98.01%`), but this is provisional because the `3,079` REVIEW rows are unresolved.

Latest JPET REVIEW evidence slice: private exact-host no-storage Zyte run `jpet-review-pack-provider5-23d755e` sampled `5` `jpet.aspetjournals.org` rows from the private top-250 REVIEW pack and recovered `0/5` valid PDFs; best category was `js_redirect_unresolved=5`. Follow-up Browserbase session run `jpet-review-browserbase-gold5-15486c5` also captured `0/5` valid PDFs, with `html_not_pdf=5`. Private overlay joined all five rows and made `0` status or denominator changes. Public aggregate assets `evidence/report461-jpet-review-provider-overlay-summary-23d755e.json` and `evidence/report461-jpet-review-browserbase-summary-15486c5.json` are published in oxjobs #461 at commit `261f04eee`; CI run `28076823234` passed and the live raw report/assets were verified after route retry. Accepted sidecar counts are unchanged until the private overlay is reviewed and adopted.

Recent REVIEW evidence, newest first: `jpet.aspetjournals.org` stayed REVIEW after Zyte plus Browserbase (`0/5` valid PDFs; Browserbase `html_not_pdf=5`); `cell.com` stayed REVIEW after Zyte plus Browserbase (`0/5` valid PDFs; Browserbase `download_started_not_captured=2`, `html_not_pdf=3`); `journals.ametsoc.org` found four public TRUE candidates and one paywall/login candidate; `eurekaselect.com` stayed REVIEW (`0/5`, `bot_block_403=5`); `actahort.org` stayed REVIEW (`0/5`, `js_redirect_unresolved=5`); `pdcnet.org` stayed REVIEW (`0/5`, `js_redirect_unresolved=5`); `sk.sagepub.com` stayed REVIEW (`0/5`, `js_redirect_unresolved=5`); `karger.com` stayed REVIEW (`0/5`, `html_instead_of_pdf=5`); `jamanetwork.com` found two paywall/login candidates and three remaining REVIEW rows. Older no-movement samples remain REVIEW unless a private overlay is explicitly reviewed and adopted.

Review-pack top hosts already sampled for denominator evidence include `api.taylorfrancis.com`, `jstor.org`, `pubs.acs.org`, `degruyterbrill.com`, `journals.lww.com`, `spiedigitallibrary.org`, `thieme-connect.de`, `pubs.rsc.org`, `tandfonline.com`, `pubs.aip.org`, `link.aps.org`, `doi.org`, `opg.optica.org`, `brill.com`, `journals.uchicago.edu`, `journals.sagepub.com`, `aip.scitation.org`, `iopscience.iop.org`, `thelancet.com`, `nature.com`, `asmedigitalcollection.asme.org`, `jamanetwork.com`, `karger.com`, `sk.sagepub.com`, `pdcnet.org`, `actahort.org`, `eurekaselect.com`, `journals.ametsoc.org`, `jpet.aspetjournals.org`, and `cell.com`.

Aggregate inspection of the private top-250 REVIEW pack found no new exact-host candidates after excluding already-sampled hosts and hosts with substantial prior evidence. Next exact work is AMETSOC overlay review/adoption or provider-guided recipe work; do not rerun known lanes unless testing a new provider-advised recipe or a specific denominator question.

Secret and evidence rule: never print or commit API keys, cookies, signed URLs, Browserbase session JSON, screenshots, HTML, private exact-host CSVs, provider `rows.ndjson`, raw DOIs, or raw URLs. Oxjobs gets aggregate counts only.

Next exact command:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab && python3 - <<'PY'
import json
from pathlib import Path
p = Path('/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/data/merged-FINAL-pdf-availability-overlay-ametsoc-review-pack-provider5-8594e9f.json')
data = json.loads(p.read_text())
print(json.dumps({
    'changed_total': data.get('changed_total'),
    'status_transitions': data.get('status_transitions'),
    'public_denominator_transitions': data.get('public_denominator_transitions'),
    'all_known_pdf_denominator_transitions': data.get('all_known_pdf_denominator_transitions'),
    'input': data.get('input', {}).get('public_denominator_counts'),
    'output': data.get('output', {}).get('public_denominator_counts'),
}, indent=2, sort_keys=True))
PY
```

Required checks before the next Taxicab push: `python3 -m unittest discover -s tests`, `python3 scripts/taxicab_pdf_eval.py --fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke`, `git diff --check`, and the configured secret scan. For oxjobs pushes, run `python3 scripts/publish-report.py 461`, `git diff --check -- working/taxicab-pdf`, the secret scan, GitHub Actions, and public raw report verification.
<!-- TAXICAB_PDF_CURRENT_HANDOFF_END -->

Last updated: 2026-06-24 UTC.

This file is the handoff contract for Taxicab retrieval-quality work. Read it
before doing new work. Keep it current before ending a long session. For the
current goal, `GOAL.md` is the concise control file and this file is the
expanded operational context.

## Current goal

```text
HTML Phase 1: complete, target hit at 9,583/10,000 good_html (95.83%).
PDF Phase 2 /goal: active, target >=95% good_pdf on pdf_expected_total.

Current handoff override: accepted full 10K PDF gate
`taxicab-pdf-after-cambridge-cache-6386430` is 2,464/6,293
`good_pdf` (39.15%), +1 versus the prior accepted public TRUE cache gate and
+627 versus the first measured denominator reference. It has 0 timeout,
0 `taxicab_error`, and 0 good-to-non-good regressions. Draft public TRUE is
2,464/2,514 (98.01%) but provisional until 3,079 REVIEW rows are resolved. The
Cambridge bounded recovery moved one sampled REVIEW row to public TRUE/all-known
TRUE after full-gate preservation. The current handoff block above is
authoritative; older entries below are historical.
Older entries including Revistas, Revmed/PLOS, OSTI/PLOS, provider snapshots,
and DOI.org cleanup are historical; prior `3c125878f`
publishes the aggregate-only
Elsevier DOI.org residual-priority correction; prior `77d71e78f` publishes the aggregate-only AMS
negative provider/gold evidence and residual priority-map refresh; prior `386f5fa73` publishes the aggregate-only ASM/JVI
mixed provider evidence and residual priority-map refresh; prior `d054e3d`
publishes the aggregate-only AAP residual
priority-map refresh; prior
`1cba3fc` publishes the AAP Pediatrics provider/gold check; prior `01be98e`
publishes the Transcript Verlag preview-provider confirmation; prior `10ec3eeb` publishes the
unknown-attribution DOI.org numeric JS-redirect gold check; prior `03560e2a`
publishes the unknown-attribution DOI.org JS-redirect
duo gold check; prior `1727a6ac` publishes the BCSJ/Oxford Academic DOI.org
JS-redirect gold check; prior `5c29deb5` publishes the AAAS Science.org gold
check; prior `0e59e67f`
publishes the PeerJ branch evidence; prior `0f9fcaa2` publishes the current
Elsevier DOI.org Browserbase recheck; prior `58d55a98`
publishes the scrubbed AHA/Lippincott summary asset, `07bc9d9f` publishes the
AHA/Lippincott gold check in the report, and `4984229f` publishes the
graph-first minimalist report. The OSTI/PLOS movement is bounded cache/reharvest
lift plus query-preserving provider-probe harness correction, not a Taxicab-main
production scraping push.
Current Taxicab branch commit `56d2c2c` adds Zyte browser `networkCapture`
PDF-body decoding to `scripts/provider_pdf_probe.py`. The first corrected
Springer no-storage recipe probe
`springer-network-capture-probe3b-56d2c2c` recovered 0/3 `good_pdf`
(two target-site 429s, one unresolved JS redirect), so it is provider/support
evidence only and does not justify Taxicab route code.
Follow-up `degruyter-network-capture-probe3-d178c76` tested a broader `pdf`
network-capture token against three current De Gruyter Brill
`/document/doi/.../pdf` rows and recovered 0/3 `good_pdf`; all three returned
405 text/html captcha evidence. This is also provider/support evidence only.
Follow-up `lippincott-network-capture-probe3-84b519f` tested three current
Lippincott `journals.lww.com` rows and recovered 0/3 `good_pdf`; outcomes were
two unresolved JS redirects and one 403 bot block. This is also
provider/support evidence only.
Follow-up `oxford-network-capture-probe3-bea12c4` tested three current Oxford
Academic `academic.oup.com` rows and recovered 0/3 `good_pdf`; outcomes were
two `html_instead_of_pdf` PDF-viewer/html shells and one 403 bot block. This is
also provider/support evidence only.
Follow-up `ssrn-network-capture-probe3-03cffc3` tested three current SSRN
`papers.ssrn.com` rows and recovered 0/3 `good_pdf`; all three responses were
200 `image/svg+xml` payloads classified as `corrupt_or_truncated_pdf`, not PDF
bytes. This is also provider/support evidence only.
Follow-up `aip-pubs-network-capture-probe3-next` tested three current AIP
Publishing `pubs.aip.org` rows and recovered 0/3 `good_pdf`; outcomes were two
403 bot blocks and one `html_instead_of_pdf` PDF-viewer/html shell. This is
also provider/support evidence only.
Follow-up `jstor-network-capture-probe3-next` tested three current JSTOR
`jstor.org` rows and recovered 0/3 `good_pdf`; every row returned 200
`text/html` article/book page content, not PDF bytes. This is also
provider/support evidence only.
Follow-up `brill-network-capture-probe3-next` tested three current Brill
`brill.com` rows and recovered 0/3 `good_pdf`; every row returned 405
`text/html` human-verification content. This is also provider/support evidence
only.
Follow-up `springer-network-wait-capture-probe3-c767a1d` tested a
docs-derived browser `networkCapture` recipe with a short `waitForTimeout`
against three current Springer `link.springer.com` rows and recovered 0/3
`good_pdf`: one tiny JSON body classified as corrupt/truncated, one unresolved
JS/router-like HTML page, and one interstitial/paywall HTML page. This is
provider/support evidence only; a blind browser wait before capture is not
enough evidence for Taxicab route code.

The current NetworkCapture sweep is 0/24 across Springer, De Gruyter Brill,
Lippincott, Oxford Academic, SSRN, AIP Publishing, JSTOR, and Brill. The
Springer wait-capture variant makes the follow-through 0/27 sampled rows. The
private ignored-local Zyte packet is
`pdf_eval_runs/zyte-provider-ticket-networkcapture-0of24-1001461/`. A local
residual refresh at `/tmp/taxicab-pdf-residual-refresh-after-networkcapture`
found top-240 priority bands are all `provider_lane_do_not_duplicate`.

Next exact command:
```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
python3 scripts/provider_pdf_probe.py \
  --input pdf_eval_runs/pdf-full10k-after-osti-plos-ee9001b/rows.ndjson \
  --category missing_pdf_harvest \
  --publisher <publisher> \
  --host <host> \
  --limit 3 \
  --recipe-file <ignored-zyte-recipe.json> \
  --strategies <strategy_name> \
  --out /tmp/taxicab-pdf-probes \
  --run-id <provider>-zyte-advised-probe3
```
The AHA/Lippincott one-row lane
`www.ahajournals.org:/doi/pdf/:doi/:id` recovered 0/1 through Zyte no-storage
provider probing and 0/1 through Browserbase gold evidence; Browserbase reached
a 403 challenge and ended `download_started_not_captured`. No Taxicab
POST/R2/DynamoDB writes occurred, no route code was written, and no production
behavior changed. The current Elsevier DOI.org Browserbase recheck
`elsevier-doi-browserbase-gold5-5d5d0fc` recovered 0/5, with four
`download_started_not_captured` verdicts and one `html_not_pdf`; it is
negative provider/gold evidence, not route-code evidence. Earlier oxjobs commit
`0e59e67f` also records PeerJ branch evidence from Taxicab commit `bf1632f`:
branch replay recovered 1/1 current PeerJ `html_instead_of_pdf` residual,
preserved 1/1 already-good PeerJ row with 0 regressions, and did not recover
the remaining PeerJ `missing_pdf_harvest` row. This is branch evidence only,
not an accepted KPI lift or Taxicab main push. Oxjobs commit `5c29deb5`
records AAAS Science.org gold evidence from Taxicab commit `53d3704`: Zyte
recovered 0/1, Browserbase recovered 0/1, and Browserbase ended
`html_not_pdf` on `www.science.org`. Earlier oxjobs commit
`1727a6ac` records BCSJ/Oxford Academic gold evidence from Taxicab commit
`897c742`: Zyte recovered 0/1, Browserbase recovered 0/1, and Browserbase
ended `html_not_pdf` on `academic.oup.com`. Earlier oxjobs commit
`03560e2a` records unknown-attribution DOI.org JS-redirect duo gold evidence
from Taxicab commit `a25417e`: Zyte recovered 0/2, Browserbase recovered 0/2,
and Browserbase ended `html_not_pdf` on aggregate PNAS and University of
Chicago hosts. Oxjobs commit `10ec3eeb` records unknown-attribution DOI.org
numeric JS-redirect gold evidence from Taxicab commit `d4ed55b`: Zyte recovered
0/1, Browserbase recovered 0/1, and Browserbase ended `html_not_pdf` on
aggregate Mediasphera host evidence. Public summary:
`working/taxicab-pdf/evidence/report461-unknown-doiorg-numeric-jsredirect-gold-summary-d4ed55b.json`.
Oxjobs commit `01be98e` records Transcript Verlag preview-provider evidence
from Taxicab commit `1587acb`: Zyte recovered 0/4 current
`supplement_or_preview_pdf` rows, PDF-byte strategies stayed
`supplement_or_preview_pdf`, and browser HTML returned `html_instead_of_pdf`.
Public summary:
`working/taxicab-pdf/evidence/report461-transcript-preview-provider-probe4-summary-1587acb.json`.
Oxjobs commit `1cba3fc` records AAP Pediatrics provider/gold evidence from
Taxicab branch commit `9399eb7`: Zyte recovered 0/1, direct PDF-byte strategies
stayed `js_redirect_unresolved`, Zyte browser HTML reached
`interstitial_or_paywall`, Browserbase recovered 0/1, and Browserbase ended
`html_not_pdf` on aggregate AAP article-abstract host evidence. Public summary:
`working/taxicab-pdf/evidence/report461-aappediatrics-htmlpdf-gold-summary-9399eb7.json`.
Earlier oxjobs commit
`74a062c6` publishes the aggregate-only
Wiley PDF-direct validator/provider Zyte recheck from Taxicab commit `9b01df6`:
0/10 recovered, no Taxicab POST/R2/DynamoDB writes, no production behavior
change, and no accepted KPI change.

Browserbase credential state: `BROWSERBASE_API_KEY` exists in ignored
`/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/.env`;
`BROWSERBASE_PROJECT_ID` is optional for the current REST session path.
Browserbase is evidence/gold only and must not overwrite Taxicab baseline
categories. AWS state: default AWS CLI and `.env.aws` session credentials are
expired, but AWS is not required for the immediate no-storage Zyte/Browserbase
evidence loop.

Current lane state: ACS/ACM/Wiley/IOP/bioRxiv PDF route families, Elsevier
DOI.org, AHA/Lippincott, AAAS, BCSJ/Oxford, and the unknown DOI.org
JS-redirect duo plus numeric JS-redirect lane, and Transcript Verlag preview
URLs, AAP Pediatrics, ASM/JVI, and AMS are provider-lane, gold-first,
validator, or do-not-duplicate until a narrow/provider-advised recipe exists.
The residual-priority rule now handles Elsevier DOI.org before the generic DOI
resolver gold-first rule, so the 15-row Elsevier DOI.org `missing_pdf_harvest`
lane is correctly demoted to `provider_lane_do_not_duplicate`.
AMS is closed as negative provider/gold evidence: Zyte no-storage recovered 0/1
with four 520 empty responses, Browserbase recovered 0/1 with `html_not_pdf`,
and no Taxicab POST/R2/DynamoDB writes or route code changes occurred. Local
residual refresh `residual-clusters-after-elsevier-doi-demote-2f627f4` moves
the Elsevier DOI.org lane, AMS, mixed ASM/JVI evidence, and prior
validator/gold lanes to do-not-duplicate where appropriate; top-240
subcluster-entry priority bands are 217 provider-lane/do-not-duplicate, 19
Browserbase/Zyte-gold-first, and 4 validator/provider. Top-240 `probe_next`
remains 0, and
`confirm_existing_branch_candidate` remains 0.
Oxjobs #461 commit `3c125878f` publishes the aggregate-only Elsevier DOI.org
residual-priority correction and refreshed queue.
Prior residual refresh `residual-clusters-after-closed-doi-demote-1d50d45`
demotes closed publisher DOI.org, unknown DOI.org, validator/provider, and
PeerJ branch-only lanes; top-240 subcluster-entry priority bands are 238
provider-lane/do-not-duplicate and 2 Browserbase/Zyte-gold-first. Oxjobs #461
commit `5a1254630` publishes the aggregate-only cleanup. Latest residual refresh
`residual-clusters-after-osti-plos-ee9001b` has top-240 all
provider-lane/do-not-duplicate after OSTI/PLOS recovery.

Next exact action: use
`working/taxicab-pdf/evidence/zyte-support/pdf-provider-lanes-after-osti-plos-ee9001b.md`
as the aggregate provider-support handoff, then test only provider-advised
PDF-byte recipes through no-storage probes before route code. Use
`python3 scripts/provider_pdf_probe.py --recipe-file <ignored-recipe.json> --strategies <recipe_name> ...`
for provider recipes; recipe probes must not call `/taxicab` POST or write
R2/DynamoDB. Taxicab branch commit `d761c59` adds the private ignored-local
provider-ticket builder. Use
`python3 scripts/build_pdf_provider_ticket.py --run-id zyte-provider-ticket-after-osti-plos-ee9001b --top-lanes 25 --samples-per-lane 3`
when Zyte needs DOI-level examples; the latest local packet is
`pdf_eval_runs/zyte-provider-ticket-after-osti-plos-ee9001b/`. Do not commit or
publish that raw packet; oxjobs stays aggregate-only. Do not repeat
OSTI/PLOS as fresh route/provider work unless testing provider-advised
guidance.
AHA/Lippincott and Elsevier DOI.org are closed as negative gold evidence for
now; PeerJ is closed as branch-only evidence until full-gate proof exists; AAAS,
BCSJ/Oxford, the unknown DOI.org JS-redirect duo, and the unknown DOI.org
numeric JS-redirect lane are closed as negative provider/gold evidence.
Transcript Verlag preview URLs are closed as candidate-quality/provider
evidence, AAP Pediatrics is closed as negative provider/gold evidence, and
ASM/JVI is closed as mixed non-repeatable provider evidence. AMS is closed as
negative provider/gold evidence. Do not duplicate those lanes unless a
provider-advised recipe appears.
Do not promote SAGE, Wiley, ACS, IOP, bioRxiv/CSHLP, Elsevier DOI.org,
rank-39 DOI.org, ACM, IngentaConnect, ICE Virtual Library, Ecologica, the
closed top-five Browserbase sample, ASTM Compass, CCCC, Atlantis Press,
IWA/AMPP/Sage Knowledge/RSNA/AJOG/Elgar, broad Elsevier article-PDF lanes,
Wiley PDF-direct, or any new lane without a narrower or provider-advised
recipe. Do not run another duplicate fresh-tail loop. Do not push Taxicab main
before full PDF 95% proof.

Historical sections below may use "current" relative to older gates; this top
block is authoritative.
```

Next exact command:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
python3 - <<'PY'
import json
from pathlib import Path
rows = json.loads(Path('pdf_eval_runs/residual-subclusters.json').read_text())['top_subclusters']
for row in rows:
    if row.get('priority_band') == 'provider_lane_do_not_duplicate':
        continue
    print(row.get('count'), row.get('priority_band'), row.get('prior_evidence_status'), row.get('category'), row.get('publisher'), row.get('host'), row.get('candidate_source'), row.get('path_pattern'))
PY
```

Current gate: structured PDF parser is implemented at Taxicab commit `a61d34b`;
oxjobs #461 commit `dcb7bb14` publishes the accepted structured-parser full
gate. Current read-only refresh `pdf-full10k-publisher-attribution-e584811` at
Taxicab commit `8a35869` is 2,196/6,293 `good_pdf` (34.90%), with 3,805
missing, 65 corrupt/truncated, 0 timeout, 0 `taxicab_error`, and a 3,783-row
gap to 95%; oxjobs #461 commit `ebe97f4d` publishes the sanitized full-gate
report. Current no-storage provider probes published so far: Springer
`84760121`, Wiley `3480ae82`, Elsevier `68c2eb46`, De Gruyter `b04396d6`,
Lippincott `40cf1b9e`, Oxford `d4b6da1b`, CUP/Cambridge `38844dea`, Taylor
`af13892d`, SSRN `2c171c7e`, JSTOR `463bb712`, AIP Publishing `14f254ac`,
RSC `e3621c28`, RSC larger `84f1c8ea`, ACS `21a7697c`, Brill `e2bac29b`, Thieme `4838bd1c`, SPIE
`fe048cca`, BMJ `6de28ec3`, Sage `d059488d`, AMA/JAMA `eddf9c5a`, Karger
`69b2780a`, APS `5da73adb`, APS larger `5435e2c7`, ACM `88c2fddb`, Optica `f57bad44`, IOP
`bd7396fb`, IOP all-current `51b4665a`, and IOP route validation `c3c9b0ac`.
AIP Publishing probe `aip-publishing-current-missing-provider-probe10-af746d4`
recovered 0/10; best categories were 6 `js_redirect_unresolved`, 3
`interstitial_or_paywall`, and 1 `html_instead_of_pdf`. Keep these residual
missing clusters in the provider/Zyte PDF-byte, click-download, or
candidate-discovery lane unless a later probe finds a narrow, regression-tested
route-code candidate. RSC probe `rsc-current-missing-provider-probe10-f709792`
recovered 1/10 through `google_referer`; larger confirmation
`rsc-current-missing-provider-probe25-05b1a38` recovered 0/25 at Taxicab
`05b1a38` and is published at oxjobs `84f1c8ea`. Best categories were 24
`js_redirect_unresolved` and 1 `html_instead_of_pdf`, so RSC stays in the
Zyte/provider support lane before route code. ACS probe `acs-current-missing-provider-probe10-7e4b5e5`
recovered 0/10; every best category was `js_redirect_unresolved`, with one
PDF-accept empty response, one Google-referer empty response, and one browser
HTML bot block. Brill probe `brill-current-missing-provider-probe10-88bc77f`
recovered 0/10; every best category and all 40 strategy attempts were
`bot_block_403`. Thieme probe `thieme-current-missing-provider-probe10-3f45c6a`
recovered 0/10; every best category and all 40 strategy attempts were
`js_redirect_unresolved`. SPIE probe `spie-current-missing-provider-probe10-9fa4596`
recovered 0/10; every best category and all 40 strategy attempts were
`js_redirect_unresolved`. BMJ probe `bmj-current-missing-provider-probe10-9ccfeaf`
recovered 2/10 current missing rows, but larger confirmation
`bmj-current-missing-provider-probe25-622512f` recovered only 1/25; residuals
were 15 `bot_block_403`, five `interstitial_or_paywall`, three
`js_redirect_unresolved`, and one `html_instead_of_pdf`. Sage probe
`sage-current-missing-provider-probe10-1f57c9b` recovered 0/10 current missing
rows; best categories were six `bot_block_403` and four
`js_redirect_unresolved`. AMA/JAMA probe
`ama-current-missing-provider-probe10-2198bc2` recovered 0/10 current missing
rows; best categories were five `interstitial_or_paywall`, four
`js_redirect_unresolved`, and one `bot_block_403`. Karger probe
`karger-current-missing-provider-probe10-4427b24` recovered 0/10 current
missing rows; every best category was `html_instead_of_pdf`. APS probe
`aps-current-missing-provider-probe10-cf3d845` recovered 1/10 current missing
rows through `google_referer`; residual best categories were nine
`js_redirect_unresolved`. ACM probe
`acm-current-missing-provider-probe10-dba7e2f` recovered 1/10 current missing
rows through `default_body`/`google_referer`; residuals were seven
`html_instead_of_pdf`, one `js_redirect_unresolved`, and one `download_404`.
Optica probe `optica-current-missing-provider-probe10-1b0823d` recovered 0/10
current missing rows; best categories were eight `js_redirect_unresolved` and
two `html_instead_of_pdf`, while browser HTML returned eight interstitial/paywall
rows. IOP, ACM, and ACS now have branch-only route evidence; none moves the accepted KPI until a read-only/full gate confirms durable records. IOP route validation is published at oxjobs `c3c9b0ac`; ACM route validation is published at oxjobs `695fb51d`; ACS route validation is published at oxjobs `82e4812f`. Latest residual clustering found 3,989 non-good rows across 174 clusters. Current corrupt no-storage probes from that full gate found Wiley 9/18 recovered, ACS 6/6 recovered, Sage 0/6 recovered, Hindawi 0/2 recovered, Springer 0/5 recovered, Elsevier-attributed 0/3 recovered, unknown-attribution 0/5 recovered, unknown `revistas.uach.cl` 0/1 recovered, unknown `journal.uniga.ac.id` 1/1 recovered, unknown `sciresol.s3.us-east-2.amazonaws.com` 0/1 recovered, unknown `oejournal.org` 0/1 recovered, unknown `authorea.com` 0/1 recovered, and unknown `mjle.journals.ekb.eg` 0/1 recovered. Hindawi `hindawi-current-corrupt-provider-probe2-6d11e24` is published at oxjobs `66cc6c44` as support evidence; Springer `springer-current-corrupt-provider-probe5-6d11e24` is published at oxjobs `79f0b3d2` as support evidence; Elsevier-attributed `elsevier-current-corrupt-provider-probe3-d1f3edb` is published at oxjobs `f57d9036` as support/cluster evidence; unknown-attribution `unknown-current-corrupt-provider-probe5-9b795af` is published at oxjobs `ffb66370` as host-splitting evidence; unknown `revistas.uach.cl` `unknown-revistasuach-current-corrupt-provider-probe1-48f425c` is published at oxjobs `37926446` as candidate-discovery/support evidence; unknown `journal.uniga.ac.id` `unknown-journaluniga-current-corrupt-provider-probe1-f52b57e` is published at oxjobs `aec51cf8` as positive provider-strategy evidence; unknown `sciresol.s3.us-east-2.amazonaws.com` `unknown-sciresol-current-corrupt-provider-probe1-7a00e39` is published at oxjobs `ca6e5e05` as validator/provider-byte evidence; unknown `oejournal.org` `unknown-oejournal-current-corrupt-provider-probe1-815a979` is published at oxjobs `42da202d` as provider/support evidence; unknown `authorea.com` `unknown-authorea-current-corrupt-provider-probe1-d1106f7` is published at oxjobs `b405108f` as provider/support evidence; unknown `mjle.journals.ekb.eg` `unknown-mjle-current-corrupt-provider-probe1-60ac8e3` is published at oxjobs `b6a214a5` as provider/support evidence. The current unknown singleton tail is exhausted. Candidate-host residual clustering is published at oxjobs `65411a6c` from Taxicab `a230505`; top concrete hosts include link.springer.com 813, onlinelibrary.wiley.com 544, degruyterbrill.com 199, sciencedirect.com 143, and api.taylorfrancis.com 52. Taylor API host-specific probe `taylor-api-current-missing-provider-probe10-a230505` is published at oxjobs `48ffd7d9`: 0/10 good_pdf and all 40 attempts download_404. Taylor direct TandF probe `taylor-tandfonline-current-missing-provider-probe10-ae2655d` is published at oxjobs `cca3d122`: 0/10 good_pdf, 9 interstitial/paywall, and 1 JS redirect. Next exact action is Taylor/Zyte provider guidance or Browserbase gold comparison before route code. Do not push Taxicab main before the full PDF 95% proof.
Confirmation-path decision: remote `--reharvest` tests deployed Taxicab main,
not this branch; local branch `Harvester` with real env credentials can write
production R2/DynamoDB, so do not use local branch writes as a silent
confirmation path. Continue with no-storage branch evidence until the PDF 95%
gate is ready for main.
Latest accepted full-gate confirmation published to oxjobs #461: read-only run
`pdf-full10k-after-readable-encrypted-f2da963` at Taxicab `f2da963` accepted
2,304/6,293 `good_pdf` (36.61%), +99 versus the prior accepted full gate. The
run has 3,796 `missing_pdf_harvest`, 65 corrupt/truncated, 4 encrypted/unreadable,
93 supplement/preview, 0 timeout, and 0 `taxicab_error`. The 95% gap is now
3,675 rows. This is measurement/validator-only: readable encrypted PDFs count as
`good_pdf` only when they have EOF, nonzero pages, and at least 500 extracted
text characters. Oxjobs commit `2092c008` publishes the safe summary/report.
Residual clustering from this full gate is complete. The largest remaining lane
is missing PDF harvest by source PDF URL host: Springer 813, Wiley 544,
De Gruyter 199, Elsevier/ScienceDirect 143, Lippincott 133, Oxford 132, CUP
122, SSRN 73, JSTOR 60, Taylor 52, RSC 47, and ACS 47. The actionable
non-missing lane is smaller but cleaner: Wiley corrupt/truncated recovered 9/18
with PDF-byte strategies, ACS corrupt/truncated recovered 6/6, and Sage
corrupt/truncated recovered 0/6. Current branch implements only ACS
`pubs.acs.org/doi/pdf/...` through PDF-byte strategies and leaves ACS
`/doi/epdf/` on the normal path. Local no-storage branch `http_get` validation
`acs-http-get-local-route-precommit-8912673` returned 6/6 `good_pdf`, with no
Taxicab POST/R2/DynamoDB writes. Treat Wiley as partial/provider-support plus
route validation, and Sage as provider/Zyte support evidence.
Previously published Nature/Oxford provider probes remain provider/Zyte support
lanes, not route-code candidates: Nature recovered 0/15 and Oxford recovered
1/25 only through a `sciengine.com` candidate, with `academic.oup.com` 0/23.
Follow-up no-storage probes: Wiley `/doi/pdf/` as-is recovered 0/10
(`js_redirect_unresolved` 8, `html_instead_of_pdf` 1, `bot_block_403` 1);
rewriting the same sample to `/doi/pdfdirect/` recovered only 2/10, including
one DOI-mismatch PDF; Springer `link.springer.com/content/pdf/` recovered 0/10
(`interstitial_or_paywall` 5, `js_redirect_unresolved` 3, `bot_block_403` 2).
These are provider/support evidence, not production route-code candidates.
PDF Phase 2: active on codex/taxicab-pdf-phase2, target >=95% good_pdf.
PDF denominator: pdf_expected_total from the 10K Goldie/OpenAlex corpus, with all-10K context reported separately.
Current tooling slice: generic no-storage provider probing in `scripts/provider_pdf_probe.py`. It reads full-gate rows or CSV queues, sanitizes URLs, tests named Zyte strategies, and writes local probe artifacts without Taxicab POST/R2/DynamoDB writes. Provider probe summaries now choose the best non-good category per DOI instead of defaulting to the first attempted strategy; this is measurement/reporting-only. Taylor API and direct TandF no-storage probes are both complete and negative; next exact action is to test only a Zyte-advised Taylor PDF-byte recipe or Browserbase gold comparison before route code.
IOP residual probe `iop-corrupt-provider-probe-3-31663bc` recovered 0/3 PDFs: one PerfDrive/captcha block and two corrupt application/pdf responses with no page objects. Treat residual IOP as Zyte/support or validator triage, not route code.
J-STAGE corrupt-provider probe `jstage-corrupt-provider-probe-3b-31663bc` recovered 0/3 residual corrupt PDFs: two application/pdf responses still had no page objects and one row timed out empty; browser HTML returned PDF-viewer shells. Treat this as Zyte binary-mode or validator-byte triage before any route-code change.
J-STAGE encrypted-provider probe `jstage-encrypted-provider-probe-3-31663bc` recovered 0/3 residual encrypted/unreadable PDFs: default body reached application/pdf bytes for all three rows but every response stayed `encrypted_or_unreadable_pdf`; browser HTML returned PDF-viewer shells. Treat this as legacy/encrypted PDF handling or validator-byte triage.
J-STAGE missing/provider subtype probes, Wiley residual probes, current publisher probes, IOP/ACM route validations, ACS route validation, Hindawi support evidence, Springer corrupt support evidence, Elsevier-attributed corrupt support evidence, unknown-attribution corrupt host-splitting evidence, the unknown `revistas.uach.cl` singleton, the unknown `journal.uniga.ac.id` singleton, the unknown `sciresol` singleton, the unknown `oejournal.org` singleton, the unknown `authorea.com` singleton, and the unknown `mjle.journals.ekb.eg` singleton are already recorded above. The unknown singleton tail is exhausted, candidate-host residual clustering is published at oxjobs `65411a6c`, Taylor API host-specific probing is published at oxjobs `48ffd7d9`, Taylor direct TandF probing is published at oxjobs `cca3d122`, and the next non-duplicate Taylor action is provider-advised PDF-byte recipe testing or Browserbase gold comparison before route code.
```

HTML main-sync commit `07c974e taxicab: sync phase 1 eval context` is pushed
to Taxicab `origin/main`. The current Taxicab branch is
`codex/taxicab-pdf-phase2`. Oxjobs #461 `taxicab-pdf` exists and has a report
scaffold pushed to oxjobs `main`. The PDF offline harness slice now has
passing tests and fixture smoke. The PDF read-only GET path also has a
5-row live smoke against the load balancer with 0 timeouts and 0 Taxicab errors.
The first limit-100 read-only baseline completed with 1/100 `good_pdf`.
That run exposed an eval bug: the classifier decoded only the first 256KB for
text scanning and then checked `%%EOF` inside that truncated slice. The
corrected EOF validator checks the complete byte body. The corrected limit-100
run is 15/100 `good_pdf`, 77 `missing_pdf_harvest`, 5
`corrupt_or_truncated_pdf`, two `encrypted_or_unreadable_pdf`, one
`bot_block_403`, and 0 `timeout` / 0 `taxicab_error`. Treat the 1/100 -> 15/100
lift as measurement correctness, not production scraping behavior.

The PDF runner now has a thread-local concurrent read-only path. Local worker
tests pass and live smoke with `--workers 4` produced 3/5 `good_pdf`,
2 `missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`.

The full 10K read-only PDF baseline completed on Taxicab commit `22b78b7`:
2,148/10,000 `good_pdf` (21.48%), gap 7,352 rows to 95%, 7,230
`missing_pdf_harvest`, 453 `corrupt_or_truncated_pdf`, 121
`encrypted_or_unreadable_pdf`, 13 `html_instead_of_pdf`, 13
`js_redirect_unresolved`, 11 `supplement_or_preview_pdf`, 9
`interstitial_or_paywall`, 2 `bot_block_403`, 0 timeout, and 0
`taxicab_error`. This is the raw all-10K denominator; denominator enrichment is
still needed before claiming a final PDF-expected KPI.

Denominator enrichment is now implemented locally: rows with empty `PDF URL`
and no explicit `Resolves To PDF=TRUE` become `no_pdf_expected` without hitting
Taxicab. Limit-100 denominator check: `pdf_expected_total=65`, 13/65
`good_pdf` (20.00%), 35 `no_pdf_expected`, 0 timeout, 0 `taxicab_error`.

The denominator-enriched full 10K baseline is complete:
1,837/6,293 `good_pdf` (29.19%), 3,707 `no_pdf_expected`, 3,939
`missing_pdf_harvest`, 373 `corrupt_or_truncated_pdf`, 102
`encrypted_or_unreadable_pdf`, 11 `html_instead_of_pdf`, 11
`js_redirect_unresolved`, 10 `supplement_or_preview_pdf`, 8
`interstitial_or_paywall`, 2 `bot_block_403`, 0 timeout, and 0
`taxicab_error`.

The accepted full 10K gate after Human Kinetics and bounded recoveries is historical: `pdf-full10k-after-humankinetics-bbd2225`, 1,910/6,293 `good_pdf` (30.35%). The then-current accepted full gate was `pdf-full10k-after-structured-parser-a61d34b`, 2,193/6,293 `good_pdf` (34.85%), +283 net versus Human Kinetics and +356 versus the denominator baseline. It had 0 timeout and 0 `taxicab_error`; 363 prior non-good rows became `good_pdf`, and 80 prior `good_pdf` rows were stricter-reclassified as `supplement_or_preview_pdf`. Oxjobs commit `dcb7bb14 #461 taxicab-pdf: publish structured parser gate` records the accepted report; oxjobs commit `9569e1f6 #461 taxicab-pdf: publish Wiley residual probe` records the 3/5 no-storage residual Wiley strategy evidence; oxjobs commit `6ba84787 #461 taxicab-pdf: publish Wiley all-row probe` records the 15/19 all-row residual Wiley strategy evidence.

The generic no-storage provider probe is pushed at Taxicab commit
`31663bc taxicab: add provider pdf strategy probe`. IOP residual probe
`iop-corrupt-provider-probe-3-31663bc` recovered 0/3 PDFs: one PerfDrive/captcha
block and two corrupt application/pdf responses with no page objects. Oxjobs
#461 commit `27d5e414 #461 taxicab-pdf: record iop residual probe` publishes
the scrubbed summary/report. J-STAGE corrupt-provider probe
`jstage-corrupt-provider-probe-3b-31663bc` recovered 0/3 residual corrupt PDFs:
two application/pdf responses still had no page objects and one row timed out
empty; browser HTML returned PDF-viewer shells. Oxjobs #461 commit
`416b6fec #461 taxicab-pdf: record jstage corrupt probe` publishes the scrubbed
summary/report. J-STAGE encrypted-provider probe
`jstage-encrypted-provider-probe-3-31663bc` recovered 0/3 residual
encrypted/unreadable PDFs; default body reached PDF bytes but all rows remained
encrypted/unreadable. Oxjobs #461 commit
`a1073dd4 #461 taxicab-pdf: record jstage encrypted probe` publishes the
scrubbed summary/report. J-STAGE missing-provider probe
`jstage-missing-provider-probe-3-31663bc` recovered 0/3 residual missing rows:
two stayed JS redirects and one timed out empty/browser-shell. Oxjobs #461
commit `e9a4458a #461 taxicab-pdf: record jstage missing probe` publishes the
scrubbed summary/report. Next lane: Taylor/TandF missing-PDF residual probing
on `www.tandfonline.com` using `scripts/provider_pdf_probe.py`.

Gated PDF reharvest mode is implemented locally. It POSTs the corpus `PDF URL`
when present, caps workers at 4, waits for write/read consistency, then re-runs
the PDF read path. First 5-row live smoke completed with 0/5 `good_pdf`,
3 Taxicab invalid-PDF POST responses mapped to `corrupt_or_truncated_pdf`, 2
`missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`.

Oxjobs #461 is pushed through `4ee9d6f4 #461 taxicab-pdf: record reharvest
smoke gate`. The Springer seed queue is now
`/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv`.
The first seed run `pdf-springer-missing-reharvest-12` recovered 1/12:
`10.1007/bf03544238` became a 7-page `good_pdf`; the other 11 rows stayed
`missing_pdf_harvest`. The current code change preserves POST status/id/content
type/resolved URL on those missing-after-POST rows so the next rerun is
diagnosable.

The post-context rerun `pdf-springer-missing-reharvest-12-post-context-b9d5918`
again recovered 1/12. All 11 misses show Taxicab POST status 201 with
`post content_type html`, resolving to Springer article/chapter/rwe HTML pages
instead of storing PDF records. A no-storage call to the existing two-step Zyte
landing-page helper for `10.1007/978-3-662-67010-1_39` also returned HTML, not a
PDF. Do not add Springer to the existing landing-page rewrite host list without
new evidence; prepare a Zyte support packet first.

PDF Browserbase evidence mode is implemented and pushed at
`f424129 taxicab: add pdf browserbase evidence mode`.
It annotates non-good PDF rows only; it does not change Taxicab baseline
categories. The local no-credential smoke writes `not_configured` evidence.
Using the ignored Parseland eval env key, the one-row Springer Browserbase
session smoke `pdf-browserbase-springer-1-f424129` returned `html_not_pdf` for
`10.1007/978-1-4419-6247-8_15015` and landed on
`https://link.springer.com/rwe/10.1007/978-1-4419-6247-8_15015`, not PDF bytes.

Elsevier queue:
`/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-25.csv`
contains 25 true `missing_pdf_harvest` rows generated from
`pdf_eval_runs/pdf-full10k-denominator-3f7cd47/rows.ndjson`. The first
unbounded reharvest attempt completed 23/25 rows before manual interrupt:
4 `good_pdf`, 6 `corrupt_or_truncated_pdf`, 13 `missing_pdf_harvest`, and 0
timeout / 0 `taxicab_error` among completed rows. Add and use `--row-timeout`
before resuming that run.

Row-timeout watchdog is implemented and pushed at
`be2f5c7 taxicab: add pdf row timeout watchdog`. It turns pathological
per-row hangs into `timeout` verdicts instead of blocking a sample. The resumed
Elsevier run `pdf-elsevier-missing-reharvest-25-84b2c05` completed all 25 rows:
4 `good_pdf`, 15 `missing_pdf_harvest`, 6 `corrupt_or_truncated_pdf`,
0 `timeout`, and 0 `taxicab_error`. This is a localized +4 recovery inside a
25-row true-missing sample; it is not a full-10K KPI lift until read-only
confirmation and a full gate.

The read-only confirmation
`pdf-elsevier-missing-readonly-after-reharvest-be2f5c7` completed on the same
25-row queue with 4 `good_pdf`, 21 `missing_pdf_harvest`, 0 timeout, and
0 `taxicab_error`. The four recovered Elsevier PDFs persisted as Taxicab
records. The six corrupt/truncated POST outcomes did not persist as corrupt
records; they read back as missing and need separate triage if this cluster is
continued.

The larger Elsevier queue
`/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-100.csv`
contains 100 of the 384 Elsevier `missing_pdf_harvest` rows from the
denominator baseline. Reharvest `pdf-elsevier-missing-reharvest-100-41d0378`
returned 6/100 `good_pdf`, 48 missing, 45 corrupt/truncated POST outcomes,
one timeout, and 0 `taxicab_error`. Raw rows/hardness contain signed
ScienceDirect asset URLs; do not publish them unsanitized.

The corrected read-only run
`pdf-elsevier-missing-readonly-previewfix-9b7d84b` returned 7/100 `good_pdf`,
92 missing, and one `supplement_or_preview_pdf` after the classifier fix for
`first-page-pdf` URLs. This is the current honest Elsevier sample metric.
Oxjobs #461 published this result at commit
`3d8a5fa0 #461 taxicab-pdf: publish elsevier 100 gate`. The next work should
split Elsevier into ScienceDirect, Lancet, Cell, direct-asset, router,
corrupt/truncated POST, and Zyte-support clusters. Do not scale blind reharvest
from the 7/100 readback.
Oxjobs #461 route split is now published at commit
`825c2e2d #461 taxicab-pdf: add elsevier route split`: 34 ScienceDirect route
rows, 23 journal-host/long-tail rows, 11 invalid-PDF POST rows, 8 Lancet rows,
7 durable recoveries, 5 cross-publisher candidates, 4 DOI-router candidates,
4 direct-asset rows, 3 Cell Press rows, and 1 preview row. Next technical lane:
no-storage ScienceDirect route probes plus scrubbed Zyte examples.
Taxicab commit `741e9a7 taxicab: add sciencedirect pdf probe` adds the
no-storage probe runner. Run `sciencedirect-route-probe-3-741e9a7` tested 3 DOI
candidates and 12 route variants; result was 0 `good_pdf`, with best category
`html_instead_of_pdf` for 3/3. Oxjobs commit
`666d0ed6 #461 taxicab-pdf: record sciencedirect probe` publishes the scrubbed
summary/report and Zyte packet. Next: send the packet or test Zyte-advised
PDF-byte fetch mode; do not add production ScienceDirect PDF route code yet.
Lancet run `lancet-route-probe-3-741e9a7` tested 3 candidate PDF URLs and
recovered 0 `good_pdf`; two rows were Zyte 520 ban-free failures and one was a
404 HTML page. Oxjobs commit `2105c8f1 #461 taxicab-pdf: record lancet probe`
publishes the scrubbed artifacts and packet `lancet-pdf-ban-741e9a7.md`.
Next shared lane: send/test Zyte guidance for ScienceDirect and Lancet PDF-byte
fetching before production route code.
Cell Press run `cell-route-probe-3-741e9a7` tested 3 candidate PDF URLs and
recovered 0 `good_pdf`; all three returned login/JavaScript HTML. Oxjobs commit
`a160ec1a #461 taxicab-pdf: record cell probe` publishes the scrubbed artifacts
and packet `cell-pdf-login-js-741e9a7.md`. Add Cell to the same Zyte/advised
PDF-byte lane before production route code.
Cell Browserbase evidence run `pdf-browserbase-cell-1-3de630f` tested one Cell
candidate and also returned `html_not_pdf` with `browserbase_available=false`.
Oxjobs commit `d0344d1d #461 taxicab-pdf: record cell browserbase evidence`
publishes only `evidence/browserbase/cell-pdf-html-not-pdf-3de630f.json`.
Do not publish raw Browserbase rows, HTML, screenshots, or final URLs from this
run because the final URL included a Cloudflare challenge token.

Wiley run `pdf-wiley-missing-reharvest-25-4267740` tested 25
`missing_pdf_harvest` rows from `onlinelibrary.wiley.com` and recovered
0 `good_pdf`: all 25 stayed `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. POST accepted HTML landing-page captures at Wiley DOI
routes, not PDF bytes. Oxjobs commit `3d7356bc #461 taxicab-pdf: add wiley
provider packet` publishes a scrubbed summary/report, the Wiley packet, and the
combined request `evidence/zyte-support/pdf-byte-fetch-provider-request-4267740.md`.

De Gruyter run `pdf-degruyter-missing-reharvest-25-95308b7` tested 25
`missing_pdf_harvest` rows from `www.degruyterbrill.com` and recovered
0 `good_pdf`: all 25 stayed `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. POST accepted HTML `/html` pages, and direct no-storage
`/pdf` probes returned JS/robot-verification HTML. Oxjobs commit
`de7d0f2d #461 taxicab-pdf: add degruyter provider packet` publishes the
scrubbed De Gruyter summary/report and packet.

Lippincott run `pdf-lippincott-missing-reharvest-25-0405edf` tested 25
`missing_pdf_harvest` rows from mostly `journals.lww.com` and recovered
0 `good_pdf`: all 25 stayed `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. POST accepted article/abstract HTML pages, and direct
no-storage `downloadpdf.aspx` probes returned secured-browser / enable-scripts
HTML. Oxjobs commit `b88a5a79 #461 taxicab-pdf: add lippincott provider
packet` publishes the scrubbed Lippincott summary/report and packet.

Oxford run `pdf-oxford-missing-reharvest-25-b259f2e` tested 25
`missing_pdf_harvest` rows from `academic.oup.com` and recovered 0 `good_pdf`:
all 25 stayed `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`.
POST accepted article/abstract HTML pages, and direct no-storage `article-pdf`
probes returned Zyte 520 empty responses. Oxjobs commit
`e1fe9deb #461 taxicab-pdf: add oxford provider packet` publishes the scrubbed
Oxford summary/report and packet.

CUP/Cambridge run `pdf-cup-missing-reharvest-25-39517e5` tested 25
`missing_pdf_harvest` rows from `www.cambridge.org` and recovered 0
`good_pdf`: all 25 stayed `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. POST accepted Cambridge Core HTML pages, and direct
no-storage explicit PDF probes returned status 200 `text/html` Cambridge Core
article/book pages, not PDF bytes. Oxjobs commit
`df7784c9 #461 taxicab-pdf: add cup provider packet` publishes the scrubbed
CUP/Cambridge summary/report and packet.
Follow-up strategy probe `cup-zyte-strategy-probe-1-26d3d5c` tested default
HTTP `httpResponseBody`, a PDF `Accept` header, residential variants, and
browser network capture over one explicit Cambridge PDF URL. Result: 0 PDF
bodies; the non-rejected strategies returned Cambridge Core HTML. Oxjobs
commit `77e793a8 #461 taxicab-pdf: record cup strategy probe` publishes the
scrubbed public summary/report.

SSRN run `pdf-ssrn-missing-reharvest-25-64b787f` tested 25
`missing_pdf_harvest` rows from `papers.ssrn.com` and recovered 0 `good_pdf`:
all 25 stayed `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`.
POST mostly accepted SSRN HTML delivery/landing pages. Direct no-storage
delivery probes returned SSRN HTML or removed-paper HTML, not PDF bytes.
Oxjobs commit `ade1b60f #461 taxicab-pdf: add ssrn provider packet` publishes
the scrubbed SSRN summary/report and packet.

IOP run `pdf-iop-missing-reharvest-25-2e2c123` tested 25
`missing_pdf_harvest` rows from `iopscience.iop.org` and recovered 16
`good_pdf`, with 6 missing, 2 corrupt/truncated, 1 timeout, and 0
`taxicab_error`. Read-only confirmation
`pdf-iop-missing-readonly-after-reharvest-2e2c123` preserved the same 16
durable `good_pdf` records, with 7 missing, 2 corrupt/truncated, 0 timeout,
and 0 `taxicab_error`. Oxjobs commit
`7d376fa0 #461 taxicab-pdf: publish iop positive sample` publishes the scrubbed
IOP summary/report. The follow-up accepted full gate
`pdf-full10k-after-iop-d6fb6bb` now quantifies all-corpus impact at +24
`good_pdf` on the PDF denominator.

Remaining IOP queue `pdf-iop-remaining45-reharvest-e5bcd30` tested 45
remaining `missing_pdf_harvest` rows from `iopscience.iop.org` and recovered
21 `good_pdf`, with 18 missing, 6 corrupt/truncated, 0 timeout, and
0 `taxicab_error`. Read-only confirmation
`pdf-iop-remaining45-readonly-e5bcd30` preserved the same 21 durable
`good_pdf` records. The follow-up accepted full gate
`pdf-full10k-after-iop-remaining-e5bcd30` quantifies cumulative IOP impact at
+45 `good_pdf` versus the denominator baseline.

RSC run `pdf-rsc-missing48-reharvest-008fe7f` tested 48
`missing_pdf_harvest` rows from `pubs.rsc.org` and recovered 0 `good_pdf`, with
47 still missing, one timeout, and 0 `taxicab_error`. POST accepted
`/articlelanding/.../unauth` HTML pages rather than `articlepdf` bytes. Oxjobs
commit `68025078 #461 taxicab-pdf: add rsc provider packet` publishes the RSC
queue, scrubbed summary/report, provider packet, and combined request update.

AIP run `pdf-aip-missing45-reharvest-8ce7e7e` tested 45
`missing_pdf_harvest` rows from `10.1063/...` AIP Publishing and recovered
0 `good_pdf`, with 44 still missing, one corrupt/truncated response, 0 timeout,
and 0 `taxicab_error`. POST returned status 201 HTML/no durable PDF records for
the missing rows. Oxjobs commit `85584ddd #461 taxicab-pdf: add aip provider
packet` publishes the AIP queue, scrubbed summary/report, provider packet, and
combined request update.

Taylor mixed queue `pdf-taylor-missing25-reharvest-e7d1361` recovered and
confirmed 2 durable direct TandF journal PDFs. Taylor TandF-only expansion
`pdf-taylor-tandfonline29-reharvest-e7d1361` recovered and confirmed 3 more.
The accepted full gate `pdf-full10k-after-taylor-e7d1361` is now 1,887/6,293
`good_pdf` (29.99%), +5 vs the prior gate, with 0 regressions, 0 timeout, and
0 `taxicab_error`. Taylor API chapter-download URLs still store HTML chapter
pages. Oxjobs commit `574539d2 #461 taxicab-pdf: publish taylor full gate`
publishes the Taylor queues, scrubbed summaries/reports, provider packet, graph
update, and latest-summary/hardness artifacts.

ACS run `pdf-acs-missing25-reharvest-2b7996a` tested 25 `missing_pdf_harvest`
rows from `pubs.acs.org` and recovered 0 `good_pdf`: 19 rows stayed missing,
six were `corrupt_or_truncated_pdf`, and there were 0 timeout / 0
`taxicab_error` rows. Oxjobs commit
`482cc4fd #461 taxicab-pdf: add acs provider packet` publishes the ACS queue,
scrubbed summary/report, provider packet, and combined request update. Treat ACS
as a Zyte/provider-advised PDF-byte and corrupt-PDF lane before production route
code.

SPIE run `pdf-spie-missing25-reharvest-62c6a33` tested 25
`missing_pdf_harvest` rows from `www.spiedigitallibrary.org` and recovered
0 `good_pdf`: all rows stayed missing, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `c5792694 #461 taxicab-pdf: add spie provider packet` publishes
the SPIE queue, scrubbed summary/report, provider packet, and combined request
update. Treat SPIE as a Zyte/provider-advised PDF-byte lane before production
route code.

Thieme run `pdf-thieme-missing25-reharvest-d0ea198` tested 25
`missing_pdf_harvest` rows from `www.thieme-connect.de` /
`science-of-synthesis.thieme.com` and recovered 0 `good_pdf`: all rows stayed
missing, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`8cb377c7 #461 taxicab-pdf: add thieme provider packet` publishes the Thieme
queue, scrubbed summary/report, provider packet, and combined request update.
Treat Thieme as a Zyte/provider-advised PDF-byte lane before production route
code.

Sage run `pdf-sage-missing25-reharvest-2705643` tested 25
`missing_pdf_harvest` rows from `journals.sagepub.com` and recovered
0 `good_pdf`: 11 rows stayed missing, 14 rows were
`corrupt_or_truncated_pdf`, and there were 0 timeout / 0 `taxicab_error` rows.
PDF routes either resolved to abstract HTML/no durable PDF records or returned
invalid PDF-like responses with no page objects. Oxjobs commit
`ca3b11fe #461 taxicab-pdf: add sage provider packet` publishes the Sage queue,
scrubbed summary/report, provider packet, and combined request update. Treat
Sage as a Zyte/provider-advised PDF-byte and invalid-PDF lane before production
route code.

Brill run `pdf-brill-missing30-reharvest-7520bc1` tested 30
`missing_pdf_harvest` rows from `brill.com` and recovered 0 `good_pdf`: all 30
rows stayed missing, with 0 timeout and 0 `taxicab_error`. The sampled
`downloadpdf` routes returned status 200 and resolved to expected Brill PDF
URLs, but no durable PDF records were readable afterward. Oxjobs commit
`172b7580 #461 taxicab-pdf: add brill provider packet` publishes the Brill
queue, scrubbed summary/report, provider packet, and combined request update.
Treat Brill as a Zyte/provider-advised PDF-byte lane before production route
code.

AMA/JAMA run `pdf-ama-jama-missing25-reharvest-005b032` tested 25
`missing_pdf_harvest` rows from `jamanetwork.com` and recovered 0 `good_pdf`:
18 rows stayed missing, 7 rows were `corrupt_or_truncated_pdf`, and there were
0 timeout / 0 `taxicab_error` rows. PDF routes either resolved to JAMA article
HTML/no durable PDF records or returned invalid PDF-like responses. Oxjobs
commit `d82e9ba6 #461 taxicab-pdf: add ama jama provider packet` publishes the
AMA/JAMA queue, scrubbed summary/report, provider packet, and combined request
update. Treat AMA/JAMA as a Zyte/provider-advised PDF-byte and invalid-PDF lane
before production route code.

APS run `pdf-aps-missing23-reharvest-65feabe` tested 23
`missing_pdf_harvest` rows from `link.aps.org` / `journals.aps.org` and
recovered 0 `good_pdf`: all 23 rows stayed missing, with 0 timeout and
0 `taxicab_error`. PDF routes resolved to APS article/abstract HTML/no durable
PDF records; one row resolved to a `journals.aps.org/.../pdf/...` URL but still
had no readable durable PDF record. Oxjobs commit
`147a9e65 #461 taxicab-pdf: add aps provider packet` publishes the APS queue,
scrubbed summary/report, provider packet, and combined request update. Treat
APS as a Zyte/provider-advised PDF-byte lane before production route code.

ACM run `pdf-acm-missing22-reharvest-5f81111` tested 22
`missing_pdf_harvest` rows from `dl.acm.org` and recovered 0 `good_pdf`:
16 rows stayed missing, five were `corrupt_or_truncated_pdf`, one timed out,
and there were 0 `taxicab_error` rows. Oxjobs commit
`32d6a637 #461 taxicab-pdf: add acm provider packet` publishes the ACM queue,
scrubbed summary/report, provider packet, and combined request update. Treat
ACM as a Zyte/provider-advised PDF-byte and invalid-PDF lane before production
route code.

BMJ run `pdf-bmj-missing32-reharvest-4c213b6` tested 32
`missing_pdf_harvest` rows from BMJ journal hosts and recovered 0 `good_pdf`:
31 rows stayed missing, one was `corrupt_or_truncated_pdf`, 0 timeout, and
0 `taxicab_error`. Oxjobs commit
`3319e184 #461 taxicab-pdf: add bmj provider packet` publishes the BMJ queue,
scrubbed summary/report, provider packet, and combined request update. Treat
BMJ as a Zyte/provider-advised PDF-byte lane before production route code.

Karger run `pdf-karger-missing28-reharvest-9a8466e` tested 28
`missing_pdf_harvest` rows and recovered 3 `good_pdf`. Read-only confirmation
`pdf-karger-missing28-readonly-9a8466e` preserved the same three durable PDFs,
with 25 rows still missing, 0 timeout, and 0 `taxicab_error`. Oxjobs commit
`ecae684b #461 taxicab-pdf: add karger recovery packet` publishes the Karger
queue, scrubbed summaries/reports, provider packet, and combined request
update. Full gate `pdf-full10k-after-karger-ca8b132` accepted +3 good rows;
oxjobs commit `5ccb3df5 #461 taxicab-pdf: publish karger full gate` publishes
the accepted report.

Optica/opg run `pdf-optica-missing21-reharvest-25496ec` tested 21
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: all rows stayed missing
after status-201 HTML captures at `opg.optica.org/viewmedia.cfm` routes, with
0 timeout and 0 `taxicab_error`. Oxjobs commit
`826bd689 #461 taxicab-pdf: add optica provider packet` publishes the Optica
queue, scrubbed report, provider packet, and combined request update.

JSTOR run `pdf-jstor-missing60-reharvest-dc6cafc` tested 60
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: all rows stayed missing
after status-201 HTML captures at `www.jstor.org/stable/pdf` routes, with
0 timeout and 0 `taxicab_error`. Oxjobs commit
`19ca1aff #461 taxicab-pdf: add jstor provider packet` publishes the JSTOR
queue, scrubbed report, provider packet, and combined request update.

Inlibra run `pdf-inlibra-missing32-reharvest-54d17e9` tested 32
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: all rows stayed missing
after status-201 HTML captures at `www.inlibra.com/document/download/pdf/uuid`
routes, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`0df48262 #461 taxicab-pdf: add inlibra provider packet` publishes the Inlibra
queue, scrubbed report, provider packet, and combined request update.

Scientific.net run `pdf-scientificnet-missing20-reharvest-4e6130f` tested 20
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: all rows stayed missing
after status-201 HTML captures at `www.scientific.net` article pages, with
0 timeout and 0 `taxicab_error`. Oxjobs commit
`3b84fb4b #461 taxicab-pdf: add scientificnet provider packet` publishes the
Scientific.net queue, scrubbed report, provider packet, and combined request
update.

Persee run `pdf-persee-missing18-reharvest-af4baf7` tested 18
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: every row classified as
`corrupt_or_truncated_pdf` after invalid PDF content, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`1a7d1ddb #461 taxicab-pdf: add persee provider packet` publishes the Persee
queue, scrubbed report, and provider packet.

Nature run `pdf-nature-missing17-reharvest-e7616c9` tested 17
`missing_pdf_harvest` rows and recovered 2 `good_pdf`. Read-only confirmation
`pdf-nature-missing17-readonly-e7616c9` preserved the same two durable PDFs,
with 15 `missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`. Oxjobs commit
`33c8c71c #461 taxicab-pdf: add nature recovery packet` publishes the Nature
queue, scrubbed reports, and residual provider packet.

J-STAGE run `pdf-jstage-missing16-reharvest-43777d8` tested 16
`missing_pdf_harvest` rows and recovered 2 `good_pdf`. Read-only confirmation
`pdf-jstage-missing16-readonly-43777d8` preserved the same two durable PDFs,
with 8 `corrupt_or_truncated_pdf`, 1 `encrypted_or_unreadable_pdf`, 5
`missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`. Oxjobs commit
`59789f72 #461 taxicab-pdf: add jstage recovery packet` publishes the J-STAGE
queue, scrubbed reports, and residual provider packet.

University of Chicago Journals run `pdf-uchicago-missing16-reharvest-6b41e44`
tested 16 `missing_pdf_harvest` rows and recovered 0 `good_pdf`: all 16 stayed
missing, with 0 timeout and 0 `taxicab_error`. POST accepted HTML/no durable
PDF records for `journals.uchicago.edu/doi/pdf` and `/doi/epdf` routes,
commonly resolving to `/doi/abs/...` article pages. Oxjobs commit
`95bde36b #461 taxicab-pdf: add uchicago provider packet` publishes the
UChicago queue, scrubbed report, and provider packet.

ASME run `pdf-asme-missing15-reharvest-c1c2b86` tested 15
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: eight rows returned
invalid PDF-like content and seven stayed missing after HTML/no-record captures,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`10d80d80 #461 taxicab-pdf: add asme provider packet` publishes the ASME queue,
scrubbed report, and provider packet.

Cairn run `pdf-cairn-missing20-reharvest-8742847` tested 20
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: nineteen rows returned
invalid PDF-like content and one stayed missing after HTML/no-record capture,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`97b61e38 #461 taxicab-pdf: add cairn provider packet` publishes the Cairn
queue, scrubbed report, and provider packet.

Physiology run `pdf-physiology-missing11-reharvest-6db1728` tested 11
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: five rows returned
invalid PDF-like content and six stayed missing after HTML/no-record capture,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`33d5cb5b #461 taxicab-pdf: add physiology provider packet` publishes the
Physiology queue, scrubbed report, and provider packet.

ASCE run `pdf-asce-missing10-reharvest-e708434` tested 10
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: five rows returned
invalid PDF-like content and five stayed missing after HTML/no-record capture,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`b57dba2f #461 taxicab-pdf: add asce provider packet` publishes the ASCE
queue, scrubbed report, and provider packet.

PDCNet run `pdf-pdcnet-missing9-reharvest-9cd3b93` tested 9
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: every row stayed missing
after HTML purchase/form captures, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `a1663d3f #461 taxicab-pdf: add pdcnet provider packet`
publishes the PDCNet queue, scrubbed report, and provider packet.

EurekaSelect run `pdf-eurekaselect-missing8-reharvest-d224066` tested 8
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: six rows returned
invalid PDF-like content and two stayed missing after HTML/no-record captures,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`357c4ee1 #461 taxicab-pdf: add eurekaselect provider packet` publishes the
EurekaSelect queue, scrubbed report, and provider packet.

ActaHort run `pdf-actahort-missing8-reharvest-8ce7ac3` tested 8
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: every row stayed missing
after status-201 HTML/no durable PDF captures from
`www.actahort.org/members/showpdf` routes, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`be526662 #461 taxicab-pdf: add actahort provider packet` publishes the
ActaHort queue, scrubbed report, and provider packet.

V&R eLibrary run `pdf-vr-elibrary-missing7-reharvest-fdfa16c` tested 7
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: six rows stayed missing
after reader routes resolved to abstract HTML/no durable PDF records, and one
explicit PDF route classified as `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`c3d3b00b #461 taxicab-pdf: add vr-elibrary provider packet` publishes the
V&R eLibrary queue, scrubbed report, and provider packet.

IWA Publishing run `pdf-iwaponline-missing7-reharvest-bfa43c4` tested 7
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: explicit article-PDF
routes resolved to article-abstract HTML with `redirectedFrom=PDF`, leaving no
durable PDF records, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`98a037c1 #461 taxicab-pdf: add iwaponline provider packet` publishes the IWA
queue, scrubbed report, and provider packet.

AMS journals run `pdf-ametsoc-missing7-reharvest-29cf658` tested 7
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: explicit
`downloadpdf/view` routes returned status 200 but created no durable readable
PDF records, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`8fe1d510 #461 taxicab-pdf: add ametsoc provider packet` publishes the AMS
queue, scrubbed report, and provider packet.

JPET/ASPET run `pdf-jpet-missing7-reharvest-0dd85b6` tested 7
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: six rows returned
invalid PDF-like content and one row stayed missing after an HTML/no-record
capture, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`ae72a1ff #461 taxicab-pdf: add jpet provider packet` publishes the JPET/ASPET
queue, scrubbed report, and provider packet.

OnePetro run `pdf-onepetro-missing7-reharvest-92f581e` tested 7
`missing_pdf_harvest` rows and recovered 0 `good_pdf`: all rows stayed missing
after HTML abstract/proceedings or no-record captures, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`029f9ac9 #461 taxicab-pdf: add onepetro provider packet` publishes the
OnePetro queue, scrubbed report, and provider packet.
Mary Ann Liebert run `pdf-liebertpub-missing7-reharvest-b5e1678` tested 7
`missing_pdf_harvest` rows from `www.liebertpub.com` and recovered
0 `good_pdf`: five rows stayed missing after Sage-hosted HTML/no-record
captures, and two rows returned invalid PDF-like content, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`c9eafb75 #461 taxicab-pdf: add liebertpub provider packet` publishes the
Liebert queue, scrubbed report, and provider packet.
AACR Figshare run `pdf-aacr-figshare-missing6-reharvest-8f674aa` tested 6
`missing_pdf_harvest` rows from `aacr.figshare.com` and recovered
0 `good_pdf`: all rows stayed missing after status-201 HTML/no durable PDF
captures, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`dd7ab56d #461 taxicab-pdf: add aacr figshare provider packet` publishes the
AACR Figshare queue, scrubbed report, and provider packet.
AMPP run `pdf-ampp-missing6-reharvest-851bd3f` tested 6
`missing_pdf_harvest` rows from `content.ampp.org` and recovered
0 `good_pdf`: all rows returned invalid PDF-like content and classified as
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`ef843caa #461 taxicab-pdf: add ampp provider packet` publishes the AMPP queue,
scrubbed report, and provider packet.
Healio run `pdf-healio-missing6-reharvest-51c7ad1` tested 6
`missing_pdf_harvest` rows from `journals.healio.com` and recovered
0 `good_pdf`: all rows returned invalid PDF-like content and classified as
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`64517b97 #461 taxicab-pdf: add healio provider packet` publishes the Healio
queue, scrubbed report, and provider packet.
Sage Knowledge run `pdf-sage-knowledge-missing10-reharvest-bef0376` tested 10
`missing_pdf_harvest` rows from `sk.sagepub.com` and recovered
0 `good_pdf`: all rows returned invalid PDF-like content and classified as
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`79af39d8 #461 taxicab-pdf: add sage knowledge provider packet` publishes the
Sage Knowledge queue, scrubbed report, and provider packet.
IGI Global run `pdf-igi-global-missing6-reharvest-14746e2` tested 6
`missing_pdf_harvest` rows from `www.igi-global.com` and recovered
1 `good_pdf`; read-only confirmation `pdf-igi-global-missing6-readonly-14746e2`
preserved the same durable PDF and left five rows missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`471f9ee3 #461 taxicab-pdf: add igi global recovery packet` publishes the IGI
queue, scrubbed reports, and residual provider packet.
UC Press run `pdf-ucpress-missing6-reharvest-dd1a528` tested 6
`missing_pdf_harvest` rows from `online.ucpress.edu` and recovered
0 `good_pdf`; all six explicit article-PDF routes returned invalid PDF-like
content and classified as `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`e435bc5e #461 taxicab-pdf: add ucpress provider packet` publishes the UC Press
queue, scrubbed report, and provider packet.
RUPress run `pdf-rupress-missing6-reharvest-76fb88d` tested 6
`missing_pdf_harvest` rows from `rupress.org` and recovered
1 `good_pdf`; read-only confirmation `pdf-rupress-missing6-readonly-76fb88d`
preserved the same durable PDF and left four rows missing plus one
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`fa847b5a #461 taxicab-pdf: add rupress recovery packet` publishes the RUPress
queue, scrubbed reports, and residual provider packet.
Emerald run `pdf-emerald-missing6-reharvest-e3fdbea` tested 6
`missing_pdf_harvest` rows from `www.emerald.com` and recovered
0 `good_pdf`; all six explicit article-PDF routes returned invalid PDF-like
content and classified as `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`f191f0eb #461 taxicab-pdf: add emerald provider packet` publishes the Emerald
queue, scrubbed report, and provider packet.
JACC run `pdf-jacc-missing6-reharvest-9e16fb8` tested 6
`missing_pdf_harvest` rows from `www.jacc.org` and recovered
0 `good_pdf`; all six explicit `doi/epdf` routes stored HTML with no durable
PDF records and classified as `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`eea013bf #461 taxicab-pdf: add jacc provider packet` publishes the JACC queue,
scrubbed report, and provider packet.
AJO run `pdf-ajo-missing6-reharvest-a30f12a` tested 6 `missing_pdf_harvest`
rows from `www.ajo.com` and recovered 0 `good_pdf`; five explicit article-PDF
routes returned invalid PDF-like content, one row stayed missing, with
0 timeout and 0 `taxicab_error`. Oxjobs commit
`a72d7c09 #461 taxicab-pdf: add ajo provider packet` publishes the AJO queue,
scrubbed report, and provider packet.
BioOne run `pdf-bioone-missing5-reharvest-1d9e18f` tested 5
`missing_pdf_harvest` rows from `bioone.org` and recovered 0 `good_pdf`; all
five explicit PDF routes stayed missing, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `b60d7147 #461 taxicab-pdf: add bioone provider packet` publishes
the BioOne queue, scrubbed report, and provider packet.
Canadian Science Publishing run `pdf-cdnsciencepub-missing5-reharvest-2a121b2`
tested 5 `missing_pdf_harvest` rows from `cdnsciencepub.com` and recovered
0 `good_pdf`; three explicit PDF routes returned invalid PDF content and two
stayed missing, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`634173b9 #461 taxicab-pdf: add canadian science provider packet` publishes the
Canadian Science queue, scrubbed report, and provider packet.
Edward Elgar run `pdf-elgaronline-missing5-reharvest-8244033` tested 5
`missing_pdf_harvest` rows from `www.elgaronline.com` and recovered
1 `good_pdf`; read-only confirmation
`pdf-elgaronline-missing5-readonly-8244033` preserved the same durable PDF and
left four rows missing, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`9771940c #461 taxicab-pdf: add edward elgar recovery packet` publishes the
Edward Elgar queue, scrubbed reports, and residual provider packet.
American Concrete Institute run `pdf-concrete-missing5-reharvest-d38b219`
tested 5 `missing_pdf_harvest` rows from `www.concrete.org` and recovered
0 `good_pdf`; all rows stayed missing after portal detail or secured sign-in
HTML captures, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`9fbae749 #461 taxicab-pdf: add concrete provider packet` publishes the ACI
queue, scrubbed report, and provider packet.
American Journal of Surgery run
`pdf-americanjournalofsurgery-missing5-reharvest-93479bd` tested 5
`missing_pdf_harvest` rows from `www.americanjournalofsurgery.com` and recovered
0 `good_pdf`; three rows returned invalid PDF content and two stayed missing
after abstract HTML captures, with 0 timeout and 0 `taxicab_error`. Oxjobs
commit `1b4912ec #461 taxicab-pdf: add american journal of surgery packet`
publishes the AJS queue, scrubbed report, and provider packet.
AJOG run `pdf-ajog-missing5-reharvest-831503a` tested 5 `missing_pdf_harvest`
rows from `www.ajog.org` and recovered 1 `good_pdf`; read-only confirmation
`pdf-ajog-missing5-readonly-831503a` preserved the same durable PDF and left
four rows missing, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`2e492500 #461 taxicab-pdf: add ajog recovery packet` publishes the AJOG queue,
scrubbed reports, and residual provider packet.
Scholarly Publishing Collective run
`pdf-scholarlypublishingcollective-missing5-reharvest-a9fdacb` tested 5
`missing_pdf_harvest` rows from `scholarlypublishingcollective.org` and
recovered 0 `good_pdf`; four article-PDF routes returned invalid PDF content
and one row resolved to article abstract HTML/no durable PDF record, with
0 timeout and 0 `taxicab_error`. Oxjobs commit
`362d2b2f #461 taxicab-pdf: add scholarly publishing collective packet`
publishes the Scholarly queue, scrubbed report, and provider packet.
Royal Society Publishing run
`pdf-royalsocietypublishing-missing5-reharvest-1d0fac0` tested 5
`missing_pdf_harvest` rows from `royalsocietypublishing.org` and recovered
0 `good_pdf`; three rows redirected to Silverchair watermark PDF URLs and two
resolved to article abstract HTML/no durable PDF record, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`cfeb6d34 #461 taxicab-pdf: add royal society provider packet` publishes the
Royal Society queue, scrubbed report, and provider packet.
KoreaScience run `pdf-koreascience-missing5-reharvest-35d3541` tested 5
`missing_pdf_harvest` rows from `koreascience.or.kr` and recovered
0 `good_pdf`; all five explicit `article/*.pdf` routes timed out under the row
watchdog, with 0 `taxicab_error`. Oxjobs commit
`53c6d7fe #461 taxicab-pdf: add koreascience timeout packet` publishes the
KoreaScience queue, scrubbed report, and provider packet.
Journal of Pharmaceutical Sciences run `pdf-jpharmsci-missing5-reharvest-3b7bf15`
tested 5 `missing_pdf_harvest` rows from `jpharmsci.org` and recovered
0 `good_pdf`; all five `/article/.../pdf` routes resolved to
`/article/.../abstract` HTML, with 0 timeout and 0 `taxicab_error`. Oxjobs
commit `c1f26ec8 #461 taxicab-pdf: add jpharmsci provider packet` publishes the
J Pharm Sci queue, scrubbed report, and provider packet.
CHEST run `pdf-chestnet-missing5-reharvest-4c6cd17` tested 5
`missing_pdf_harvest` rows from `journal.chestnet.org` and recovered
1 `good_pdf`; read-only confirmation `pdf-chestnet-missing5-readonly-4c6cd17`
preserved the same durable PDF and left four rows missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`ee27cd5e #461 taxicab-pdf: add chestnet recovery packet` publishes the CHEST
queue, scrubbed reports, and provider packet.
Green Journal run `pdf-thegreenjournal-missing4-reharvest-a211471` tested 4
`missing_pdf_harvest` rows from `thegreenjournal.com` and recovered
0 `good_pdf`; all four stayed `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`0e0bb05f #461 taxicab-pdf: add green journal provider packet` publishes the
Green Journal queue, scrubbed report, and provider packet.
SciELO run `pdf-scielo-missing4-reharvest-7d2c782` tested 4
`missing_pdf_harvest` rows from `scielo.br` and recovered 2 `good_pdf`;
read-only confirmation `pdf-scielo-missing4-readonly-7d2c782` preserved the
same two durable PDFs and left two rows missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`41a903e6 #461 taxicab-pdf: add scielo recovery packet` publishes the SciELO
queue, scrubbed reports, and provider packet.
AIP `pubs.aip.org` run `pdf-pubs-aip-missing25-reharvest-751ad63` tested 25
`missing_pdf_harvest` rows and recovered 0 `good_pdf`; all rows stayed missing
after status-201 HTML/no-record captures, split between 20 article-abstract
fallbacks and 5 signed Silverchair PDF redirects, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`b7940463 #461 taxicab-pdf: add pubs aip provider packet` publishes the AIP
platform queue, scrubbed report, and provider packet.
DOI-router run `pdf-doi-org-missing19-reharvest-659e13e` tested 19
`missing_pdf_harvest` rows and recovered 0 `good_pdf`; 17 rows stayed missing,
2 timed out, and 0 hit `taxicab_error`. The sample mixed publisher fulltext,
PDF, and abstract redirects plus at least one likely non-PDF supplemental
candidate, so this is candidate-filtering plus provider-routing debt, not a
broad route-code change. Oxjobs commit
`4c711418 #461 taxicab-pdf: add doi router provider packet` publishes the
DOI-router queue, scrubbed report, and provider packet.
ScienceDirect direct asset run
`pdf-sciencedirectassets-missing6-reharvest-16bcb5a` tested 6
`missing_pdf_harvest` rows and recovered 0 `good_pdf`; all rows stayed missing,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`58ab0e73 #461 taxicab-pdf: add sciencedirect assets packet` publishes the
ScienceDirect asset queue, scrubbed report, and provider packet.
Springer `link.springer.com` run
`pdf-springer-link-missing25-reharvest-d401917` tested 25
`missing_pdf_harvest` rows and recovered 0 `good_pdf`; all rows stayed missing
after status-201 HTML/no-record captures, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `469a996b #461 taxicab-pdf: add springer link provider packet`
publishes the Springer queue, scrubbed report, and provider packet.
De Gruyter Brill residual run
`pdf-degruyterbrill-missing25-reharvest-f2c5e99` tested 25 current full-gate
`missing_pdf_harvest` rows from `www.degruyterbrill.com` and recovered
0 `good_pdf`; all rows stayed missing after status-201 HTML/no-record
captures, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`ddb8a16f #461 taxicab-pdf: add degruyterbrill residual packet` publishes the
residual queue, scrubbed report, and provider packet.
AIAA tail run `pdf-aiaa-missing4-reharvest-2faaaa2` tested 4 current full-gate
`missing_pdf_harvest` rows from `arc.aiaa.org` and recovered 0 `good_pdf`;
two rows stayed missing after status-201 HTML/no-record captures and two
returned `corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `83c0b0fe #461 taxicab-pdf: add aiaa tail packet` publishes the
queue, scrubbed report, and provider packet.
Neurology tail run `pdf-neurology-missing4-reharvest-42dc6f4` tested 4 current
full-gate `missing_pdf_harvest` rows from `www.neurology.org` and recovered
0 `good_pdf`; three rows stayed missing after status-201 HTML/no-record
captures and one returned `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`d9ede76b #461 taxicab-pdf: add neurology tail packet` publishes the queue,
scrubbed report, and provider packet.
Begell House tail run `pdf-begellhouse-missing4-reharvest-db7d5fc` tested
4 current full-gate `missing_pdf_harvest` rows from `www.dl.begellhouse.com`
and recovered 0 `good_pdf`; all four rows stayed missing after status-201
HTML/no-record captures, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`36ba508f #461 taxicab-pdf: add begellhouse tail packet` publishes the queue,
scrubbed report, and provider packet.
MIT Press Direct tail run `pdf-direct-mit-missing4-reharvest-8643285` tested
4 current full-gate `missing_pdf_harvest` rows from `direct.mit.edu` and
recovered 0 `good_pdf`; all four rows returned invalid PDF content and
classified as `corrupt_or_truncated_pdf`, with 0 timeout and 0
`taxicab_error`. Oxjobs commit
`9fdca746 #461 taxicab-pdf: add direct mit tail packet` publishes the queue,
scrubbed report, and provider packet.
RSNA tail run `pdf-rsna-missing4-reharvest-987d362` tested 4 current
full-gate `missing_pdf_harvest` rows from `pubs.rsna.org` and recovered
0 `good_pdf`; all four rows returned invalid PDF content and classified as
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`67a5b554 #461 taxicab-pdf: add rsna tail packet` publishes the queue,
scrubbed report, and provider packet.
Gold Journal tail run `pdf-goldjournal-missing4-reharvest-91c0c88` tested 4
current full-gate `missing_pdf_harvest` rows from `www.goldjournal.net` and
recovered 0 `good_pdf`; two rows stayed missing after status-201 HTML abstract
captures and two rows returned invalid PDF content, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`8d1c57b4 #461 taxicab-pdf: add gold journal tail packet` publishes the queue,
scrubbed report, and provider packet.
ATS Journals tail run `pdf-atsjournals-missing4-reharvest-a618e5a` tested 4
current full-gate `missing_pdf_harvest` rows from `www.atsjournals.org` and
recovered 0 `good_pdf`; all four rows stayed missing after status-201 HTML
captures resolving to `academic.oup.com/atsjournals`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`7e4dcc79 #461 taxicab-pdf: add ats journals tail packet` publishes the queue,
scrubbed report, and provider packet.
Transcript Verlag corrected run
`pdf-transcript-verlag-missing4-readonly-previewfix-43ab357` tested the 4
stored PDFs from `www.transcript-verlag.de` and accepted 0 `good_pdf`; all four
rows are `supplement_or_preview_pdf` because they match `chunk_prev/prev_*.pdf`,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`433d621e #461 taxicab-pdf: add transcript preview correction` publishes the
queue, corrected report, and preview-candidate note.
PNAS bounded reharvest `pdf-pnas-missing4-reharvest-3d943cf` tested 4 rows
from `www.pnas.org` and accepted 0 `good_pdf`; all four rows classified as
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`8ff5fd14 #461 taxicab-pdf: add pnas tail packet` publishes the queue,
scrubbed report, and provider packet.
Peter Lang bounded reharvest `pdf-peterlang-missing4-reharvest-eb523da`
tested 4 rows from `www.peterlang.com` and accepted 0 `good_pdf`; all four
rows stayed `missing_pdf_harvest` after status-201 HTML captures resolving to
`www.peterlang.com/document/...`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `a12417e1 #461 taxicab-pdf: add peter lang tail packet`
publishes the queue, scrubbed report, and provider packet.
Nomos eLibrary bounded reharvest `pdf-nomos-elibrary-missing4-reharvest-b4bbab0`
tested 4 rows from `www.nomos-elibrary.de` and accepted 0 `good_pdf`; all four
rows stayed `missing_pdf_harvest` after status-201 HTML captures resolving to
`www.inlibra.com/de/document/view/detail/uuid/...`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`d7d1220d #461 taxicab-pdf: add nomos elibrary tail packet` publishes the
queue, scrubbed report, and provider packet.
Journal of Pediatric Surgery bounded reharvest
`pdf-jpedsurg-missing4-reharvest-66bf4f1` tested 4 rows from
`www.jpedsurg.org` and accepted 0 `good_pdf`; all four rows stayed
`missing_pdf_harvest` after status-201 HTML captures resolving to
`www.jpedsurg.org/article/.../abstract`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`d6c52a5b #461 taxicab-pdf: add jpedsurg tail packet` publishes the queue,
scrubbed report, and provider packet.
JBC bounded reharvest `pdf-jbc-missing4-reharvest-83f5456` tested 4 rows from
`www.jbc.org` and accepted 0 `good_pdf`; all four rows stayed
`missing_pdf_harvest` after status-201 HTML captures resolving to
`www.jbc.org/article/.../fulltext`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `c5a71e38 #461 taxicab-pdf: add jbc tail packet` publishes the
queue, scrubbed report, and provider packet.
ADS bounded reharvest `pdf-adsabs-missing4-reharvest-1b03675` tested 4 rows
from `ui.adsabs.harvard.edu` and accepted 4 `good_pdf`; read-only confirmation
`pdf-adsabs-missing4-readonly-1b03675` preserved 4 durable PDFs at
`articles.adsabs.harvard.edu`, with 0 timeout and 0 `taxicab_error`. Oxjobs
commit `34c32f5f #461 taxicab-pdf: add adsabs recovery` publishes the queue,
summaries, and reports. This is a positive bounded recovery, not an accepted
full-10K KPI lift until a full read-only gate confirms the corpus-level impact.
NCTM bounded reharvest `pdf-nctm-missing4-reharvest-97bcaa1` tested 4 rows
from `pubs.nctm.org` and accepted 1 `good_pdf`; read-only confirmation
`pdf-nctm-missing4-readonly-97bcaa1` preserved 1 durable PDF, with 3 missing
rows, 0 timeout, and 0 `taxicab_error`. The recovered route used
`downloadpdf/view`; the three residual `downloadpdf/journals` routes stored
XML article HTML and produced no durable PDF records. Oxjobs commit
`877d1107 #461 taxicab-pdf: add nctm recovery` publishes the queue, summaries,
reports, provider packet, and next AAAHQ queue. This is a positive bounded
recovery, not an accepted full-10K KPI lift until a full read-only gate
confirms the corpus-level impact.
AAAHQ bounded reharvest `pdf-aaahq-missing4-reharvest-7f47ce9` tested 4 rows
from `publications.aaahq.org` and accepted 0 `good_pdf`; three rows returned
invalid PDF content and one row stored article abstract HTML instead of PDF
bytes. Read-only confirmation `pdf-aaahq-missing4-readonly-7f47ce9` returned
all four rows to `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `63789cfc #461 taxicab-pdf: add aaahq tail packet` publishes the
queue, summaries, reports, provider packet, and next EJSO queue. AAAHQ is a
provider/Zyte corrupt-PDF and HTML-fallback lane, not a production-code win.
EJSO bounded reharvest `pdf-ejso-missing4-reharvest-30ce1b5` tested 4 rows
from `www.ejso.com` and accepted 0 `good_pdf`; all four candidate `/pdf`
routes resolved to article `/abstract` HTML and produced no durable PDF
records. Read-only confirmation `pdf-ejso-missing4-readonly-30ce1b5` returned
all four rows to `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `fc590d0f #461 taxicab-pdf: add ejso tail packet` publishes the
queue, summaries, reports, provider packet, and next AUA Journals queue. EJSO
is a provider/Zyte PDF-byte lane, not a production-code win.

Current next lane: send/test Zyte guidance for ScienceDirect, Lancet, Cell,
Wiley, De Gruyter, Lippincott, Oxford, CUP/Cambridge, SSRN, RSC, AIP, Taylor API
chapter-download, ACS, SPIE, Thieme, Sage, Brill, AMA/JAMA, APS, ACM, BMJ,
Karger, Optica, JSTOR, Inlibra, Scientific.net, Persee, Nature, J-STAGE,
University of Chicago Journals, ASME, Cairn, Physiology, ASCE, PDCNet, EurekaSelect, ActaHort, V&R eLibrary, IWA Publishing, AMS journals, JPET/ASPET, OnePetro, Mary Ann Liebert, AACR Figshare, AMPP, Healio, Sage Knowledge, IGI Global, UC Press, RUPress, Emerald, JACC, AJO, BioOne, Canadian Science Publishing, Edward Elgar, American Concrete Institute, American Journal of Surgery, AJOG, Scholarly Publishing Collective, Royal Society Publishing, KoreaScience, Journal of Pharmaceutical Sciences, CHEST, Green Journal, SciELO, AIP `pubs.aip.org`, DOI-router, ScienceDirect direct asset, and Springer `link.springer.com` rows
before production route code, plus De Gruyter Brill, AIAA, Neurology, Begell
House, MIT Press Direct, RSNA, Gold Journal, ATS Journals, and Transcript
Verlag residual/candidate-quality rows, PNAS corrupt PDF rows, Peter Lang
HTML/no-record rows, Nomos/Inlibra HTML/no-record rows, JPedsurg
abstract-HTML/no-record rows, and JBC fulltext-HTML/no-record rows. ADS is a
positive bounded recovery lane. NCTM is a partial-positive bounded recovery
lane with residual XML-HTML/no-record provider debt. AAAHQ is a corrupt/HTML
provider lane with no durable recovered PDFs. EJSO is an abstract-HTML/no-record
provider lane with no durable recovered PDFs. AUA Journals is an HTML/no-record
provider lane with no durable recovered PDFs. Springer Publishing is an
HTML/no-record provider lane with no durable recovered PDFs. Vestnik/KRSU is an
HTML/no-record provider lane with no durable recovered PDFs. Duke University
Press is an abstract-HTML/no-record provider lane with no durable recovered
PDFs. GeoScienceWorld is an abstract-HTML/no-record provider lane with no
durable recovered PDFs. Indian Journals is an HTML/no-record provider lane with
no durable recovered PDFs. AJConline is an abstract-HTML/no-record provider
lane with no durable recovered PDFs. IATED is an invalid-PDF/no-record provider
lane with no durable recovered PDFs. Brepols is an invalid-PDF/no-record
provider lane with no durable recovered PDFs. Copernicus Meeting Organizer is
an HTML-capture/no-record provider lane with no durable recovered PDFs. Google
Drive is a viewer-HTML/no-record provider lane with no durable recovered PDFs.
protocols.io is a partial-positive direct-PDF lane with two durable recovered
PDFs and one residual corrupt/validator row. ASA/Scitation is an
HTML-capture/no-record provider lane with no durable recovered PDFs. IOS Press
is an invalid-PDF/HTML provider lane with no durable recovered PDFs. AAI
Journals is an HTML/no-record provider lane with no durable recovered PDFs.
JCVA Online is an abstract-HTML/invalid-PDF provider lane with no durable
recovered PDFs. Human Kinetics is a partial-positive lane with one durable PDF
and two residual XML-HTML/no-record rows. If continuing independent technical
work, use the accepted full rows from
`pdf_eval_runs/pdf-full10k-after-structured-parser-a61d34b/rows.ndjson` and
start by publishing the Wiley PDF-direct candidate evidence to oxjobs #461. The
all-row residual Wiley probe `wiley-residual-corrupt-provider-probe-19-a61d34b`
recovered 15/19 as `good_pdf`, and Taxicab commit `3b2d218` local `http_get`
validation recovered 13/19 without Taxicab writes. The remaining residuals were
empty/bot/JS/preview cases. Oxjobs commit `d4f99eee` publishes the candidate
evidence; next decide bounded confirmation without a Taxicab main push. IOP
is accepted as the first repeated whole-corpus PDF KPI lift; the
structured-parser gate is the latest accepted measurement gate at 2,193/6,293
`good_pdf` (34.85%), +356 versus the denominator baseline, and the gap to 95%
remains 3,786 rows.

## Absolute paths

- Active Taxicab repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`
- Do not use: `/Users/shubh-trips/Documents/openalex-taxicab`
- Oxjobs #133 report/control repo for HTML: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`
- New PDF oxjob/report: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf` after creation with `scripts/create-job.py`
- Taxicab issue registry: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-harvest-router-issues` (#329)
- Parseland-only report: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/parseland-work-reporting` (#336). Do not put Taxicab V1 KPIs there.

## Git state to expect

- Taxicab branch for PDF Phase 2: `codex/taxicab-pdf-phase2`.
- Taxicab main-sync commit: `07c974e taxicab: sync phase 1 eval context`.
- Latest accepted production measurement is `full10k-mdpi-jbc-preprints-clean-e22b60e`: **9,583/10,000 `good_html` (95.83%)**, target crossed by 83 rows, +135 rows over the Oxford gate, 0 good-to-non-good regressions.
- Production `main` contains the accepted Preprints, JBC, and MDPI retrieval fixes plus deploy-stability/health-check changes:
  - `9ef6c9b taxicab: use browser html for preprints`
  - `ab5de79 taxicab: use resolved browser routes after doi redirects`
  - `5aba149 taxicab: route jbc linkinghub dois to fulltext`
  - `876887a taxicab: use browser html for mdpi`
  - `62b5f01 taxicab: wait for ecs deploy stability`
  - `54bbe83 taxicab: make health check lightweight`
  - `e22b60e taxicab: use threaded gunicorn workers`
- The old Taxicab branch `codex/taxicab-v1-eval-system` contains the Phase 1 eval/docs history. Main already contains the accepted production HTML routing fixes. This sync slice brings the non-production eval/docs/handoff state onto main without changing production scraping behavior.
- Taxicab production `main` auto-deploys to ECS. Further production pushes still require targeted proof plus full no-regression proof if scraping behavior changes.
- Oxjobs main has #133 reporting updates through `89c21749 #133 taxicab-audit: accept mdpi jbc preprints full gate`. Public raw report verified live with `95.83%`, `9,583`, `MDPI +119`, and inline `<svg class="curve"`.

## Current accepted measurement

Accepted full run: `full10k-mdpi-jbc-preprints-clean-e22b60e`

```text
good_html: 9,583 / 10,000
good_html_rate: 95.83%
gap_to_95_rows: 0
rows_above_95: 83
non_good_rows: 417
latest_lift_vs_oxford_gate: +135 good_html rows
good_to_non_good_regressions: 0
recovered_publishers: MDPI +119, Elsevier/JBC +8, Rxiv/Preprints +8
residual_clusters: current queue in oxjobs evidence/report133-quarry-residual-clusters-e22b60e.json
```

Category counts:

```text
good_html: 9583
pdf_instead_of_html: 135
bot_block_403: 65
empty_response: 59
js_required: 55
missing_harvest: 48
router_only: 38
download_404: 0
invalid_content: 17
taxicab_error: 0
timeout: 0
```

## Newly accepted recovery lanes

These are now accepted into the public #133 KPI. Do not rerun them unless new residual rows appear.

```text
MDPI router cluster: reharvest 119/119 good_html; read-only confirmation 119/119
JBC empty-response cluster: reharvest 8/8 good_html; read-only confirmation 8/8
Preprints router cluster: reharvest 8/8 good_html; read-only confirmation 8/8
Full 10K read-only gate: 9,583/10,000 good_html; +135 rows; 0 regressions
```

Authoritative local artifacts:

```text
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/rows.ndjson
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/summary.json
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/hardness.json
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/report.html
eval_runs/full10k-mdpi-jbc-preprints-clean-e22b60e/rows.ndjson
eval_runs/full10k-mdpi-jbc-preprints-clean-e22b60e/summary.json
eval_runs/full10k-mdpi-jbc-preprints-clean-e22b60e/hardness.json
eval_runs/full10k-mdpi-jbc-preprints-clean-e22b60e/report.html
eval_runs/mdpi119-reharvest-e22b60e/summary.json
eval_runs/mdpi119-readonly-e22b60e/summary.json
eval_runs/jbc8-reharvest-e22b60e/summary.json
eval_runs/jbc8-readonly-e22b60e/summary.json
eval_runs/preprints8-reharvest-e22b60e/summary.json
eval_runs/preprints8-readonly-e22b60e/summary.json
/tmp/taxicab-oxford-reharvest/oxford11-reharvest-before-route-d1aa4ef/summary.json
/tmp/taxicab-oxford-reharvest/oxford11-readonly-after-reharvest-d1aa4ef/summary.json
/tmp/taxicab-oxford-reharvest/oxford-timeout3-sentinel-d1aa4ef/summary.json
/tmp/taxicab-oxford-reharvest/quarry-full10k-oxford-d1aa4ef/residual-clusters.json
/tmp/taxicab-oxford-reharvest/quarry-full10k-oxford-d1aa4ef/browserbase-candidates.csv
/tmp/taxicab-oxford-reharvest/quarry-full10k-oxford-d1aa4ef/zyte-support-candidates.csv
/tmp/taxicab-uq-espace/uq2-reharvest-retry-d1aa4ef/summary.json
/tmp/taxicab-uq-espace/doiorg-recoverable4-readonly-final-d1aa4ef/summary.json
/tmp/taxicab-missing48-asme/missing48-reharvest-asme-fab783d/summary.json
```

## What is already done

- Eval harness exists and is runnable without importing Flask `app.py`.
- Taxonomy and artifact writers exist.
- `--row-timeout` exists and prevents hung live rows from blocking a whole run.
- Browserbase evidence fields stay separate from Taxicab baseline category.
- ScienceDirect PDF asset rewrite was deployed to Taxicab `main` at `bd4a8e3` and accepted by full 10K read-only gate: +19 `good_html`, 0 regressions.
- Residual missing-harvest tail was accepted by full 10K read-only gate: +19 `good_html`, 0 regressions.
- ASME browserHtml routing was deployed to Taxicab `main` at `fab783d` and accepted by the production loop: bounded ASME reharvest recovered 7/8, one-row retry recovered the last row, final ASME read-only confirmation was 8/8 `good_html`, and the clean full 10K gate accepted 9,436/10,000 `good_html` (94.36%), net +4 rows.
- UQ eSpace browserHtml routing was deployed to Taxicab `main` at `d1aa4ef` and accepted by the production loop: targeted UQ reharvest recovered 2/2 after ECS propagation, the four DOI.org recoverable rows read back as 4/4 `good_html`, and the clean full 10K gate accepted 9,440/10,000 `good_html` (94.40%), net +4 rows, gap 60, 0 good-to-non-good regressions.
- Remaining `missing_harvest` tail was rechecked after the ASME gate: bounded reharvest recovered 0/48, with 20 still missing, 21 `invalid_content`, six timeout, and one bot block. Treat this tail as lower priority.
- Browserbase evidence runner was changed on branch commit `2df8910` to use Browserbase REST APIs instead of the local Browserbase Python SDK.
- Report #133 has a report-336-style graph. The graph is embedded inline from `evidence/curve-latest.svg`, matching #336's inline-SVG pattern and avoiding iframe-relative asset resolution failures.
- Live #133 graph verification passed after oxjobs commit `89c21749`: public raw report contains `<svg class="curve"` and not `<img class="curve"`. Latest live report contains `95.83%`, `9,583/10,000`, `MDPI +119`, `Elsevier/JBC +8`, and `Rxiv/Preprints +8`; the MDPI/JBC/Preprints full-gate JSON returns 9,583 `good_html`.
- MDPI Browserbase session evidence was expanded on 2026-06-11: Taxicab stayed `router_only` for 10/10 sampled MDPI rows, while Browserbase full sessions recovered `good_html` for 10/10. Compact public artifact: `working/taxicab-audit/evidence/report133-mdpi-browserbase-session-expanded10-9287bb9.json`.
- IOP Browserbase session evidence was completed on 2026-06-11: current Taxicab read-only stayed `bot_block_403` for 14/14 `iopscience.iop.org` residual rows; Browserbase sessions recovered article-level `good_html` for 2/14 and stayed `bot_block_403` for 12/14, with screenshots captured for 14/14. Compact public artifact: `working/taxicab-audit/evidence/report133-iop-browserbase-session-fc4896d.json`; support packet: `working/taxicab-audit/evidence/report133-iop-zyte-support-packet.md`.
- Browserbase evidence classifier was tightened on branch commits `a6bfebf` and `0522d6e` so generic 404/520/browser error pages no longer count as Browserbase `good_html`. Tests now cover large error pages and real articles that merely mention 404/520 terms.
- DOI.org JS-required cluster was triaged on 2026-06-11: Taxicab remains non-good for 11/11 rows after the error-page guard (10 `js_required`, one `invalid_content`); Browserbase sessions recovered article-level `good_html` for 4/11 and classified 7/11 as invalid/error. Compact public artifact: `working/taxicab-audit/evidence/report133-doiorg-js-browserbase-session-0522d6e.json`; triage note: `working/taxicab-audit/evidence/report133-doiorg-js-triage-0522d6e.md`.
- Wolters Kluwer/Lippincott JS-required cluster was triaged on 2026-06-12: Taxicab read-only remains `js_required` for 11/11 rows on `login.wolterskluwer.com`; the first Browserbase pass exposed a false-positive `good_html` bug on `Page Expired` login pages; branch commit `2acd1eb` fixes expired-login evidence classification; corrected Browserbase session evidence is 0/11 `good_html`, 11/11 `invalid_content`, with 11 screenshots captured locally. Compact public artifact: `working/taxicab-audit/evidence/report133-wolterskluwer-pageexpired-browserbase-session-2acd1eb.json`; triage note: `working/taxicab-audit/evidence/report133-wolterskluwer-pageexpired-triage-2acd1eb.md`.
- ASME JS-required cluster was completed on 2026-06-12: initial Taxicab read-only was 8/8 `js_required`; Browserbase sessions recovered 5/8 article pages; direct Zyte no-storage browserHtml recovered 6/8; production main `fab783d` deployed the narrow ASME browserHtml route; bounded reharvest plus one-row retry recovered 8/8; final read-only confirmation stayed 8/8 `good_html`; full 10K accepted `full10k-asme-deployed-clean-fab783d` at 9,436/10,000 `good_html`. Public artifacts: `working/taxicab-audit/evidence/report133-asme-browserhtml-candidate-619739d.json`, `working/taxicab-audit/evidence/report133-asme-reharvest-live-fab783d.json`, `working/taxicab-audit/evidence/report133-asme-readonly-after-reharvest-fab783d.json`, and `working/taxicab-audit/evidence/report133-asme-fullgate-fab783d.json`.
- UQ eSpace / DOI.org recoverable rows were completed on 2026-06-12: two UQ eSpace DOI.org rows required Zyte `browserHtml=true` to avoid a small browser-compatibility shell, while the ASM Digital Library and Kyobo Scholar rows recovered after DOI.org final-host reharvest/read-back. Production main `d1aa4ef` deployed the narrow UQ eSpace browserHtml route; full 10K accepted `full10k-uq-deployed-clean-d1aa4ef` at 9,440/10,000 `good_html`. Public artifacts: `working/taxicab-audit/evidence/report133-uq-reharvest-d1aa4ef.json`, `working/taxicab-audit/evidence/report133-uq-readonly-d1aa4ef.json`, and `working/taxicab-audit/evidence/report133-uq-fullgate-d1aa4ef.json`.
- Oxford/OUP cache-refresh was completed on 2026-06-12 with no production code change: targeted Oxford reharvest recovered 8/11 non-good rows, read-only confirmation persisted 8/11, and a three-row timeout sentinel cleared aggressive full-run measurement artifacts. The clean full 10K gate accepted `full10k-oxford-reharvest-clean-d1aa4ef` at 9,448/10,000 `good_html` (94.48%), net +8 rows, gap 52, 0 good-to-non-good regressions, 0 `timeout`, and 0 `taxicab_error`. Public artifacts: `working/taxicab-audit/evidence/report133-oxford-reharvest-d1aa4ef.json`, `working/taxicab-audit/evidence/report133-oxford-readonly-d1aa4ef.json`, `working/taxicab-audit/evidence/report133-oxford-timeout-sentinel-d1aa4ef.json`, and `working/taxicab-audit/evidence/report133-oxford-fullgate-d1aa4ef.json`.
- Preprints local recovery was proven on 2026-06-13: the Oxford residual set had eight `router_only` rows on `preprints.org`; default Zyte through the DOI URL returned 2.6-2.8 KB privacy/router shells, while forced `browserHtml` on the resolved Preprints URL returned 331 KB to 1.86 MB article HTML for 8/8 rows. Early production reharvest still saw old behavior until the ECS rollout issue was diagnosed; the final accepted gate recovered 8/8.
- JBC local recovery was proven on 2026-06-13: eight `jbc.org` `empty_response` rows were old Elsevier/LinkingHub DOIs landing on tiny `/pdf` viewer shells; local routing rewrites compact JBC PII URLs to `https://www.jbc.org/article/<PII>/fulltext`; 8/8 no-storage probes classified `good_html`. Early `/test-zyte` probes were mixed while old tasks were still serving; the final accepted gate recovered 8/8.
- MDPI local recovery was proven on 2026-06-13: residual cluster had 119 `router_only` rows on `mdpi.com`; 10-row Taxicab read-only confirmation stayed `router_only`; Browserbase session evidence recovered 10/10; local Zyte `browserHtml` on the resolved MDPI URL recovered 10/10 large article pages with article signals. After threaded Gunicorn rollout, the final accepted gate recovered 119/119.
- Deploy-stability instrumentation was added on 2026-06-13: `.github/workflows/aws.yml` now waits for ECS service stability after `update-service`, and `/` plus `/health` are lightweight JSON health endpoints while the old metadata response moved to `/metadata`. The default deploy waiter timed out on the large service, but live load-balancer health and full retrieval gates later validated the accepted `e22b60e` production state.
- Threaded Gunicorn workers were deployed on 2026-06-13 to reduce rollout health-check starvation. The default ECS waiter still timed out on the large service, but live root sampling after rollout returned 12/12 quick new-health responses and targeted `/test-zyte` checks confirmed new MDPI/JBC/Preprints routing.
- MDPI/JBC/Preprints crossed the target on 2026-06-13: targeted production gates recovered MDPI 119/119, JBC 8/8, and Preprints 8/8; the clean full 10K read-only gate accepted 9,583/10,000 `good_html` (95.83%), +135 rows, 0 `timeout`, 0 `taxicab_error`, and 0 good-to-non-good regressions. Public oxjobs #133 raw report and full-gate JSON were verified live after cache lag.

## Browserbase and secrets

- Do not print secrets.
- Load local ignored credential files before asking Shubh to authenticate. Active Taxicab `.env` has provider/R2/Zyte material and `.env.aws` has AWS CLI-style session variables. Do not echo values. Ask for auth only if a safe command proves the local session is expired or the files are missing.
- Do not say Browserbase credentials are missing until you have checked ignored local env files and safe AWS/env discovery without printing values. Browserbase REST evidence has already worked in this environment; project ID was not required for the current REST session path.
- Live probe result: Browserbase REST session create returned HTTP 201 in 0.22s and release returned HTTP 200.
- Current runner state: local Playwright startup passed, and `--with-browserbase --browserbase-mode session` completed the 10-row MDPI sample under `--row-timeout 150`. Keep using row watchdogs for Browserbase session loops.

## PDF Phase 2 work contract

Do not treat any PDF-like response as success. A PDF row is `good_pdf` only
when Taxicab retrieves the correct, complete full-text PDF for the expected
OpenAlex work. The validator must reject HTML/interstitial/paywall bodies,
empty/corrupt/truncated PDFs, encrypted unreadable PDFs, supplements, previews,
and wrong-work PDFs.

PDF Phase 2 categories:

```text
good_pdf
no_pdf_expected
missing_pdf_harvest
download_404
bot_block_403
timeout
html_instead_of_pdf
js_redirect_unresolved
interstitial_or_paywall
empty_response
corrupt_or_truncated_pdf
wrong_pdf_content
supplement_or_preview_pdf
encrypted_or_unreadable_pdf
taxicab_error
```

Required PDF workflow:

```bash
git checkout main
git pull --rebase origin main
git checkout -b codex/taxicab-pdf-phase2
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
```

Then create the oxjobs report surface from a clean oxjobs tree:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/oxjobs
git pull --rebase
scripts/create-job.py taxicab-pdf --owner shubhankar --status working
```

## Immediate next actions

### 0. Finish the HTML main-sync gate

Complete.

Verification:

```text
commit: 07c974e taxicab: sync phase 1 eval context
push: origin/main
unit tests: 54 passed
fixture smoke: passed, 20 fixtures, 11 categories
live read-only smoke: passed, 8 rows, 0 timeout, 0 taxicab_error
secret pattern scan: no raw secret pattern findings
```

### 1. Create the PDF oxjobs report/control job

Complete.

```text
job: #461 taxicab-pdf
creation commit: 55396854 #461 taxicab-pdf: create job
scaffold commit: 0ad032e2 #461 taxicab-pdf: add report scaffold
report manifest: working/taxicab-pdf/report.yaml
```

### 2. Commit the PDF offline harness

Complete.

```text
commit: e53adae taxicab: add pdf eval fixture harness
python3 -m unittest discover -s tests: 62 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke: passed, 15 fixtures, 15 categories
git diff --check: passed
secret pattern scan: no raw secret pattern findings
```

### 3. Commit the PDF read-only live-smoke path

Complete.

```text
commit: 6661cde taxicab: add pdf read-only eval path
python3 -m unittest discover -s tests: 64 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --run-id pdf-live-smoke --out /tmp/taxicab-pdf-live-smoke --timeout 30 --retries 1 --progress-every 1: passed
live smoke counts: 1 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
```

### 4. Commit the PDF limit-100 baseline state

Complete.

```text
commit: e011267 taxicab: record pdf limit-100 baseline
run_id: pdf-limit100-readonly-6661cde
good_pdf: 1
missing_pdf_harvest: 77
corrupt_or_truncated_pdf: 19
encrypted_or_unreadable_pdf: 2
bot_block_403: 1
timeout: 0
taxicab_error: 0
```

### 5. Commit the PDF EOF-validator correction

Current verification:

```bash
python3 -m unittest tests.test_pdf_eval_harness
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-eof --out /tmp/taxicab-pdf-fixture-smoke-eof
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out pdf_eval_runs/ --run-id pdf-limit100-readonly-eof-fix --timeout 45 --retries 1 --progress-every 10
```

Corrected result:

```text
good_pdf: 15
missing_pdf_harvest: 77
corrupt_or_truncated_pdf: 5
encrypted_or_unreadable_pdf: 2
bot_block_403: 1
timeout: 0
taxicab_error: 0
```

Commit/push:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-eof-final --out /tmp/taxicab-pdf-fixture-smoke-eof-final
git diff --check
python3 scripts/secret_scan.py
git add openalex_taxicab/pdf_eval_harness.py tests/test_pdf_eval_harness.py GOAL.md NEXT_TO_DO.md AGENTS.md CLAUDE.md
git commit -m "taxicab: fix pdf eof validation"
git pull --rebase origin codex/taxicab-pdf-phase2
git push origin codex/taxicab-pdf-phase2
```

### 6. Run the full 10K PDF read-only baseline

Complete.

```text
run_id: pdf-full10k-readonly-22b78b7
good_pdf: 2,148 / 10,000
good_pdf_rate: 21.48%
gap_to_95_rows: 7,352
missing_pdf_harvest: 7,230
corrupt_or_truncated_pdf: 453
encrypted_or_unreadable_pdf: 121
html_instead_of_pdf: 13
js_redirect_unresolved: 13
supplement_or_preview_pdf: 11
interstitial_or_paywall: 9
bot_block_403: 2
timeout: 0
taxicab_error: 0
```

### 7. Publish the full baseline to oxjobs #461

Complete in oxjobs commit `9fb20f77`, with cluster table refinement in
`c1108056`.

### 8. Commit denominator enrichment and rerun full baseline

Complete.

```text
commit: 3f7cd47 taxicab: derive pdf expected denominator
run_id: pdf-full10k-denominator-3f7cd47
pdf_expected_total: 6,293
good_pdf: 1,837
good_pdf_rate: 29.19%
gap_to_95_rows: 4,142
no_pdf_expected: 3,707
missing_pdf_harvest: 3,939
corrupt_or_truncated_pdf: 373
encrypted_or_unreadable_pdf: 102
timeout: 0
taxicab_error: 0
```

### 9. Publish denominator-enriched baseline to oxjobs #461

Complete in oxjobs commit `088b019d`.

### 10. Commit gated PDF reharvest mode

Current verification:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-reharvest --out /tmp/taxicab-pdf-fixture-smoke-reharvest
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 5 --reharvest --workers 2 --out /tmp/taxicab-pdf-reharvest-smoke --run-id pdf-reharvest-smoke-5 --timeout 45 --retries 1 --progress-every 1
```

Result:

```text
0/5 good_pdf
3 corrupt_or_truncated_pdf
2 missing_pdf_harvest
0 timeout
0 taxicab_error
```

### 11. Confirm Elsevier sample recovery and update oxjobs #461

Completed confirmation command:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
git switch codex/taxicab-pdf-phase2
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-25.csv --out pdf_eval_runs/ --run-id pdf-elsevier-missing-readonly-after-reharvest-be2f5c7 --workers 4 --row-timeout 120 --timeout 60 --retries 1 --progress-every 1
```

Next exact commands:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
git switch codex/taxicab-pdf-phase2
python3 - <<'PY'
import csv
from pathlib import Path
with Path("pdf_eval_runs/residual-clusters.csv").open(newline="", encoding="utf-8") as f:
    for row in list(csv.DictReader(f))[:20]:
        print(f"{row['rank']}\t{row['category']}\t{row['publisher']}\t{row['host']}\t{row['count']}\t{row['recommended_agent']}\t{row['evidence_strength']}")
PY
```

### 12. Continue from the post-95 HTML residual queue only if PDF work is paused

Use the accepted post-95 queue:

```text
oxjobs: working/taxicab-audit/evidence/report133-quarry-residual-clusters-e22b60e.json
browserbase candidates: working/taxicab-audit/evidence/report133-browserbase-candidates-e22b60e.csv
zyte candidates: working/taxicab-audit/evidence/report133-zyte-support-candidates-e22b60e.csv
```

The next high-signal work is PDF-vs-landing splitting, IOP/MUSE bot-block evidence, Optica/Crossref/router cleanup, residual DOI.org JS host splitting, and unknown-publisher interpretability. MDPI, JBC, and Preprints are complete unless new residual rows appear.

### 9. If making production scraping changes

Keep the loop strict:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
targeted cluster eval
full 10K read-only gate if production behavior changed
```

Do not update the public KPI from a targeted gate alone. Full gate acceptance still requires 0 unexplained good-to-non-good regressions, 0 `taxicab_error`, and no unresolved timeout artifacts.

### 9. ECS deploy notes

The default `aws ecs wait services-stable` can time out on this large service even after useful tasks are serving. The accepted `e22b60e` rollout was validated by live LB checks and targeted/full retrieval gates after the waiter timed out. When AWS auth is fresh, inspect target health directly instead of relying only on the GitHub waiter:

```bash
aws ecs describe-services --cluster harvester --services harvester-service
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
aws logs tail <log-group> --since 30m
```

If local AWS auth is expired, ask Shubh to refresh with `aws login`. The ignored `.env` and `.env.aws` files exist, but a previous safe check showed the refreshed credentials were still expired. Do not print values from either file.

### 10. IOP bot-block cluster

Evidence complete; next action is Envoy/Zyte support, not a Taxicab production patch.

```text
category: bot_block_403
publisher: iop
host: iopscience.iop.org
rows: 14
recommended agents: Lens + Envoy
Taxicab read-only confirmation: 14/14 bot_block_403
Browserbase full sessions: 2/14 good_html, 12/14 bot_block_403, 14/14 screenshots captured
```

Artifacts:

```text
/tmp/taxicab-iop-bot14-fc4896d.csv
/tmp/taxicab-iop-readonly/iop-bot14-readonly-fc4896d/
/tmp/taxicab-iop-browserbase/iop-bot14-browserbase-session-fc4896d/
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-iop-browserbase-session-fc4896d.json
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-iop-zyte-support-packet.md
```

Do not rerun this cluster unless checking a Zyte-side/provider-side change. Send the support packet or move Lens to the next residual JS/PDF/empty split.

### 5. Oxford/OUP cache-refresh

Complete and accepted. Do not rerun Oxford unless new residual rows appear in the current queue.

```text
production code change: none
targeted reharvest: 8/11 good_html
read-only confirmation: 8/11 good_html
timeout sentinel: 3/3 full-run timeout artifacts cleared as good_html
clean full 10K gate: full10k-oxford-reharvest-clean-d1aa4ef
public KPI: 9,448/10,000 good_html (94.48%)
net lift: +8 good_html rows
gap_to_95_rows: 52
good-to-non-good regressions: 0
taxicab_error: 0
timeout: 0
```

Artifacts:

```text
/tmp/taxicab-oxford-reharvest/oxford11-reharvest-before-route-d1aa4ef/
/tmp/taxicab-oxford-reharvest/oxford11-readonly-after-reharvest-d1aa4ef/
/tmp/taxicab-oxford-reharvest/oxford-timeout3-sentinel-d1aa4ef/
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-oxford-fullgate-d1aa4ef.json
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-quarry-residual-clusters-oxford-d1aa4ef.json
```

### 6. Optica router/wait shells

Prior Quarry noted `opg.optica.org` rows with `viewmedia.cfm?...html=true` wait shells. Current Oxford summary shows seven `opg.optica.org` router rows.

Next step: create a target DOI file from the Oxford residual cluster artifact, run read-only confirmation, then test URL cleanup or browserHtml no-storage. Do not patch until a narrow hypothesis recovers article HTML.

### 7. Crossref chooser and Project MUSE residuals

Current host matrix includes Crossref chooser/router rows, `muse.jhu.edu` verify/bot rows, preprints.org router rows, and JBC empty responses. These are Taxicab-side candidates only after separate host-specific probes.

Next step: split into separate DOI files by host (`preprints.org`, `jbc.org`, `muse.jhu.edu`, `opg.optica.org`, `crossref.org`), then test URL extraction/rewrite or browserHtml without storage.

### 8. DOI.org JS-required cluster

Evidence complete; next action is host-level splitting, not a broad Taxicab patch.

```text
category at baseline: js_required
publisher: unknown
host: doi.org
rows: 11
Taxicab after error-page guard: 10 js_required, 1 invalid_content, 0 good_html
Browserbase full sessions: 4 good_html, 5 invalid_content, 2 error
screenshots captured: 9/11
```

Artifacts:

```text
/tmp/taxicab-js-doiorg-unknown11-65ac863.csv
/tmp/taxicab-js-doiorg-readonly/js-doiorg-unknown11-readonly-65ac863/
/tmp/taxicab-js-doiorg-browserbase-final/js-doiorg-unknown11-browserbase-session-0522d6e/
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-doiorg-js-browserbase-session-0522d6e.json
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-doiorg-js-triage-0522d6e.md
```

Do not send this as one broad Zyte packet. The browser-recoverable rows are now complete: ASM Digital Library, UQ eSpace, and Kyobo Scholar read back as 4/4 `good_html` after targeted reharvest/read-only confirmation. Only revisit remaining DOI.org rows after splitting by final host.

### 9. Wolters Kluwer / Lippincott expired-login cluster

Evidence complete; next action is resolver/direct-article URL discovery, not a production Browserbase fallback and not a broad Zyte rendering packet from the stored URL.

```text
category at baseline: js_required
publisher: lippincott
host: login.wolterskluwer.com
rows: 11
Taxicab read-only confirmation: 11/11 js_required on Wolters Kluwer Ping authorization resume URLs
Browserbase full sessions after commit 2acd1eb: 0/11 good_html, 11/11 invalid_content, 11/11 screenshots captured
root evidence: rendered page title "Page Expired"; final URL stays login.wolterskluwer.com/as/.../resume/as/authorization.ping
```

Do not report these rows as browser-recoverable. If this cluster is revisited, first discover stable article landing URLs from DOI resolver metadata, LWW journal URLs, or publisher link templates, then run a targeted Taxicab/Browserbase comparison from those URLs.

### 10. HTML Phase 1 ASME browserHtml route

Complete and accepted for HTML landing-page retrieval. This is separate from
the current PDF Phase 2 ASME sample lane.

```text
production commit: fab783d taxicab: use browser html for asme
production deploy: GitHub Actions ECS deploy passed
targeted reharvest: 7/8 good_html, then one-row retry recovered 1/1
final ASME read-only confirmation: 8/8 good_html
clean full 10K gate: full10k-asme-deployed-clean-fab783d
public KPI: 9,436/10,000 good_html (94.36%)
net lift: +4 good_html rows
gross ASME recovery: +8 good_html rows
red regressions/reclassifications: 4 prior false-good error/expired-login pages now invalid_content
taxicab_error: 0
timeout: 0
```

Artifacts:

```text
/tmp/taxicab-asme-js8-8823957.csv
/tmp/taxicab-asme-deployed/asme-js8-reharvest-fab783d/
/tmp/taxicab-asme-deployed/asme-js8-readonly-final-fab783d/
eval_runs/full10k-asme-deployed-clean-fab783d/
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-asme-reharvest-live-fab783d.json
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-asme-readonly-after-reharvest-fab783d.json
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-asme-fullgate-fab783d.json
```

### 11. Missing-harvest residual tail

There are 48 `missing_harvest` rows left, including 35 unknown/unknown. The latest bounded reharvest recovered 0/48, so this is now lower-yield than MDPI, IOP, and host-specific JS/router work. Any further public KPI claim needs:

1. bounded reharvest with `--row-timeout`;
2. read-only confirmation of recovered rows;
3. timeout sentinel if any watchdog artifacts appear;
4. clean full 10K read-only gate.

### 12. UQ eSpace / DOI.org browserHtml route

Complete and accepted. Do not redo UQ unless new UQ eSpace residual rows appear.

```text
production commit: d1aa4ef taxicab: use browser html for uq espace
production deploy: GitHub Actions ECS deploy passed
targeted UQ reharvest after ECS propagation: 2/2 good_html
final DOI.org recoverable read-only confirmation: 4/4 good_html
clean full 10K gate: full10k-uq-deployed-clean-d1aa4ef
public KPI: 9,440/10,000 good_html (94.40%)
net lift: +4 good_html rows
good-to-non-good regressions: 0
```

Artifacts:

```text
/tmp/taxicab-uq-espace/uq2-reharvest-retry-d1aa4ef/
/tmp/taxicab-uq-espace/doiorg-recoverable4-readonly-final-d1aa4ef/
eval_runs/full10k-uq-deployed-clean-d1aa4ef/
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-uq-reharvest-d1aa4ef.json
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-uq-readonly-d1aa4ef.json
/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit/evidence/report133-uq-fullgate-d1aa4ef.json
```

### 13. #133 graph/report verification

Done after oxjobs commit `89c21749`: live report HTML contains `<svg class="curve"`, does not contain `<img class="curve"`, includes `95.83%`, and exposes the accepted MDPI/JBC/Preprints full-gate JSON. Re-run if the report is regenerated:

```bash
curl -L -sS -o /tmp/ox133.html https://oxjobs.org/reports/133
curl -L -sS -o /tmp/ox133-report.html 'https://oxjobs.org/reports/133/raw?path=evidence/report.html'
rg -n '95\.83%|9,583|MDPI \+119|Elsevier/JBC \+8|Rxiv/Preprints \+8|<svg class="curve"|<img class="curve"' /tmp/ox133-report.html
curl -L -sS -o /tmp/ox133-curve.svg -w '%{http_code} %{content_type}\n' 'https://oxjobs.org/reports/133/raw?path=evidence/curve-latest.svg'
curl -L -sS -o /tmp/ox133-fullgate.json -w '%{http_code} %{content_type}\n' 'https://oxjobs.org/reports/133/raw?path=evidence/report133-mdpi-jbc-preprints-fullgate-e22b60e.json'
```

Expected: report HTML contains `95.83%`, `9,583`, the three recovered-publisher lift lines, and `<svg class="curve"` but not `<img class="curve"`; the standalone curve asset returns `200 image/svg+xml`; the full-gate JSON returns `200 application/json`.

### 14. Browserbase session runner

The local Playwright startup check passed and the 10-row MDPI session sample completed. Keep using row watchdogs and low concurrency.

Useful checks:

```bash
pgrep -af 'taxicab_eval.py|playwright|node.*driver|browserbase|npm exec playwright'
python3 -m playwright --version
python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    print(p.chromium)
PY
```

If Playwright hangs again, do not keep launching long Browserbase session loops. Use existing completed Browserbase session artifacts for MDPI and move Envoy/Zyte support forward.

## Required gates before commits

Taxicab branch:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
git diff --check
rg -n "(ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY)=[^[:space:]]+|bm-verify=[A-Za-z0-9_-]{12,}|X-Amz-(Credential|Signature|Security-Token)=|hcvalidate\\.perfdrive\\.com/\\?ssa=" .
```

Oxjobs #133:

```bash
python3 scripts/publish-report.py 133
git diff --check -- working/taxicab-audit
rg -n "(ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY)=[^[:space:]]+|bm-verify=[A-Za-z0-9_-]{12,}|X-Amz-(Credential|Signature|Security-Token)=|hcvalidate\\.perfdrive\\.com/\\?ssa=" working/taxicab-audit
```

The regex exit code `1` means no matches, which is good.

## Commit and push rules

- Commit and push frequently after focused verification.
- Taxicab code branch commits go to `codex/taxicab-v1-eval-system` unless intentionally moving a production fix through `main`.
- Oxjobs reporting commits go to `main`, staging only `working/taxicab-audit`.
- Never bundle unrelated Parseland report files into Taxicab #133 commits.

## Stop and report

Stop and report instead of improvising if:

- a change would broadly alter production scraping behavior;
- a targeted or full gate shows a `good_html` regression;
- Browserbase sees content but Zyte cannot for a host cluster, because that is a Zyte support path first;
- a secret value or signed provider URL appears in any tracked file;
- AWS/ECS/deploy state contradicts the repo assumptions above.

## Current Sidecar Correction Check

Status: live five-row reharvest check completed on 2026-06-28.

Original sidecar was not mutated:

```text
/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/data/merged-FINAL-pdf-availability.draft.csv
```

Private corrected copy and mini sidecar:

```text
/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/data/merged-FINAL-pdf-availability.corrected-20260628.csv
/tmp/taxicab-corrected-attention5-sidecar.csv
```

What changed in the corrected copy:

```text
3 total row changes
1 Office-document download changed to no public PDF expected
2 stale PDF links changed to the PDF links found from Taxicab HTML through Parseland
```

Live check command:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
PYTHONPATH=. python3 scripts/taxicab_batch_e2e.py \
  --sidecar /tmp/taxicab-corrected-attention5-sidecar.csv \
  --batch-number 1 \
  --batch-size 5 \
  --out /tmp/taxicab-corrected-attention5-e2e \
  --workers 2 \
  --timeout 120 \
  --reharvest
```

Result:

```text
5 total rows
3 pass
2 fail
60.00% on these five rows
4 rows where a public PDF is expected
2 public PDFs found by Taxicab
0 review rows
```

Plain reading: the two stale-link corrections and the Office-document label
correction behave as expected. The remaining two rows need provider/source
follow-up, not a broad Taxicab route change.

Remaining-two Browserbase evidence check:

```text
run: remaining2-browserbase-20260628
rows checked: 2
Taxicab good_pdf: 0
Browserbase valid PDFs recovered: 0
ScienceDirect case: download started but Browserbase did not capture PDF bytes
source-host case: Browserbase rendered HTML, not PDF
local direct checks: ScienceDirect returned HTML/403; source host returned 403 or TLS failure
decision: provider/source evidence only; no broad Taxicab route change
```

Raw Browserbase JSON, screenshots, HTML, final URLs, DOI rows, and
signed/challenge URLs are local only under `/tmp/taxicab-remaining2-browserbase`
and must not be published.

Next exact command:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/oxjobs
python3 scripts/publish-report.py 461
git diff --check -- working/taxicab-pdf
rg -n "(ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY)=[^[:space:]]+|bm-verify=[A-Za-z0-9_-]{12,}|X-Amz-(Credential|Signature|Security-Token)=|hcvalidate\\.perfdrive\\.com/\\?ssa=" working/taxicab-pdf
```
