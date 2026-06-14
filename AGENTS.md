# OpenAlex Taxicab Agent Guide

Current goal state: HTML Phase 1 is complete at 9,583/10,000 `good_html`
(95.83%). PDF Phase 2 is active and targets >=95% `good_pdf` on the
PDF-expected portion of the 10K Goldie corpus. Read `GOAL.md` and
`NEXT_TO_DO.md` before changing code.

Latest PDF metric: accepted full 10K read-only gate
`pdf-full10k-after-karger-ca8b132` is 1,890/6,293 `good_pdf` (30.03%),
+53 rows versus the denominator baseline of 1,837/6,293 (29.19%) and +3 rows
versus the prior accepted gate, with `missing_pdf_harvest` down from 3,939 to
3,863, 0 good-to-non-good regressions, 0 timeout, and 0 `taxicab_error`. The
gap to 95% is now 4,089 rows.
Gated PDF reharvest mode is pushed at commit `8193c47`; the first committed
5-row smoke recovered 0/5. The Springer seed queue then recovered 1/12
(`10.1007/bf03544238`) and left 11 rows missing. Reharvest post-context
instrumentation is pushed at commit `b9d5918`; the rerun shows all 11 misses
received POST status 201 with `post content_type html`, not PDF. Treat Springer
as a Zyte-support/evidence cluster before production code changes.
PDF Browserbase evidence mode is pushed at commit `f424129`: it annotates non-good PDF rows
without changing baseline categories. The first Springer Browserbase session
smoke returned `html_not_pdf`, confirming the sample is not browser-recoverable
as a direct PDF.
PDF runner row-timeout watchdog is pushed at commit `be2f5c7`. Use
`--row-timeout` for PDF reharvest samples before scaling. The resumed Elsevier
true-missing sample `pdf-elsevier-missing-reharvest-25-84b2c05` finished with
4/25 `good_pdf`, 15 `missing_pdf_harvest`, 6 `corrupt_or_truncated_pdf`,
0 timeout, and 0 `taxicab_error`; this is localized sample recovery, not yet a
full-10K KPI lift.
Read-only confirmation `pdf-elsevier-missing-readonly-after-reharvest-be2f5c7`
shows the same 4/25 `good_pdf` and 21 `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`; the four recovered PDFs persisted as Taxicab records.
The 100-row Elsevier queue reharvest returned 6/100 `good_pdf`, 45
corrupt/truncated POST outcomes, 48 missing, and one timeout. A classifier
correction now treats `first-page-pdf` URLs as `supplement_or_preview_pdf`; the
corrected read-only result is 7/100 `good_pdf`, 92 missing, one preview, and
0 timeout / 0 `taxicab_error`.
Oxjobs #461 published this 100-row gate at commit `3d8a5fa0`. Next work is
Elsevier route/support clustering, not more blind reharvest.
Oxjobs commit `825c2e2d` adds the sanitized Elsevier route split:
34 ScienceDirect route rows, 11 invalid-PDF POST rows, 8 Lancet rows,
4 direct-asset rows, 3 Cell rows, 7 durable recoveries, and smaller
router/cross-publisher clusters. Next technical lane is no-storage
ScienceDirect route probing plus scrubbed Zyte examples.
Taxicab commit `741e9a7` adds the no-storage probe. Run
`sciencedirect-route-probe-3-741e9a7` tested 3 DOI candidates across 12 route
variants and recovered 0 PDFs. Oxjobs commit `666d0ed6` records the scrubbed
probe and Zyte packet `sciencedirect-pdf-viewer-html-741e9a7.md`.
Lancet run `lancet-route-probe-3-741e9a7` recovered 0/3 PDFs, with two 520
ban-free failures and one 404 HTML page. Oxjobs commit `2105c8f1` records the
Lancet probe and packet `lancet-pdf-ban-741e9a7.md`.
Cell Press run `cell-route-probe-3-741e9a7` recovered 0/3 PDFs, with login/JS
HTML instead of PDF bytes. Oxjobs commit `a160ec1a` records the Cell probe and
packet `cell-pdf-login-js-741e9a7.md`.
Browserbase run `pdf-browserbase-cell-1-3de630f` also returned `html_not_pdf`
for one Cell candidate; Browserbase did not recover a direct PDF. Raw
Browserbase artifacts stay local because the final URL included a Cloudflare
challenge token. Oxjobs commit `d0344d1d` records only the scrubbed public
summary `evidence/browserbase/cell-pdf-html-not-pdf-3de630f.json`.
Wiley run `pdf-wiley-missing-reharvest-25-4267740` recovered 0/25
`good_pdf`; all rows stayed `missing_pdf_harvest`, and POST accepted HTML
landing pages at Wiley DOI routes instead of PDF bytes. Oxjobs commit
`3d7356bc` records the scrubbed Wiley summary/report, Wiley Zyte packet, and
combined provider request `pdf-byte-fetch-provider-request-4267740.md`.
De Gruyter run `pdf-degruyter-missing-reharvest-25-95308b7` also recovered
0/25 `good_pdf`; POST accepted `/html` pages and direct no-storage `/pdf`
probes returned JS/robot-verification HTML. Oxjobs commit `de7d0f2d` records
the scrubbed De Gruyter summary/report and Zyte packet.
Lippincott run `pdf-lippincott-missing-reharvest-25-0405edf` also recovered
0/25 `good_pdf`; POST accepted article/abstract HTML pages and direct
no-storage `downloadpdf.aspx` probes returned secured-browser HTML. Oxjobs
commit `b88a5a79` records the scrubbed Lippincott summary/report and packet.
Oxford run `pdf-oxford-missing-reharvest-25-b259f2e` also recovered 0/25
`good_pdf`; POST accepted article/abstract HTML pages and direct no-storage
`article-pdf` probes returned Zyte 520 empty responses. Oxjobs commit
`e1fe9deb` records the scrubbed Oxford summary/report and packet.
CUP/Cambridge run `pdf-cup-missing-reharvest-25-39517e5` also recovered 0/25
`good_pdf`; POST accepted Cambridge Core HTML pages and direct no-storage
explicit PDF probes returned status 200 `text/html` Cambridge Core pages.
Oxjobs commit `df7784c9` records the scrubbed CUP/Cambridge summary/report and
packet. The combined provider request now covers ScienceDirect, Lancet, Cell,
Wiley, De Gruyter, Lippincott, Oxford, and CUP/Cambridge.
CUP/Cambridge strategy probe `cup-zyte-strategy-probe-1-26d3d5c` tested
default HTTP, PDF `Accept`, residential variants, and browser network capture;
none returned PDF bytes. Oxjobs commit `77e793a8` records the scrubbed summary.
SSRN run `pdf-ssrn-missing-reharvest-25-64b787f` recovered 0/25 `good_pdf`;
POST mostly accepted SSRN delivery/landing HTML, and direct delivery probes
returned SSRN HTML or removed-paper HTML. Oxjobs commit `ade1b60f` records the
scrubbed SSRN summary/report and packet.
IOP run `pdf-iop-missing-reharvest-25-2e2c123` recovered 16/25 `good_pdf`;
read-only confirmation preserved the same 16 durable records. Oxjobs commit
`7d376fa0` records the positive sample. Remaining IOP queue
`pdf-iop-remaining45-readonly-e5bcd30` preserved 21/45 more durable records.
Oxjobs commit `5cca142e` records the latest accepted full-gate impact:
+45 `good_pdf` on the 6,293-row PDF denominator. IOP is now the first repeated
whole-corpus PDF KPI lift, but still far short of the 95% target.
RSC run `pdf-rsc-missing48-reharvest-008fe7f` recovered 0/48 `good_pdf`, with
47 still `missing_pdf_harvest`, one timeout, and 0 `taxicab_error`. POST
accepted `/articlelanding/.../unauth` HTML pages instead of `articlepdf` bytes,
so RSC is now a Zyte/provider-advised PDF-byte lane, not a route-code change.
Oxjobs commit `68025078` records the RSC queue, summary, report, and packet.
AIP run `pdf-aip-missing45-reharvest-8ce7e7e` recovered 0/45 `good_pdf`, with
44 still `missing_pdf_harvest`, one corrupt/truncated response, and 0 timeout /
0 `taxicab_error`. POST returned status 201 HTML/no durable PDF for missing
rows, so AIP/Scitation is also a Zyte/provider-advised PDF-byte lane. Oxjobs
commit `85584ddd` records the AIP queue, summary, report, and packet.
Taylor runs recovered five durable direct TandF journal PDFs. The accepted full
gate `pdf-full10k-after-taylor-e7d1361` is 1,887/6,293 `good_pdf` (29.99%),
+5 vs prior gate and +50 vs denominator baseline, with 0 regressions,
0 timeout, and 0 `taxicab_error`. Taylor API chapter-download URLs still need
provider guidance. Oxjobs commit `574539d2` records the Taylor queues,
summaries, reports, graph update, and packet. Next technical lane: send/test
provider guidance for accumulated packets or choose a fresh high-volume
cluster.
ACS run `pdf-acs-missing25-reharvest-2b7996a` recovered 0/25 `good_pdf`, with
19 rows still `missing_pdf_harvest`, six `corrupt_or_truncated_pdf`, and
0 timeout / 0 `taxicab_error`. Oxjobs commit `482cc4fd` records the ACS queue,
scrubbed summary/report, provider packet, and combined request update. Treat ACS
as a Zyte/provider-advised PDF-byte and corrupt-PDF lane before route code.
SPIE run `pdf-spie-missing25-reharvest-62c6a33` recovered 0/25 `good_pdf`, with
all rows still `missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`. Oxjobs
commit `c5792694` records the SPIE queue, scrubbed summary/report, provider
packet, and combined request update. Treat SPIE as a Zyte/provider-advised
PDF-byte lane before route code.
Thieme run `pdf-thieme-missing25-reharvest-d0ea198` recovered 0/25 `good_pdf`,
with all rows still `missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`.
Oxjobs commit `8cb377c7` records the Thieme queue, scrubbed summary/report,
provider packet, and combined request update. Treat Thieme as a
Zyte/provider-advised PDF-byte lane before route code.
Sage run `pdf-sage-missing25-reharvest-2705643` recovered 0/25 `good_pdf`,
with 11 rows still `missing_pdf_harvest`, 14 `corrupt_or_truncated_pdf`,
0 timeout, and 0 `taxicab_error`. Oxjobs commit `ca3b11fe` records the Sage
queue, scrubbed summary/report, provider packet, and combined request update.
Treat Sage as a Zyte/provider-advised PDF-byte and invalid-PDF lane before
route code.
Brill run `pdf-brill-missing30-reharvest-7520bc1` recovered 0/30 `good_pdf`,
with all rows still `missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`.
Oxjobs commit `172b7580` records the Brill queue, scrubbed summary/report,
provider packet, and combined request update. Treat Brill as a
Zyte/provider-advised PDF-byte lane before route code.
AMA/JAMA run `pdf-ama-jama-missing25-reharvest-005b032` recovered 0/25
`good_pdf`, with 18 rows still `missing_pdf_harvest`, 7
`corrupt_or_truncated_pdf`, 0 timeout, and 0 `taxicab_error`. Oxjobs commit
`d82e9ba6` records the AMA/JAMA queue, scrubbed summary/report, provider packet,
and combined request update. Treat AMA/JAMA as a Zyte/provider-advised PDF-byte
and invalid-PDF lane before route code.
APS run `pdf-aps-missing23-reharvest-65feabe` recovered 0/23 `good_pdf`, with
all rows still `missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`.
Oxjobs commit `147a9e65` records the APS queue, scrubbed summary/report,
provider packet, and combined request update. Treat APS as a
Zyte/provider-advised PDF-byte lane before route code.
ACM run `pdf-acm-missing22-reharvest-5f81111` recovered 0/22 `good_pdf`, with
16 rows still `missing_pdf_harvest`, 5 `corrupt_or_truncated_pdf`, one timeout,
and 0 `taxicab_error`. Oxjobs commit `32d6a637` records the ACM queue,
scrubbed summary/report, provider packet, and combined request update. Treat
ACM as a Zyte/provider-advised PDF-byte lane before route code.
BMJ run `pdf-bmj-missing32-reharvest-4c213b6` recovered 0/32 `good_pdf`, with
31 rows still `missing_pdf_harvest`, one `corrupt_or_truncated_pdf`, 0 timeout,
and 0 `taxicab_error`. Oxjobs commit `3319e184` records the BMJ queue,
scrubbed summary/report, provider packet, and combined request update. Treat
BMJ as a Zyte/provider-advised PDF-byte lane before route code.
Karger run `pdf-karger-missing28-reharvest-9a8466e` recovered 3/28
`good_pdf`; read-only confirmation `pdf-karger-missing28-readonly-9a8466e`
preserved the same three durable PDFs, with 25 rows still
`missing_pdf_harvest`, 0 timeout, and 0 `taxicab_error`. Oxjobs commit
`ecae684b` records the Karger queue, scrubbed summaries/reports, provider
packet, and combined request update. Full gate
`pdf-full10k-after-karger-ca8b132` accepted the +3 at corpus scale with 0
good-to-non-good regressions, 0 timeout, and 0 `taxicab_error`; oxjobs commit
`5ccb3df5` publishes that report. Optica/opg run
`pdf-optica-missing21-reharvest-25496ec` recovered 0/21 `good_pdf`; all rows
stayed missing after status-201 HTML captures at `opg.optica.org/viewmedia.cfm`
routes, with 0 timeout and 0 `taxicab_error`. Oxjobs commit `826bd689`
publishes the Optica packet. JSTOR run `pdf-jstor-missing60-reharvest-dc6cafc`
recovered 0/60 `good_pdf`; all rows stayed missing after status-201 HTML
captures at `www.jstor.org/stable/pdf` routes, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `19ca1aff` publishes the JSTOR packet. Next
Inlibra run `pdf-inlibra-missing32-reharvest-54d17e9` recovered 0/32
`good_pdf`; all rows stayed missing after status-201 HTML captures at
`www.inlibra.com/document/download/pdf/uuid` routes, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `0df48262` publishes the Inlibra packet. Next
Scientific.net run `pdf-scientificnet-missing20-reharvest-4e6130f` recovered
0/20 `good_pdf`; all rows stayed missing after status-201 HTML captures at
`www.scientific.net` article pages, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `3b84fb4b` publishes the Scientific.net packet. Persee run
`pdf-persee-missing18-reharvest-af4baf7` recovered 0/18 `good_pdf`; every row
classified as `corrupt_or_truncated_pdf` after invalid PDF content, with
0 timeout and 0 `taxicab_error`. Oxjobs commit `1a7d1ddb` publishes the Persee
packet. Nature run `pdf-nature-missing17-reharvest-e7616c9` recovered 2/17
`good_pdf`, and read-only confirmation `pdf-nature-missing17-readonly-e7616c9`
preserved the same two durable PDFs; 15 rows remain missing. Oxjobs commit
`33c8c71c` publishes the Nature recovery/residual packet. J-STAGE run
`pdf-jstage-missing16-reharvest-43777d8` recovered 2/16 `good_pdf`, and
read-only confirmation `pdf-jstage-missing16-readonly-43777d8` preserved the
same two durable PDFs; residual rows are 8 corrupt/truncated, 1 encrypted, and
5 missing. Oxjobs commit `59789f72` publishes the J-STAGE recovery/residual
packet. University of Chicago Journals run
`pdf-uchicago-missing16-reharvest-6b41e44` recovered 0/16 `good_pdf`; all rows
stayed `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. POST
accepted HTML/no durable PDF records for `journals.uchicago.edu/doi/pdf` and
`/doi/epdf` routes, commonly resolving to `/doi/abs/...` article pages. Oxjobs
commit `95bde36b` publishes the UChicago provider packet. ASME run
`pdf-asme-missing15-reharvest-c1c2b86` recovered 0/15 `good_pdf`;
eight rows returned invalid PDF-like content and seven stayed
`missing_pdf_harvest` after status-201 HTML/no durable PDF captures, with
0 timeout and 0 `taxicab_error`. Oxjobs commit `10d80d80` publishes the ASME
provider packet. Cairn run
`pdf-cairn-missing20-reharvest-8742847` recovered 0/20 `good_pdf`; nineteen
rows returned invalid PDF-like content and one stayed `missing_pdf_harvest`,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit `97b61e38` publishes the
Cairn provider packet. Physiology run
`pdf-physiology-missing11-reharvest-6db1728` recovered 0/11 `good_pdf`; five
rows returned invalid PDF-like content and six stayed `missing_pdf_harvest`,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit `33d5cb5b` publishes the
Physiology provider packet. ASCE run
`pdf-asce-missing10-reharvest-e708434` recovered 0/10 `good_pdf`; five rows
returned invalid PDF-like content and five stayed `missing_pdf_harvest`, with
0 timeout and 0 `taxicab_error`. Oxjobs commit `b57dba2f` publishes the ASCE
provider packet. PDCNet run `pdf-pdcnet-missing9-reharvest-9cd3b93` recovered
0/9 `good_pdf`; all rows stayed `missing_pdf_harvest` after HTML purchase/form
captures, with 0 timeout and 0 `taxicab_error`. Oxjobs commit `a1663d3f`
publishes the PDCNet provider packet. EurekaSelect run
`pdf-eurekaselect-missing8-reharvest-d224066` recovered 0/8 `good_pdf`; six
rows returned invalid PDF-like content and two stayed `missing_pdf_harvest`,
with 0 timeout and 0 `taxicab_error`. Oxjobs commit `357c4ee1` publishes the
EurekaSelect provider packet. ActaHort run
`pdf-actahort-missing8-reharvest-8ce7ac3` recovered 0/8 `good_pdf`; all rows
stayed `missing_pdf_harvest` after status-201 HTML/no durable PDF captures from
`www.actahort.org/members/showpdf` routes, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `be526662` publishes the ActaHort provider
packet. V&R eLibrary run `pdf-vr-elibrary-missing7-reharvest-fdfa16c`
recovered 0/7 `good_pdf`; six rows stayed `missing_pdf_harvest` after reader
routes resolved to abstract HTML/no durable PDF records, and one explicit PDF
route returned invalid PDF-like content, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `c3d3b00b` publishes the V&R eLibrary provider packet. Next
IWA Publishing run `pdf-iwaponline-missing7-reharvest-bfa43c4` recovered 0/7
`good_pdf`; explicit article-PDF routes resolved to article-abstract HTML with
`redirectedFrom=PDF`, leaving no durable PDF records, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `98a037c1` publishes the IWA provider packet.
AMS journals run `pdf-ametsoc-missing7-reharvest-29cf658` recovered 0/7
`good_pdf`; explicit `journals.ametsoc.org/downloadpdf/view` routes returned
status 200 but no durable readable PDF records were created, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `8fe1d510` publishes the AMS provider packet.
JPET/ASPET run `pdf-jpet-missing7-reharvest-0dd85b6` recovered 0/7 `good_pdf`;
six rows returned invalid PDF-like content and one stayed `missing_pdf_harvest`
after an HTML/no-record capture, with 0 timeout and 0 `taxicab_error`. Oxjobs
commit `ae72a1ff` publishes the JPET/ASPET provider packet.
OnePetro run `pdf-onepetro-missing7-reharvest-92f581e` recovered 0/7
`good_pdf`; all rows stayed `missing_pdf_harvest` after HTML
abstract/proceedings or no-record captures, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `029f9ac9` publishes the OnePetro provider
packet.
Mary Ann Liebert run `pdf-liebertpub-missing7-reharvest-b5e1678` recovered
0/7 `good_pdf`; five rows stayed missing after Sage-hosted HTML/no-record
captures and two rows returned invalid PDF-like content, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `c9eafb75` publishes the Liebert provider
packet.
AACR Figshare run `pdf-aacr-figshare-missing6-reharvest-8f674aa` recovered
0/6 `good_pdf`; all rows stayed missing after status-201 HTML/no durable PDF
captures from Figshare downloader/PDF routes, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `dd7ab56d` publishes the AACR Figshare
provider packet.
AMPP run `pdf-ampp-missing6-reharvest-851bd3f` recovered 0/6 `good_pdf`; all
six `content.ampp.org` rows returned invalid PDF-like content and classified as
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`ef843caa` publishes the AMPP queue, scrubbed report, and provider packet.
Healio run `pdf-healio-missing6-reharvest-51c7ad1` recovered 0/6 `good_pdf`;
all six `journals.healio.com/doi/epdf` rows returned invalid PDF-like content
and classified as `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `64517b97` publishes the Healio queue,
scrubbed report, and provider packet.
Sage Knowledge run `pdf-sage-knowledge-missing10-reharvest-bef0376` recovered
0/10 `good_pdf`; all ten `sk.sagepub.com` download PDF rows returned invalid
PDF-like content and classified as `corrupt_or_truncated_pdf`, with 0 timeout
and 0 `taxicab_error`. Oxjobs commit `79af39d8` publishes the Sage Knowledge
queue, scrubbed report, and provider packet.
IGI Global run `pdf-igi-global-missing6-reharvest-14746e2` recovered 1/6
`good_pdf`; read-only confirmation `pdf-igi-global-missing6-readonly-14746e2`
preserved the same durable PDF and left five rows missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `471f9ee3` publishes the IGI queue, scrubbed
reports, and residual provider packet. Next independent lane is UC Press
(`online.ucpress.edu`) from the latest full gate.
Current latest pushed Taxicab branch commit before this handoff-doc update is
`51c7ad1`.

