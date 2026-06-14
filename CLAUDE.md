# OpenAlex Taxicab

Academic content harvesting API. Fetches HTML and PDFs from publisher websites via Zyte API, stores in Cloudflare R2 + DynamoDB.

Current goal state: HTML retrieval Phase 1 is complete at 9,583/10,000
`good_html` (95.83%). PDF retrieval Phase 2 is active and targets >=95%
`good_pdf` on the PDF-expected subset of the 10K Goldie corpus. Use
`GOAL.md` as the current control file and update it before long handoffs.
Latest PDF measurement gate: accepted full 10K read-only gate
`pdf-full10k-after-karger-ca8b132` is 1,890/6,293 `good_pdf` (30.03%),
+53 rows versus the denominator baseline of 1,837/6,293 (29.19%) and +3 rows
versus the prior accepted gate, with `missing_pdf_harvest` down from 3,939 to
3,863, 0 good-to-non-good regressions, 0 timeout, and 0 Taxicab API errors.
The gap to 95% is now 4,089 rows.
Gated PDF reharvest mode is pushed at `8193c47`; the first committed smoke
recovered 0/5. The Springer seed queue from oxjobs #461 recovered 1/12
(`10.1007/bf03544238`) and left 11 missing. Reharvest post-context
instrumentation is pushed at `b9d5918`; the rerun shows the 11 remaining
Springer misses were POST 201 HTML captures, not PDF records. A no-storage
two-step Zyte probe also returned HTML for a failed sample, so prepare/support
packet evidence before changing production routing.
PDF Browserbase evidence mode is pushed at `f424129`: it annotates non-good PDF rows
separately from the Taxicab verdict. The first Springer Browserbase session
smoke returned `html_not_pdf`, not a recoverable PDF.
PDF row-timeout watchdog is pushed at `be2f5c7`. Use `--row-timeout` before
scaling reharvest samples. The resumed Elsevier true-missing sample finished
with 4/25 `good_pdf`, 15 `missing_pdf_harvest`, 6 `corrupt_or_truncated_pdf`,
0 timeout, and 0 Taxicab errors. Treat this as localized sample evidence until
full 10K gate proof. Read-only confirmation
`pdf-elsevier-missing-readonly-after-reharvest-be2f5c7` preserved the same four
`good_pdf` rows and left 21 rows missing, with 0 timeout and 0 Taxicab errors.
The 100-row Elsevier run exposed an eval bug: a ScienceDirect `first-page-pdf`
preview was counted as `good_pdf`. Current branch code classifies first-page or
preview PDF URLs as `supplement_or_preview_pdf`. Corrected Elsevier 100-row
read-only result: 7/100 `good_pdf`, 92 missing, one preview, 0 timeout, and
0 Taxicab errors. Oxjobs #461 published this gate at commit `3d8a5fa0`.
Do not scale blind Elsevier reharvest from this result; split
ScienceDirect/Lancet/Cell/direct-asset/router rows into route/support clusters.
Oxjobs commit `825c2e2d` adds that sanitized split. Next lane: no-storage
ScienceDirect route probes and scrubbed Zyte examples before any production
PDF route change.
Taxicab commit `741e9a7` adds the no-storage ScienceDirect probe. Run
`sciencedirect-route-probe-3-741e9a7` recovered 0/3 PDFs across 12 route
variants. Oxjobs commit `666d0ed6` records the scrubbed probe and Zyte packet;
next step is Zyte support or a Zyte-advised PDF-byte fetch mode.
Lancet run `lancet-route-probe-3-741e9a7` recovered 0/3 PDFs, with two 520
ban-free failures and one 404 HTML page. Oxjobs commit `2105c8f1` records the
Lancet probe and packet `lancet-pdf-ban-741e9a7.md`.
Cell Press run `cell-route-probe-3-741e9a7` recovered 0/3 PDFs, with login/JS
HTML instead of PDF bytes. Oxjobs commit `a160ec1a` records the Cell probe and
packet `cell-pdf-login-js-741e9a7.md`.
Browserbase run `pdf-browserbase-cell-1-3de630f` also returned `html_not_pdf`
for one Cell candidate. Browserbase did not recover a direct PDF; the raw
artifacts stay local because the final URL included a Cloudflare challenge
token. Oxjobs commit `d0344d1d` records only the scrubbed public summary
`evidence/browserbase/cell-pdf-html-not-pdf-3de630f.json`.
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
packet.
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
`pdf-asme-missing15-reharvest-c1c2b86` recovered 0/15 `good_pdf`; eight rows
returned invalid PDF-like content and seven stayed `missing_pdf_harvest` after
status-201 HTML/no durable PDF captures, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `10d80d80` publishes the ASME provider packet. Cairn run
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
reports, and residual provider packet.
UC Press run `pdf-ucpress-missing6-reharvest-dd1a528` recovered 0/6
`good_pdf`; all six `online.ucpress.edu` article-PDF rows returned invalid
PDF-like content and classified as `corrupt_or_truncated_pdf`, with 0 timeout
and 0 `taxicab_error`. Oxjobs commit `e435bc5e` publishes the UC Press queue,
scrubbed report, and provider packet.
RUPress run `pdf-rupress-missing6-reharvest-76fb88d` recovered 1/6
`good_pdf`; read-only confirmation `pdf-rupress-missing6-readonly-76fb88d`
preserved the same durable PDF and left four rows missing plus one
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`fa847b5a` publishes the RUPress queue, scrubbed reports, and residual provider
packet.
Emerald run `pdf-emerald-missing6-reharvest-e3fdbea` recovered 0/6 `good_pdf`;
all six `www.emerald.com` article-PDF rows returned invalid PDF-like content
and classified as `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `f191f0eb` publishes the Emerald queue,
scrubbed report, and provider packet.
JACC run `pdf-jacc-missing6-reharvest-9e16fb8` recovered 0/6 `good_pdf`; all
six `www.jacc.org/doi/epdf` routes stored HTML with no durable PDF records and
classified as `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `eea013bf` publishes the JACC queue, scrubbed report, and
provider packet.
AJO run `pdf-ajo-missing6-reharvest-a30f12a` recovered 0/6 `good_pdf`; five
`www.ajo.com/article/.../pdf` rows returned invalid PDF content and one stayed
missing, with 0 timeout and 0 `taxicab_error`. Oxjobs commit `a72d7c09`
publishes the AJO queue, scrubbed report, and provider packet.
BioOne run `pdf-bioone-missing5-reharvest-1d9e18f` recovered 0/5 `good_pdf`;
all five `bioone.org` PDF rows stayed missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `b60d7147` publishes the BioOne queue,
scrubbed report, and provider packet.
Canadian Science Publishing run `pdf-cdnsciencepub-missing5-reharvest-2a121b2`
recovered 0/5 `good_pdf`; three `cdnsciencepub.com` explicit PDF rows returned
invalid PDF content and two stayed missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `634173b9` publishes the Canadian Science
queue, scrubbed report, and provider packet.
Edward Elgar run `pdf-elgaronline-missing5-reharvest-8244033` recovered 1/5
`good_pdf`; read-only confirmation `pdf-elgaronline-missing5-readonly-8244033`
preserved the same durable PDF and left four rows missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `9771940c` publishes the Edward Elgar queue,
scrubbed reports, and residual provider packet.
American Concrete Institute run `pdf-concrete-missing5-reharvest-d38b219`
recovered 0/5 `good_pdf`; all `www.concrete.org` getarticle rows resolved to
portal detail or secured sign-in HTML and stayed missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `9fbae749` publishes the ACI queue, scrubbed
report, and provider packet.
American Journal of Surgery run
`pdf-americanjournalofsurgery-missing5-reharvest-93479bd` recovered 0/5
`good_pdf`; three article PDF rows returned invalid PDF content and two stayed
missing, with 0 timeout and 0 `taxicab_error`. Oxjobs commit `1b4912ec`
publishes the AJS queue, scrubbed report, and provider packet.
AJOG run `pdf-ajog-missing5-reharvest-831503a` recovered 1/5 `good_pdf`;
read-only confirmation `pdf-ajog-missing5-readonly-831503a` preserved the same
durable PDF and left four rows missing, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `2e492500` publishes the AJOG queue, scrubbed reports, and
provider packet.
Scholarly Publishing Collective run
`pdf-scholarlypublishingcollective-missing5-reharvest-a9fdacb` recovered 0/5
`good_pdf`; four article-PDF routes returned invalid PDF content and one row
resolved to article abstract HTML/no durable PDF record, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `362d2b2f` publishes the Scholarly queue,
scrubbed report, and provider packet.
Royal Society Publishing run
`pdf-royalsocietypublishing-missing5-reharvest-1d0fac0` recovered 0/5
`good_pdf`; three rows redirected to Silverchair watermark PDF URLs and two
resolved to article abstract HTML/no durable PDF record, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `cfeb6d34` publishes the Royal Society queue,
scrubbed report, and provider packet.
KoreaScience run `pdf-koreascience-missing5-reharvest-35d3541` recovered 0/5
`good_pdf`; all five explicit `koreascience.or.kr:80/article/*.pdf` routes
timed out under the row watchdog, with 0 `taxicab_error`. Oxjobs commit
`53c6d7fe` publishes the KoreaScience queue, scrubbed report, and provider
packet.
Journal of Pharmaceutical Sciences run `pdf-jpharmsci-missing5-reharvest-3b7bf15`
recovered 0/5 `good_pdf`; all five `/article/.../pdf` routes resolved to
`/article/.../abstract` HTML and produced no durable PDF record, with
0 timeout and 0 `taxicab_error`. Oxjobs commit `c1f26ec8` publishes the J Pharm
Sci queue, scrubbed report, and provider packet.
CHEST run `pdf-chestnet-missing5-reharvest-4c6cd17` recovered 1/5 `good_pdf`;
read-only confirmation `pdf-chestnet-missing5-readonly-4c6cd17` preserved the
same durable PDF and left four rows missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `ee27cd5e` publishes the CHEST queue, scrubbed
reports, and provider packet.
Green Journal run `pdf-thegreenjournal-missing4-reharvest-a211471` recovered
0/4 `good_pdf`; all four rows stayed `missing_pdf_harvest` after explicit
`thegreenjournal.com` PDF/action routes resolved to article abstract HTML or no
durable PDF record, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`0e0bb05f` publishes the Green Journal queue, scrubbed report, and provider
packet.
SciELO run `pdf-scielo-missing4-reharvest-7d2c782` recovered 2/4 `good_pdf`;
read-only confirmation `pdf-scielo-missing4-readonly-7d2c782` preserved the
same two durable PDFs and left two rows missing, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `41a903e6` publishes the SciELO queue,
scrubbed reports, and provider packet.
AIP `pubs.aip.org` run `pdf-pubs-aip-missing25-reharvest-751ad63` recovered
0/25 `good_pdf`; all rows stayed `missing_pdf_harvest` after status-201
HTML/no-record captures, split between 20 article-abstract fallbacks and 5
signed Silverchair PDF redirects. Oxjobs commit `b7940463` publishes the AIP
platform queue, scrubbed report, and provider packet.
DOI-router run `pdf-doi-org-missing19-reharvest-659e13e` recovered
0/19 `good_pdf`; 17 rows stayed `missing_pdf_harvest`, 2 timed out, and 0
rows hit `taxicab_error`. Oxjobs commit `4c711418` publishes the DOI-router
queue, scrubbed report, and provider packet. Next independent lane is
ScienceDirect direct asset run
`pdf-sciencedirectassets-missing6-reharvest-16bcb5a`, which recovered
0/6 `good_pdf`; all rows stayed `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `58ab0e73` publishes the ScienceDirect asset
queue, scrubbed report, and provider packet. Next high-volume lane is Springer
run `pdf-springer-link-missing25-reharvest-d401917`, which recovered
0/25 `good_pdf`; all rows stayed `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `469a996b` publishes the Springer queue,
scrubbed report, and provider packet.
De Gruyter Brill residual run
`pdf-degruyterbrill-missing25-reharvest-f2c5e99` recovered 0/25 `good_pdf`;
all rows stayed `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `ddb8a16f` publishes the residual queue, scrubbed report, and
provider packet.
AIAA tail run `pdf-aiaa-missing4-reharvest-2faaaa2` recovered 0/4 `good_pdf`;
two rows stayed `missing_pdf_harvest` and two returned
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`83c0b0fe` publishes the AIAA queue, scrubbed report, and provider packet.
Neurology tail run `pdf-neurology-missing4-reharvest-42dc6f4` recovered 0/4
`good_pdf`; three rows stayed `missing_pdf_harvest` and one returned
`corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`d9ede76b` publishes the Neurology queue, scrubbed report, and provider packet.
Next tail lane is Begell House on `www.dl.begellhouse.com` from the latest full
gate.
Current latest pushed Taxicab branch commit before this handoff-doc update is
`42dc6f4`.

