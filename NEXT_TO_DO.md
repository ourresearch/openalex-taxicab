# Taxicab next work for Codex and Claude

Last updated: 2026-06-14 PDT.

This file is the handoff contract for Taxicab retrieval-quality work. Read it
before doing new work. Keep it current before ending a long session. For the
current goal, `GOAL.md` is the concise control file and this file is the
expanded operational context.

## Current goal

```text
HTML Phase 1: complete, target hit at 9,583/10,000 good_html (95.83%).
Current gate: J-STAGE partial-positive provider lane is recorded and confirmed; University of Chicago journals bounded sample or provider-guidance test is next.
PDF Phase 2: active on codex/taxicab-pdf-phase2, target >=95% good_pdf.
PDF denominator: pdf_expected_total from the 10K Goldie/OpenAlex corpus, with all-10K context reported separately.
Next exact command: cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab && jq -r -s '(["DOI","Link","PDF URL","publisher","host","baseline_category","baseline_run_id"]), ([.[] | select(.category=="missing_pdf_harvest") | select((.candidate_url//"")|test("https?://([^/]+\\.)?journals\\.uchicago\\.edu";"i"))][0:25][] | [.doi, ("https://doi.org/" + .doi), .candidate_url, (.publisher//"unknown"), "journals.uchicago.edu", .category, .run_id]) | @csv' pdf_eval_runs/pdf-full10k-after-karger-ca8b132/rows.ndjson > /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/uchicago-missing-25.csv
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

The accepted full 10K gate after Karger is complete:
`pdf-full10k-after-karger-ca8b132`, 1,890/6,293 `good_pdf` (30.03%),
+53 rows versus the denominator baseline and +3 versus the prior gate, 3,863
`missing_pdf_harvest`, 395 `corrupt_or_truncated_pdf`, 102 `encrypted_or_unreadable_pdf`, 11
`html_instead_of_pdf`, 11 `js_redirect_unresolved`, 11
`supplement_or_preview_pdf`, 8 `interstitial_or_paywall`, 2 `bot_block_403`,
0 timeout, and 0 `taxicab_error`. There were 0 good-to-non-good regressions;
14 non-good rows moved from missing to corrupt/truncated. Oxjobs commit
`5ccb3df5 #461 taxicab-pdf: publish karger full gate` records the accepted report.

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

Current next lane: send/test Zyte guidance for ScienceDirect, Lancet, Cell,
Wiley, De Gruyter, Lippincott, Oxford, CUP/Cambridge, SSRN, RSC, AIP, Taylor API
chapter-download, ACS, SPIE, Thieme, Sage, Brill, AMA/JAMA, APS, ACM, BMJ,
Karger, Optica, JSTOR, Inlibra, Scientific.net, Persee, Nature, and J-STAGE
PDF-byte or click/download fetches before production route code. If continuing
independent technical work, choose University of Chicago journals from the latest full gate or test provider
guidance for accumulated packets. IOP is accepted as the first repeated
whole-corpus PDF KPI lift; Karger is the latest accepted lift, and the gap to
95% remains 4,089 rows.

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
rg -n "(ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY)=[^[:space:]]+" .
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
cd /Users/shubh-trips/Documents/OpenAlex/oxjobs
git pull --rebase origin main
python3 scripts/publish-report.py 461
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

### 10. ASME browserHtml route

Complete and accepted. Do not redo ASME unless new ASME residual rows appear in the current queue.

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