## Repository

- Use `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- Use `main` only for verified deployable state. Use `codex/taxicab-pdf-phase2` for PDF Phase 2 once the HTML Phase 1 main-sync commit is pushed.
- Preserve unrelated local changes.
- Read `NEXT_TO_DO.md` before choosing a cluster. It is the handoff contract for Codex/Claude continuity.

## Production Safety

- Pushing `main` deploys to ECS through `.github/workflows/aws.yml`.
- Eval harness, tests, docs, and reports are safe setup work.
- Production scraping behavior changes need targeted eval plus no-regression proof before push.
- Do not import `app.py` from eval code or tests; it creates R2 clients at import time.
- Commit and push frequently after focused checks. The required loop is:
  `git status --short`, scoped changes, focused tests, `git add`, `git commit`,
  `git pull --rebase`, `git push`.

## Providers

- Zyte is the production core.
- Browserbase is evidence/recoverability/gold-sample collection unless explicitly promoted later.
- Confirmed Zyte gaps should become reproducible support packets with DOI, URL, category, evidence snippet, and Browserbase comparison when available.

## Secrets

- Never print or commit secret values.
- Load local ignored `.env` / `.env.aws` first for provider, R2, Zyte, and AWS CLI-style variables. Do not ask Shubh to re-auth unless those files are missing or a safe AWS command proves the local session is expired.
- AWS CLI may be used for discovery, but do not echo decrypted Secrets Manager or SSM values.
- Secret variable names can appear in docs and `.env.example`; raw values cannot.

## Verification

Run these before committing eval-system changes:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
rg -n "ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY" .
```