## Agent Operating Rules

- Active repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- `main` auto-deploys to ECS through `.github/workflows/aws.yml`. Work on a `codex/` branch and push only after focused verification.
- For PDF Phase 2, use `codex/taxicab-pdf-phase2` after the HTML Phase 1 main-sync commit is on `main`.
- Never print or commit secret values. Secret names may appear in docs, but raw values for `ZYTE_API_KEY`, `BROWSERBASE_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `R2_SECRET_ACCESS_KEY`, and `CRAWLERA_KEY` must stay out of tracked files and reports.
- Use the local ignored credential files before asking Shubh to authenticate. `.env` contains Taxicab provider/R2/Zyte material, and `.env.aws` contains AWS CLI-style session variables. Load them into process environment without echoing values; ask for auth only if the files are missing or a safe command proves the session is expired.
- Zyte remains the production retrieval core. Browserbase is evidence/recoverability unless a later, separately tested production fallback is approved.
- Taxicab V1 reporting lives in `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit` (#133). #336 is Parseland-only.
- PDF Phase 2 gets a separate auto-ID oxjob named `taxicab-pdf`; do not mix PDF KPIs into #133's HTML target.
- Evaluation code must not import `app.py`; Flask app import requires R2 credentials at import time.
- Before continuing the improvement loop, read `NEXT_TO_DO.md` in this repo and in oxjobs `working/taxicab-audit/NEXT_TO_DO.md`.
- Commit and push frequently after focused checks: `git status --short`, tests,
  `git add`, `git commit`, `git pull --rebase`, `git push`.

## Taxicab V1 Eval Commands

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
python3 scripts/taxicab_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --out /tmp/taxicab-live-smoke
python3 scripts/taxicab_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out eval_runs/
```

For live reharvest samples, prefer a per-row watchdog:

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

Optional Browserbase evidence mode uses Browserbase REST plus Playwright. The local Browserbase Python SDK is no longer required for `scripts/taxicab_eval.py` because SDK import hung in this environment.

```bash
python3 -m playwright --version
python3 scripts/taxicab_eval.py --with-browserbase --browserbase-mode session ...
```

Known current Browserbase state: REST session create/release works with the ignored Parseland eval env key. Local Playwright startup now passes, and the expanded 10-row MDPI Browserbase session run completed under `--row-timeout 150`. See `NEXT_TO_DO.md` before spending more Browserbase time.

Before push, run a secret scan:

```bash
rg -n "ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY" .
```

Inspect matches before committing; variable names are OK, secret values and signed provider URLs are not.

## Taxicab PDF Phase 2 Eval Commands

```bash
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --out /tmp/taxicab-pdf-live-smoke
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --out pdf_eval_runs/ --workers 8
```

PDF Phase 2 reports live in oxjobs #461 at `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf`.

## Project Structure

- `app.py` - Flask REST API endpoints
- `openalex_taxicab/harvest.py` - Core harvesting logic, soft-block detection, S3/DynamoDB storage
- `openalex_taxicab/http_cache.py` - HTTP requests via Zyte API, DOI resolution, publisher-specific handling
- `openalex_taxicab/eval_harness.py` - Taxicab V1 retrieval-quality classifier and artifact writer
- `openalex_taxicab/pdf_eval_harness.py` - Taxicab PDF retrieval-quality classifier and artifact writer
- `openalex_taxicab/publisher_index.py` - DOI-prefix/domain publisher classifier, vendored from Parseland
- `openalex_taxicab/util.py` - Utility functions (MIME type detection, timing)
- `scripts/taxicab_eval.py` - Read-only/reharvest eval CLI
- `scripts/taxicab_pdf_eval.py` - Read-only PDF eval CLI