The broad scan above intentionally finds variable names in docs and code.
Inspect matches and reject raw values, tokens, cookies, or signed provider URLs.

For live read-only smoke:

```bash
python3 scripts/taxicab_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --smoke \
  --out /tmp/taxicab-live-smoke
```

For a limited baseline:

```bash
python3 scripts/taxicab_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --limit 100 \
  --out eval_runs/
```

For PDF Phase 2:

```bash
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke
python3 scripts/taxicab_pdf_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --smoke \
  --out /tmp/taxicab-pdf-live-smoke
python3 scripts/taxicab_pdf_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --out pdf_eval_runs/ \
  --workers 8
python3 scripts/taxicab_pdf_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv \
  --limit 1 \
  --with-browserbase \
  --browserbase-mode session \
  --browserbase-timeout 60 \
  --out /tmp/taxicab-pdf-browserbase-springer \
  --run-id pdf-browserbase-springer-1
python3 scripts/taxicab_pdf_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-100.csv \
  --out pdf_eval_runs/ \
  --run-id pdf-elsevier-missing-readonly-previewfix-9b7d84b \
  --workers 4 \
  --row-timeout 120 \
  --timeout 60 \
  --retries 1 \
  --progress-every 10
```

For explicit low-concurrency reharvest samples, bound each row with
`--row-timeout` so a pathological Taxicab/Zyte request records `timeout`
instead of holding the whole run open:

```bash
python3 scripts/taxicab_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --corpus /tmp/sample.csv \
  --reharvest \
  --workers 2 \
  --timeout 20 \
  --retries 1 \
  --row-timeout 60 \
  --out /tmp/taxicab-reharvest-watchdog
```

For Browserbase evidence mode, the harness uses Browserbase REST plus Playwright. The local Browserbase Python SDK is intentionally not required because SDK import hung in this environment.

```bash
python3 -m playwright --version
python3 scripts/taxicab_eval.py --with-browserbase --browserbase-mode session ...
```

Current Browserbase state: Browserbase REST session create/release is healthy. Local Playwright startup now passes, and the expanded 10-row MDPI Browserbase session run completed under `--row-timeout 150`.

## Reporting

- oxjobs control surface: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`.
- PDF Phase 2 uses oxjobs #461 `taxicab-pdf` with its own report surface at `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf`.
- Keep Taxicab retrieval KPIs separate from Parseland extraction KPIs.
- Keep HTML and PDF Taxicab KPIs separate. Report `good_html_rate` for #133 and `good_pdf_rate` for the new PDF job.