## Testing Locally

Uses `.venv` and `.env` (no `python-dotenv` installed, load env vars manually).

### Test a URL fetch + soft-block check

```bash
.venv/bin/python -c "
import os
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip()

from openalex_taxicab.http_cache import http_get
from openalex_taxicab.harvest import Harvester
import re

url = 'http://dx.doi.org/10.1088/0256-307x/40/10/100401'
response = http_get(url)
print('Status code:', response.status_code)
print('Resolved URL:', response.url)

content = response.content if isinstance(response.content, str) else response.content.decode('utf-8', 'ignore')
print('Content length:', len(content))

h = Harvester.__new__(Harvester)
is_soft_block = h._check_soft_block(content.encode('utf-8') if isinstance(content, str) else content)
print('Is soft block:', is_soft_block)

title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
if title_match:
    print('Page title:', title_match.group(1).strip())
"
```

### Test DOI redirect resolution only

```bash
.venv/bin/python -c "
import os
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip()

from openalex_taxicab.http_cache import resolve_doi_redirects

result = resolve_doi_redirects('https://doi.org/10.1088/0256-307x/40/10/100401')
print('Final URL:', result['final_url'])
print('Chain:', ' -> '.join(result['redirect_chain']))
"
```

## Key Concepts

- **BROWSER_HTML_URLS**: Domains requiring Zyte browser rendering (`browserHtml=True` + `javascript=True`). Add domains here when a publisher uses JS-based bot protection.
- **BOT_PROTECTION_DOMAINS**: Known bot protection services (e.g. `perfdrive.com`). DOI redirect resolution walks back the chain if it lands on one of these.
- **Soft blocks**: Pages that return HTTP 200 but contain captcha/verification content. Detected by pattern matching in `Harvester._check_soft_block()`.
- **Publisher-specific handling**: Some publishers need special Zyte params (cookies, JS actions, waitForSelector). See `http_get()` and `call_with_zyte_api()` in `http_cache.py`.
