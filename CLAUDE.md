# OpenAlex Taxicab

<!-- TAXICAB_PDF_CURRENT_HANDOFF_START -->
## Current PDF Handoff: 2026-06-17 Vestnik Rosnou Provider-Negative Evidence

Accepted strict full 10K PDF gate `pdf-full10k-after-vetsci-41ddbad`
is `2,394/6,293 good_pdf` (`38.04%`), up `+1` versus Visnykj and `+557`
versus the denominator baseline of `1,837/6,293` (`29.19%`). The 95% target is
`5,979/6,293`, so the current gap is `3,585` rows.

Vetsci remains the latest accepted KPI lift. Vestnik Rosnou /
`vestnik-rosnou.ru` was the next fresh low-volume lane after that gate;
no-storage provider probe `unknown-vestnikrosnou-current-provider-probe1-30f248f`
recovered `0/1 good_pdf`, with all strategies ending as `download_404`.
Vestnik Rosnou is now prior provider/Zyte or gold-sample evidence, not a fresh
route-promotion lane.

Residual queue after vestnik-rosnou demotion: top 240 subclusters are all
`provider_lane_do_not_duplicate`; full 1,415-subcluster export has `1,051`
provider-lane/do-not-duplicate, `325` one-row `probe_next`, `20`
validator/provider, `8` Browserbase/Zyte-gold-first, and `11` inspect-first
subclusters. First non-provider lane is a validator-confirmation
`corrupt_or_truncated_pdf` singleton. Next exact low-volume fresh probe, if
continuing singleton probes:

```bash
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
python3 scripts/provider_pdf_probe.py \
  --input pdf_eval_runs/pdf-full10k-after-vetsci-41ddbad/rows.ndjson \
  --category missing_pdf_harvest \
  --publisher unknown \
  --host vektornm.ru \
  --limit 1 \
  --strategies all \
  --out /tmp/taxicab-pdf-probes \
  --run-id unknown-vektornm-current-provider-probe1-<commit> \
  --timeout 60
```

If prioritizing larger expected recovery, stop singleton probing and move
Envoy-Zyte to provider-advised recipes/support packets for the large
do-not-duplicate lanes.

For bounded reharvest DOI-file runs, use a real `/tmp/*.csv` path. Do not use
process substitution for CSV input because `/dev/fd/...` has no `.csv` suffix
and the harness treats it as plain DOI text. Keep raw row-level artifacts
local/ignored. Public oxjobs #461 artifacts must be aggregate or scrubbed.
Browserbase remains evidence/gold only; Zyte remains the production provider
core. Any lower OSTI/PLOS, JPS, Tellus, JTH, JID, zurnalai, UP Poznan,
wulixb, worldwidejournals, wmpllc, visnykj, virtus, or vetsci metric blocks are
historical; this block is the current handoff.
<!-- TAXICAB_PDF_CURRENT_HANDOFF_END -->
Academic content harvesting API. Fetches HTML and PDFs from publisher websites via Zyte API, stores in Cloudflare R2 + DynamoDB.

Current goal state: HTML retrieval Phase 1 is complete at 9,583/10,000
`good_html` (95.83%). PDF retrieval Phase 2 is active and targets >=95%
`good_pdf` on the PDF-expected subset of the 10K Goldie corpus. Use
`GOAL.md` as the current control file and update it before long handoffs.
Latest PDF measurement gate: accepted strict full 10K read-only gate
`pdf-full10k-after-visnykj-68b5ebb` is 2,393/6,293 `good_pdf`
(38.03%), +1 row versus Worldwidejournals and +556 rows versus the denominator baseline
of 1,837/6,293 (29.19%). The run has 3,781 `missing_pdf_harvest`, 65
`corrupt_or_truncated_pdf`, 4 `encrypted_or_unreadable_pdf`, 23
`supplement_or_preview_pdf`, 4 `interstitial_or_paywall`, 0 timeout, and 0
`taxicab_error`. The gap to 95% is 3,586 rows. This is a bounded
Visnykj direct-PDF cache/reharvest lift, not a Taxicab-main
production scraping push.

Latest #461 report publish: oxjobs commit `1d3a2a2f9` records wmpllc
provider-negative evidence; the next publish should record the accepted
visnykj gate. Prior `37af671ac` publishes the worldwidejournals accepted gate,
refreshed graph, scrubbed aggregate evidence, and wmpllc/visnykj handoff. Older
provider-support snapshot entries remain historical context, including
`working/taxicab-pdf/evidence/zyte-support/pdf-provider-lanes-after-osti-plos-ee9001b.md`.
Prior `5a1254630` publishes the closed DOI.org residual-priority cleanup and refreshed residual queue; prior
`3c125878f` publishes the Elsevier DOI.org residual-priority correction; prior
`77d71e78f` publishes the AMS negative provider/gold evidence and AMS-demoted
residual priority-map refresh; prior `386f5fa73` publishes the ASM/JVI mixed provider evidence and residual
priority-map refresh; prior `d054e3d`
publishes the AAP residual priority-map refresh; prior `1cba3fc` publishes the AAP Pediatrics
provider/gold check, `01be98e` publishes the Transcript Verlag
preview-provider confirmation, `10ec3eeb` publishes the unknown-attribution
DOI.org numeric JS-redirect gold check, `03560e2a` publishes the
unknown-attribution DOI.org JS-redirect duo gold check, `1727a6ac` publishes the
BCSJ/Oxford Academic DOI.org JS-redirect gold check, `5c29deb5` publishes the
AAAS Science.org gold check, `0e59e67f` publishes the PeerJ branch evidence, and
`4984229f` made the PDF report graph-first and minimalist. The current accepted
metric is `pdf-full10k-after-osti-plos-ee9001b`: 2,385/6,293 `good_pdf`
(37.90%), +2 rows versus Atlantis, +548 rows versus denominator baseline, and a
3,594-row gap to 95%. The AHA/Lippincott one-row lane
`www.ahajournals.org:/doi/pdf/:doi/:id` recovered 0/1 through Zyte no-storage
provider probing and 0/1 through Browserbase gold evidence; Browserbase reached
a 403 challenge and ended `download_started_not_captured`. No Taxicab
POST/R2/DynamoDB writes occurred, no route code was written, and no production
behavior changed. The Elsevier DOI.org current recheck
`elsevier-doi-browserbase-gold5-5d5d0fc` sampled five current
Elsevier-attributed DOI.org candidate rows and recovered 0/5 through
Browserbase; verdicts were four `download_started_not_captured` and one
`html_not_pdf`. Earlier oxjobs commit `74a062c6` remains the aggregate-only
Wiley PDF-direct validator/provider Zyte recheck from Taxicab commit `9b01df6`;
that recheck recovered 0/10 current `corrupt_or_truncated_pdf` rows. ACS, ACM,
Wiley PDF-direct, IOP article-PDF, bioRxiv PDF path families, Elsevier DOI.org,
and the AHA/Lippincott lane are not promotion candidates without a
narrower/provider-advised recipe. Top-240 `probe_next` remains 0 and
`confirm_existing_branch_candidate` remains 0. Published artifacts are
aggregate-only; raw rows stay local.

Latest local validations: OSTI/PLOS query-preserving provider-probe recovery is
complete at Taxicab branch commit `ee9001b`; Atlantis Press is complete at
Taxicab commit `3b13642`; prior-evidence mapping is complete through the closed
DOI.org residual-priority cleanup at Taxicab commit `1d50d45`; oxjobs #461
latest publish is `91eafaf82`; latest support snapshot content commit is
`92420e70b`; latest support snapshot asset commit is `e96ba4bfd`; latest
Taxicab branch tooling commit is `d761c59` for private provider-ticket packets;
provider recipe probe support now includes network-capture PDF decoding at
`56d2c2c`.
Browserbase PDF
evidence mode remains fixed at
Taxicab commit `bdcc38a` to survive download-start navigation errors and
capture started/not-captured download evidence. `BROWSERBASE_API_KEY` exists in
ignored `/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/.env`;
`BROWSERBASE_PROJECT_ID` is optional for the current REST session path. The
ACS, ACM, Wiley, IOP, bioRxiv, and Elsevier DOI.org demotion/gold-first
refreshes supersede the older residual lane queue; do not duplicate those route
families unless testing a provider-advised recipe.
Earlier validations remain: supplement validator recovered +70 at full-gate
scale; DOI.org/OSTI recovered +2 at full-gate scale; SAGE landing-page rewrite
regressed preservation rows; Wiley, ACS, and Elsevier DOI.org residual probes
do not currently justify promotion. Published artifacts are aggregate-only;
local `rows.ndjson` files contain row-level evidence.

Latest provider-recipe probe: `springer-network-capture-probe3b-56d2c2c`
tested the official Zyte browser `networkCapture` shape as a no-storage recipe
against 3 Springer `link.springer.com/content/pdf` rows. It recovered 0/3
`good_pdf`: two rows returned target-site 429 rate-limit errors and one row
returned HTML with an unresolved JS redirect. This is provider/support evidence
only, not a Taxicab route-code candidate. Follow-up
`degruyter-network-capture-probe3-d178c76` tested a broader `pdf` network
capture token against 3 De Gruyter Brill `/document/doi/.../pdf` rows and
recovered 0/3; every row returned 405 text/html captcha evidence. This is also
provider/support evidence only. The private ignored-local Zyte ticket packet
was regenerated after these probes with
`python3 scripts/build_pdf_provider_ticket.py --run-id zyte-provider-ticket-after-osti-plos-ee9001b --top-lanes 25 --samples-per-lane 3`;
keep the raw packet out of git and oxjobs.
Next no-storage probe `lippincott-network-capture-probe3-84b519f` recovered
0/3 from current `journals.lww.com` rows: two unresolved JS redirects and one
403 bot block. This also stays in provider/support; do not write Lippincott
route code from it.
Follow-up `oxford-network-capture-probe3-bea12c4` tested the same broad `pdf`
network-capture token against 3 current Oxford Academic `academic.oup.com`
rows and recovered 0/3 `good_pdf`: two rows were PDF-viewer/html shells despite
`application/pdf` content type, and one row returned a 403 bot block. This also
stays in provider/support; do not write Oxford route code from it.
Follow-up `ssrn-network-capture-probe3-03cffc3` tested the same broad `pdf`
network-capture token against 3 current SSRN `papers.ssrn.com` rows and
recovered 0/3 `good_pdf`: all three rows returned 200 `image/svg+xml` payloads
classified as `corrupt_or_truncated_pdf`, not PDF bytes. Keep SSRN in
provider/support; do not write SSRN route code from it.
Follow-up `aip-pubs-network-capture-probe3-next` tested 3 current AIP
Publishing `pubs.aip.org` rows with the same network-capture recipe and
recovered 0/3 `good_pdf`: two rows returned 403 bot blocks and one row returned
a PDF-viewer/html shell. Keep AIP in provider/support; do not write AIP route
code from it.
Follow-up `jstor-network-capture-probe3-next` tested 3 current JSTOR
`jstor.org` rows with the same network-capture recipe and recovered 0/3
`good_pdf`: every row returned 200 `text/html` article/book page content, not
PDF bytes. Keep JSTOR in provider/support; do not write JSTOR route code from
it.
Follow-up `brill-network-capture-probe3-next` tested 3 current Brill
`brill.com` rows with the same network-capture recipe and recovered 0/3
`good_pdf`: every row returned 405 `text/html` human-verification content. Keep
Brill in provider/support; do not write Brill route code from it.
Follow-up `springer-network-wait-capture-probe3-c767a1d` tested a
docs-derived browser `networkCapture` recipe with a short `waitForTimeout`
against 3 current Springer `link.springer.com` rows and recovered 0/3
`good_pdf`: one tiny JSON body classified as corrupt/truncated, one unresolved
JS/router-like HTML page, and one interstitial/paywall HTML page. Keep Springer
in provider/support; a blind browser wait before capture is not enough evidence
for Taxicab route code.

Current NetworkCapture sweep is 0/24 across Springer, De Gruyter Brill,
Lippincott, Oxford Academic, SSRN, AIP Publishing, JSTOR, and Brill; the
Springer wait-capture variant makes the follow-through 0/27 sampled rows. The
private ignored-local Zyte packet is
`pdf_eval_runs/zyte-provider-ticket-networkcapture-0of24-1001461/`. A local
residual refresh `residual-refresh-after-networkcapture-0of24-1001461` found
top-240 priority bands are all `provider_lane_do_not_duplicate`, so the next
action is Zyte-supported provider guidance, not another route guess.

Next action: if Zyte provides a PDF-byte recipe, save it as an ignored local
JSON file and run a no-storage probe with
`python3 scripts/provider_pdf_probe.py --input pdf_eval_runs/pdf-full10k-after-osti-plos-ee9001b/rows.ndjson --category missing_pdf_harvest --publisher <publisher> --host <host> --limit 3 --recipe-file <ignored-recipe.json> --strategies <strategy_name> --out /tmp/taxicab-pdf-probes --run-id <provider>-zyte-advised-probe3`.
Use
`working/taxicab-pdf/evidence/zyte-support/pdf-provider-lanes-after-osti-plos-ee9001b.md`
as the aggregate provider-support handoff, then test any provider-advised
PDF-byte recipe through no-storage probes before route code. The probe harness
accepts provider recipes with
`python3 scripts/provider_pdf_probe.py --recipe-file <ignored-recipe.json> --strategies <recipe_name> ...`;
recipe runs must stay no-storage and must not call `/taxicab` POST. The OSTI/PLOS
Build a private ignored-local Zyte ticket packet when row-level examples are
needed with
`python3 scripts/build_pdf_provider_ticket.py --run-id zyte-provider-ticket-after-osti-plos-ee9001b --top-lanes 25 --samples-per-lane 3`.
The latest local packet is under
`pdf_eval_runs/zyte-provider-ticket-after-osti-plos-ee9001b/`; do not commit or
copy the raw packet into oxjobs because it contains DOI-level examples.
The OSTI/PLOS
gold-first rows are already recovered and closed by
`pdf-full10k-after-osti-plos-ee9001b`; residual refresh
`residual-clusters-after-osti-plos-ee9001b` has top-240 all
provider-lane/do-not-duplicate. Closed DOI.org and branch-only residuals were
demoted by `residual-clusters-after-closed-doi-demote-1d50d45`; Elsevier DOI.org
missing-PDF residuals are correctly demoted as prior negative provider/gold
evidence instead of re-entering the generic DOI resolver gold queue. AMS is
closed as negative
provider/gold evidence: Zyte no-storage
recovered 0/1 with four 520 empty responses, and Browserbase recovered 0/1
with `html_not_pdf`; this is not route-code evidence. ASM/JVI is mixed
provider evidence and not a route candidate; AAP
Pediatrics is closed as negative provider/gold evidence;
AHA/Lippincott and Elsevier DOI.org lanes are closed as negative evidence for
current purposes. PeerJ branch commit `bf1632f` adds a narrow
`peerj.com/articles/*.pdf` PDF-byte strategy; branch replay recovered 1/1
current PeerJ `html_instead_of_pdf` residual, preserved 1/1 already-good PeerJ
row with 0 regressions, and did not recover the remaining PeerJ
`missing_pdf_harvest` row. Oxjobs #461 commit `0e59e67f` publishes the
aggregate-only PeerJ evidence. This is branch evidence only, not an accepted
KPI lift or Taxicab main push. The current branch-candidate queue is otherwise
exhausted. AAAS Science.org gold check at Taxicab branch commit `53d3704`
recovered 0/1 through Zyte and 0/1 through Browserbase; Browserbase ended
`html_not_pdf` on `www.science.org`, and oxjobs #461 commit `5c29deb5`
publishes the aggregate-only evidence. BCSJ/Oxford Academic gold check at
Taxicab branch commit `897c742` recovered 0/1 through Zyte and 0/1 through
Browserbase; Browserbase ended `html_not_pdf` on `academic.oup.com`, and
oxjobs #461 commit `1727a6ac` publishes the aggregate-only evidence.
Unknown-attribution DOI.org JS-redirect duo gold check at Taxicab branch commit
`a25417e` recovered 0/2 through Zyte and 0/2 through Browserbase; Browserbase
ended `html_not_pdf` on aggregate PNAS and University of Chicago hosts, and
oxjobs #461 commit `03560e2a` publishes the aggregate-only evidence.
Unknown-attribution DOI.org numeric JS-redirect gold check at Taxicab branch
commit `d4ed55b` recovered 0/1 through Zyte and 0/1 through Browserbase;
Browserbase ended `html_not_pdf` on aggregate Mediasphera host evidence, and
oxjobs #461 commit `10ec3eeb` publishes the aggregate-only public summary at
`working/taxicab-pdf/evidence/report461-unknown-doiorg-numeric-jsredirect-gold-summary-d4ed55b.json`.
Transcript Verlag preview-provider confirmation at Taxicab branch commit
`1587acb` recovered 0/4 current `supplement_or_preview_pdf` rows through Zyte;
PDF-byte strategies stayed `supplement_or_preview_pdf`, browser HTML returned
`html_instead_of_pdf`, and oxjobs #461 commit `01be98e` publishes the
aggregate-only public summary at
`working/taxicab-pdf/evidence/report461-transcript-preview-provider-probe4-summary-1587acb.json`.
AAP Pediatrics provider/gold check at Taxicab branch commit `9399eb7` recovered
0/1 through Zyte and 0/1 through Browserbase; direct PDF-byte strategies stayed
`js_redirect_unresolved`, Zyte browser HTML reached `interstitial_or_paywall`,
and Browserbase ended `html_not_pdf` on aggregate AAP article-abstract host
evidence. Oxjobs #461 commit `1cba3fc` publishes the aggregate-only public
summary at
`working/taxicab-pdf/evidence/report461-aappediatrics-htmlpdf-gold-summary-9399eb7.json`.
Local residual refresh `residual-clusters-after-elsevier-doi-demote-2f627f4`
moves the 15-row Elsevier DOI.org missing-PDF lane to do-not-duplicate, after
AMS, mixed ASM/JVI evidence, plus prior validator/gold lanes were already
closed where appropriate; top-240 subcluster-entry priority bands are 217
provider-lane/do-not-duplicate, 19 Browserbase/Zyte-gold-first, and 4
validator/provider. Oxjobs #461 commit `3c125878f` publishes the aggregate-only
Elsevier DOI.org residual-priority correction and refreshed queue.
Local residual refresh `residual-clusters-after-closed-doi-demote-1d50d45`
demotes closed publisher DOI.org, unknown DOI.org, validator/provider, and
PeerJ branch-only lanes; oxjobs #461 commit `5a1254630` publishes the
aggregate-only cleanup. OSTI/PLOS then recovered at Taxicab commit `ee9001b`;
residual refresh `residual-clusters-after-osti-plos-ee9001b` has top-240 all
provider-lane/do-not-duplicate.
Browserbase can be used for evidence/gold
collection from the ignored Parseland eval env, but must not overwrite the
Taxicab baseline verdict. Keep Browserbase as evidence/gold only, Zyte as the
production core, and do not push Taxicab main before the full PDF 95% proof.
AWS CLI/default `.env.aws` session credentials are currently expired; AWS is
not required for the immediate no-storage Zyte/Browserbase evidence loop.

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

Historical detail below is chronological and may use "current" relative to the
older gate being discussed. The top block above is the authoritative handoff.
Current read-only refresh `pdf-full10k-publisher-attribution-e584811` at
Taxicab commit `8a35869` is 2,196/6,293 `good_pdf` (34.90%), with
3,805 `missing_pdf_harvest`, 65 `corrupt_or_truncated_pdf`, 0 timeout,
0 `taxicab_error`, and a 3,783-row gap to 95%. Treat the +3 current read-only
movement as cache/read-only drift plus attribution refresh, not production
scraping-code lift. Oxjobs #461 commit `ebe97f4d` publishes this full-gate
refresh and its sanitized report asset.
Current Springer no-storage provider probe
`springer-current-missing-provider-probe10-8a35869` at Taxicab commit
`8585a77` recovered 0/10 current missing rows; best categories were five
`interstitial_or_paywall` and five `js_redirect_unresolved`. Keep Springer in
the Zyte/provider PDF-byte lane. Oxjobs #461 commit `84760121` publishes the
probe summary/report and updates the combined Zyte packet.
Current Wiley no-storage provider probe
`wiley-current-missing-provider-probe10-8585a77` at Taxicab commit `fa95e59`
recovered 0/10 current missing rows; best categories were nine
`js_redirect_unresolved` and one `bot_block_403`. All 40 strategy attempts
stayed HTML, empty, or blocked. Keep current Wiley missing-PDF rows in the
Zyte/provider PDF-byte lane; do not broaden Wiley route rewrites from this
evidence. Oxjobs #461 commit `3480ae82` publishes the scrubbed probe summary,
report asset, and combined Zyte packet update.
Current Elsevier no-storage provider probe
`elsevier-current-missing-provider-probe10-fa95e59` at Taxicab commit
`8abd909` recovered 0/10 current missing rows; best categories were seven
`js_redirect_unresolved`, two `html_instead_of_pdf`, and one `empty_response`.
The sample spans Elsevier platform hosts plus attribution-noise hosts, so keep
Elsevier in the provider/Zyte lane and split clusters before route code.
Oxjobs #461 commit `68c2eb46` publishes the scrubbed probe summary/report and
combined Zyte packet update.
Current De Gruyter no-storage provider probe
`degruyter-current-missing-provider-probe10-eb75f5e` at Taxicab commit
`eb75f5e` recovered 0/10 current missing rows; best categories were eight
`js_redirect_unresolved` and two `bot_block_403`. Browser HTML hit captcha for
all 10 rows, while `accept_pdf` and `google_referer` returned empty bodies for
all 10 rows. Keep De Gruyter in the provider/Zyte PDF-byte lane; do not add
route code from this evidence. Oxjobs #461 commit `b04396d6` publishes the
scrubbed probe summary/report and combined Zyte packet update.
Current Lippincott no-storage provider probe
`lippincott-current-missing-provider-probe10-eb75f5e` at Taxicab commit
`4689af7` recovered 0/10 current missing rows; all 40 strategy attempts were
`download_404` against LWW `PageNotFound.aspx` HTML. Keep Lippincott in the
candidate-discovery plus provider/Zyte PDF-byte lane. Oxjobs #461 commit
`40cf1b9e` publishes the scrubbed probe summary/report and combined Zyte packet
update.
Current Oxford no-storage provider probe
`oxford-current-missing-provider-probe10-4689af7` at Taxicab commit `67187dc`
recovered 1/10 current missing rows; residual best categories were five
`bot_block_403`, three `html_instead_of_pdf`, and one `js_redirect_unresolved`.
Oxjobs #461 commit `d4b6da1b` publishes the scrubbed summary/report and
combined Zyte packet update. This is partial provider-strategy evidence, not a
production route-code candidate yet.
Current CUP/Cambridge no-storage provider probe
`cup-current-missing-provider-probe10-67187dc` at Taxicab commit `41a9df8`
recovered 0/10 current missing rows; all 40 strategy attempts were
`js_redirect_unresolved`. Oxjobs #461 commit `38844dea` publishes the scrubbed
summary/report and combined Zyte packet update. This is provider/Zyte PDF-byte
and JavaScript/access-flow evidence, not a route-code candidate.
Current Taylor no-storage provider probe
`taylor-current-missing-provider-probe10-70f8f8a` at Taxicab commit `70f8f8a`
recovered 0/10 current missing rows; best categories were six `download_404`,
three `interstitial_or_paywall`, and one `empty_response`. Oxjobs #461 commit
`af13892d` publishes the scrubbed summary/report and combined Zyte packet
update. This is current residual candidate-discovery/provider evidence, not a
route-code candidate, and stays separate from the earlier accepted Taylor +5
direct TandF PDF lift.
Current SSRN no-storage provider probe
`ssrn-current-missing-provider-probe10-863d7aa` at Taxicab commit `863d7aa`
recovered 0/10 current missing rows; every best category was
`js_redirect_unresolved`. `accept_pdf` and Google-referer variants returned
empty responses for all rows, while browser HTML and default-body variants
stayed on unresolved SSRN JavaScript delivery. Oxjobs #461 commit `2c171c7e`
publishes the scrubbed summary/report and combined Zyte packet update. This is
provider/click-download evidence, not a Taxicab route-code candidate.
Current JSTOR no-storage provider probe
`jstor-current-missing-provider-probe10-fe0d018` at Taxicab commit `fe0d018`
recovered 0/10 current missing rows; every best category was
`html_instead_of_pdf`. `default_body`, `accept_pdf`, and `google_referer`
returned HTML for all rows, while browser HTML returned eight HTML rows and two
interstitial/paywall rows. Oxjobs #461 commit `463bb712` publishes the
scrubbed summary/report and combined Zyte packet update. This is provider
PDF-byte evidence, not a Taxicab route-code candidate.
Current AIP Publishing no-storage provider probe
`aip-publishing-current-missing-provider-probe10-af746d4` at Taxicab commit
`af746d4` recovered 0/10 current missing rows; best categories were six
`js_redirect_unresolved`, three `interstitial_or_paywall`, and one
`html_instead_of_pdf`. Oxjobs #461 commit `14f254ac` publishes the scrubbed
summary/report and combined Zyte packet update. This is provider/access-flow
evidence, not a Taxicab route-code candidate.
Current RSC no-storage provider probe
`rsc-current-missing-provider-probe10-f709792` at Taxicab commit `f709792`
recovered 1/10 current missing rows through `google_referer`; residual best
categories were eight `js_redirect_unresolved` and one `html_instead_of_pdf`,
with browser HTML also hitting six `bot_block_403` rows. Larger confirmation
`rsc-current-missing-provider-probe25-05b1a38` at Taxicab commit `05b1a38`
recovered 0/25; best categories were 24 `js_redirect_unresolved` and one
`html_instead_of_pdf`. Oxjobs #461 commit `84f1c8ea` publishes the result.
Keep RSC in the Zyte/provider support lane before route code unless a
Zyte-advised recipe changes the result.
Current ACS no-storage provider probe
`acs-current-missing-provider-probe10-7e4b5e5` at Taxicab commit `7e4b5e5`
recovered 0/10 current missing rows; every DOI's best category was
`js_redirect_unresolved`. PDF-accept and Google-referer each had one
`empty_response`, and browser HTML hit one `bot_block_403` row. Oxjobs #461
commit `21a7697c` publishes the scrubbed summary/report and combined Zyte
packet update. Keep ACS in the provider/Zyte PDF-byte and JS/access-flow lane
before route code.
Current Brill no-storage provider probe
`brill-current-missing-provider-probe10-88bc77f` at Taxicab commit `88bc77f`
recovered 0/10 current missing rows; every DOI's best category was
`bot_block_403`, and all 40 strategy attempts returned `bot_block_403`. Oxjobs
#461 commit `e2bac29b` publishes the scrubbed summary/report and combined Zyte
packet update. Keep Brill in the provider/Zyte bot-block and PDF-byte support
lane before route code.
Current Thieme no-storage provider probe
`thieme-current-missing-provider-probe10-3f45c6a` at Taxicab commit `3f45c6a`
recovered 0/10 current missing rows; every DOI's best category was
`js_redirect_unresolved`, and all 40 strategy attempts returned
`js_redirect_unresolved`. Oxjobs #461 commit `4838bd1c` publishes the scrubbed
summary/report and combined Zyte packet update. Keep Thieme in the
provider/Zyte PDF-byte and JS/access-flow lane before route code.
Current SPIE no-storage provider probe
`spie-current-missing-provider-probe10-9fa4596` at Taxicab commit `9fa4596`
recovered 0/10 current missing rows; every DOI's best category was
`js_redirect_unresolved`, and all 40 strategy attempts returned
`js_redirect_unresolved`. Oxjobs #461 commit `fe048cca` publishes the scrubbed
summary/report and combined Zyte packet update. Keep SPIE in the provider/Zyte
PDF-byte and JS/access-flow lane before route code.
Current BMJ no-storage provider probe
`bmj-current-missing-provider-probe10-9ccfeaf` at Taxicab commit `9ccfeaf`
recovered 2/10 current missing rows; residual best categories were six
`bot_block_403` and two `interstitial_or_paywall`. `default_body` recovered
both PDFs, while PDF-accept and Google-referer each recovered one. Oxjobs #461
commit `6de28ec3` publishes the scrubbed summary/report and combined Zyte
packet update. Larger confirmation `bmj-current-missing-provider-probe25-622512f`
at Taxicab commit `622512f` recovered only 1/25; residuals were 15
`bot_block_403`, five `interstitial_or_paywall`, three
`js_redirect_unresolved`, and one `html_instead_of_pdf`. Oxjobs #461 commit
`e5b648f6` publishes the result. Keep BMJ in the Zyte/provider support lane
before route code unless a Zyte-advised recipe changes the result.
Current Sage no-storage provider probe
`sage-current-missing-provider-probe10-1f57c9b` at Taxicab commit `1f57c9b`
recovered 0/10 current missing rows; best categories were six `bot_block_403`
and four `js_redirect_unresolved`, and every strategy stayed blocked, empty,
or unresolved. Oxjobs #461 commit `d059488d` publishes the scrubbed
summary/report and combined Zyte packet update. Keep Sage in the provider/Zyte
bot-block and JS/access-flow support lane before route code.
Current AMA/JAMA no-storage provider probe
`ama-current-missing-provider-probe10-2198bc2` at Taxicab commit `2198bc2`
recovered 0/10 current AMA/JAMA-attributed missing rows; best categories were
five `interstitial_or_paywall`, four `js_redirect_unresolved`, and one
`bot_block_403`. PDF-byte strategies mostly returned empty bodies while
browser HTML returned article/paywall pages. Oxjobs #461 commit `eddf9c5a`
publishes the scrubbed summary/report and combined Zyte packet update. Keep
AMA/JAMA in the provider/Zyte PDF-byte, access-flow, and bot-block support lane
before route code.
Current Karger no-storage provider probe
`karger-current-missing-provider-probe10-4427b24` at Taxicab commit `4427b24`
recovered 0/10 current Karger missing rows; every DOI's best category was
`html_instead_of_pdf`. Default-body returned interstitial/paywall HTML for all
10 rows, PDF-accept mostly returned empty bodies, and browser HTML returned
large article HTML pages instead of PDF bytes. Oxjobs #461 commit `69b2780a`
publishes the scrubbed summary/report and combined Zyte packet update. Keep
Karger residuals in the provider/Zyte PDF-byte and access-flow support lane
before route code.
Current APS no-storage provider probe
`aps-current-missing-provider-probe10-cf3d845` at Taxicab commit `cf3d845`
recovered 1/10 current APS missing rows through `google_referer`
(`10.1103/4gbr-6kbs`); the other nine best categories were
`js_redirect_unresolved`. Larger confirmation
`aps-current-missing-provider-probe25-576c058` at Taxicab commit `576c058`
found 24 current APS rows and recovered 0/24; best categories were 22
`js_redirect_unresolved` and two `html_instead_of_pdf`. Oxjobs #461 commit
`5435e2c7` publishes the larger confirmation. Keep APS in the Zyte/provider
support lane before route code unless a Zyte-advised recipe changes the result.
Current ACM no-storage provider probe
`acm-current-missing-provider-probe10-dba7e2f` at Taxicab commit `dba7e2f`
first recovered 1/10 current ACM missing rows through `default_body` and
`google_referer`. Larger confirmation
`acm-current-missing-provider-probe25-26f35ea` at Taxicab commit `26f35ea`
found all 22 current ACM rows and recovered 6/22: three `default_body` and
three `google_referer` good PDFs. Residual best categories were 12
`html_instead_of_pdf`, three `js_redirect_unresolved`, and one
`empty_response`. Oxjobs #461 commit `88b3d53f` publishes the larger
confirmation. ACM is now a narrow PDF-byte route-strategy candidate; residual
536-byte PDF-labeled HTML shells remain provider/Zyte support evidence.
Implementation candidate: current branch routes only `dl.acm.org/doi/pdf/...` URLs through Zyte PDF-byte strategies (`default_body`, `accept_pdf`, then `google_referer`) with explicit request timeouts. It does not route ACM `/doi/epdf/` or `/action/showFmPdf` paths. Local no-storage branch `http_get` validation `acm-http-get-local-route-precommit-1950532` returned 5/22 classifier `good_pdf`; 4/22 were clean candidate-URL DOI matches and one was a candidate DOI mismatch (`10.1145/507678.507679` row pointed to `10.1145/507670.507679`). Residual categories were nine `html_instead_of_pdf`, six `empty_response`, and two `js_redirect_unresolved`. No Taxicab POST/R2/DynamoDB writes. Oxjobs #461 commit `695fb51d` publishes this route-validation evidence.
Current Optica no-storage provider probe
`optica-current-missing-provider-probe10-1b0823d` at Taxicab commit `1b0823d`
recovered 0/10 current Optica missing rows. Best categories were eight
`js_redirect_unresolved` and two `html_instead_of_pdf`; default body,
PDF-accept, and Google-referer all stayed unresolved JS, while browser HTML
returned two HTML rows and eight interstitial/paywall rows. Oxjobs #461 commit
`f57bad44` publishes the scrubbed summary/report and combined Zyte packet
update. Keep Optica in the provider/Zyte PDF-byte and access-flow lane before
route code.
Current IOP no-storage provider probe
`iop-current-missing-provider-probe10-8aaf717` at Taxicab commit `8aaf717`
recovered 6/10 current IOP missing rows as `good_pdf`. Valid PDFs came from
`iopscience.iop.org/article/.../pdf` routes using `default_body`, `accept_pdf`,
or `google_referer`; residual best categories were two `bot_block_403` rows and
two `interstitial_or_paywall` book-chapter rows. Oxjobs #461 commit `bd7396fb`
publishes the scrubbed summary/report and combined Zyte packet update.
All-current IOP confirmation
`iop-current-missing-provider-probe25-ad609f7` at Taxicab commit `ad609f7`
covered all 18 current refreshed IOP missing rows and recovered 9/18 as
`good_pdf`. Residual best categories were six `bot_block_403`, two
`interstitial_or_paywall`, and one `html_instead_of_pdf`. Valid PDFs again came
from `iopscience.iop.org/article/.../pdf` routes, mostly through `default_body`
with some `accept_pdf` wins. Oxjobs #461 commit `51b4665a` publishes the
scrubbed summary/report and combined Zyte packet update. This confirms a narrow
branch-only IOP article-PDF route candidate; do not broaden to IOP book/chapter
PDF paths because those hit interstitial/paywall rows.
Implementation candidate: Taxicab commit `07c8f95` routes only
`iopscience.iop.org/article/.../pdf` URLs through Zyte PDF-byte strategies
(`default_body`, `accept_pdf`, then `google_referer`) with explicit request
timeouts. It does not route IOP book/chapter PDF paths. Verification passed:
`python3 -m unittest discover -s tests` ran 97 tests, PDF fixture smoke passed,
and local no-storage branch `http_get` validation
`iop-http-get-local-route-precommit` returned 11/16 `good_pdf` and five
`bot_block_403` residuals, with no Taxicab POST/R2/DynamoDB writes. Oxjobs
#461 commit `c3c9b0ac` publishes the scrubbed route-validation summary/report.
Latest focused evidence: no-storage run
`wiley-residual-corrupt-provider-probe-19-a61d34b` recovered 15/19 current
residual Wiley corrupt rows as `good_pdf`. The four residuals are two
`empty_response`, one `bot_block_403`, and one `supplement_or_preview_pdf`.
Default-body and PDF-Accept each won six rows; Google-referer won three rows;
browser HTML returned HTML shells/JS, so it is not the PDF-byte path here.
Oxjobs #461 commit `6ba84787` publishes this evidence. This is strategy
evidence only; next implement a narrow Wiley PDF-byte strategy candidate and
prove it with bounded reharvest/read-only confirmation before any full-gate
claim.
Implementation candidate: Taxicab commit `3b2d218` routes Wiley
`/doi/pdfdirect/` URLs through Zyte HTTP body strategies (`default_body`,
`accept_pdf`, then `google_referer`) instead of browser HTML/cookie-shell
capture. Tests passed with full `python3 -m unittest discover -s tests` and
PDF fixture smoke. A local no-storage `http_get` measurement over the 19
current residual Wiley rows returned 13/19 `good_pdf`; this is not a production
gate because the branch is not deployed to Taxicab main.
Oxjobs #461 commit `d4f99eee` publishes this candidate evidence. Confirmation
path decision: remote `--reharvest` exercises deployed Taxicab main, not this
branch; local branch `Harvester` with real env credentials can write production
R2/DynamoDB, so do not use it as a silent branch-confirmation path. Continue
with no-storage branch evidence until a full 95% PDF proof is ready for main.
Oxjobs #461 commit `c15cd194` publishes the branch-confirmation decision,
follow-up route probes, and the corrected ScienceDirect current-missing probe.
Latest no-storage probes: Wiley `/doi/pdf/` as-is recovered 0/10; rewriting
that same sample to `/doi/pdfdirect/` recovered only 2/10, including one
DOI-mismatch PDF; Springer `link.springer.com/content/pdf/` recovered 0/10;
ScienceDirect current missing recovered 0/10 after Taxicab commit `69553ae`
normalized provider-probe host filters. Treat these as provider/support
evidence, not production route-code candidates.
Oxjobs #461 commit `d8e62ef8` refreshes the combined Zyte PDF-byte support
packet with these current ScienceDirect, Wiley, and Springer follow-up probes.
Current attribution slice: publisher classification now considers source
`PDF URL` fields and provider-probe CSV queues classify publishers from
candidate PDF URLs when an explicit publisher is absent. On the accepted
structured-parser full-gate rows this reduces `missing_pdf_harvest`
`publisher=unknown` from 966 to 642 rows, moving 324 rows into interpretable
publisher/platform buckets. This is measurement/triage lift only; it does not
change production scraping behavior or the accepted `good_pdf` KPI. Oxjobs #461
commit `8b1d1b2f` publishes the report slice and evidence JSON; oxjobs #461
commit `ebe97f4d` publishes the follow-up full-gate refresh; oxjobs #461 commit
`84760121` publishes the current Springer provider probe; oxjobs #461 commit
`3480ae82` publishes the current Wiley provider probe; oxjobs #461 commit
`68c2eb46` publishes the current Elsevier provider probe; oxjobs #461 commit
`b04396d6` publishes the current De Gruyter provider probe; oxjobs #461 commit
`40cf1b9e` publishes the current Lippincott provider probe; oxjobs #461 commit
`d4b6da1b` publishes the current Oxford provider probe; oxjobs #461 commit
`38844dea` publishes the current CUP/Cambridge provider probe; oxjobs #461
commit `af13892d` publishes the current Taylor provider probe; oxjobs #461
commit `2c171c7e` publishes the current SSRN provider probe; oxjobs #461
commit `463bb712` publishes the current JSTOR provider probe; oxjobs #461
commit `14f254ac` publishes the current AIP Publishing provider probe; oxjobs
#461 commit `e3621c28` publishes the current RSC provider probe; oxjobs #461
commit `21a7697c` publishes the current ACS provider probe; oxjobs #461 commit `e2bac29b` publishes the current Brill provider probe; oxjobs #461 commit `4838bd1c` publishes the current Thieme provider probe; oxjobs #461 commit `fe048cca` publishes the current SPIE provider probe; oxjobs #461 commit `6de28ec3` publishes the current BMJ provider probe; oxjobs #461 commit `d059488d` publishes the current Sage provider probe; oxjobs #461 commit `eddf9c5a` publishes the current AMA/JAMA provider probe; oxjobs #461 commit `69b2780a` publishes the current Karger provider probe; oxjobs #461 commit `5da73adb` publishes the current APS provider probe; oxjobs #461 commit `88c2fddb` publishes the current ACM provider probe; oxjobs #461 commit `f57bad44` publishes the current Optica provider probe; oxjobs #461 commit `bd7396fb` publishes the current IOP provider probe; oxjobs #461 commit `51b4665a` publishes the all-current IOP confirmation; oxjobs #461 commit `c3c9b0ac` publishes the IOP route validation; oxjobs #461 commit `695fb51d` publishes the ACM route validation; oxjobs #461 commit `5abc1635` publishes the Nature residual and Oxford larger current probe evidence; oxjobs #461 commit `dc4438dc` publishes the unknown direct-PDF recovery evidence and sanitizes old signed URL fields from the #461 hardness set; oxjobs #461 commit `bbf1da67` publishes the AJOL unknown-tail recovery and residual tail probe evidence; oxjobs #461 commit `d9455b42` publishes the current unknown-provider refresh; oxjobs #461 commit `eacb1a53` publishes the accepted unknown-refresh full gate; oxjobs #461 commit `2092c008` publishes the readable-encrypted full gate.
Latest current-provider confirmations: Nature residual no-storage run `nature-current-missing-provider-probe25-7189521` found 15 residual Nature rows and recovered 0/15; residual best categories were 11 `interstitial_or_paywall` and four `js_redirect_unresolved`. Oxford larger no-storage run `oxford-current-missing-provider-probe25-7189521` recovered 1/25, but the only recovery was a `sciengine.com` candidate; the `academic.oup.com` subset recovered 0/23 with 15 bot blocks, four HTML rows, three interstitial/paywall rows, and one 404. Do not promote Nature or OUP route code from these runs; keep both in provider/Zyte support.
Latest bounded direct-PDF recovery: unknown-publisher current-provider probes at Taxicab `2244ccc` found recoverable direct PDFs in small clusters. IJISRT recovered 3/3, ISCA recovered 2/2, Microbiology Research recovered 1/3, and Diabetes Journals recovered 0/3. Bounded production-write reharvest `pdf-unknown-ijisrt-isca-reharvest5-2244ccc` recovered 5/5 across IJISRT and ISCA, and read-only confirmation `pdf-unknown-ijisrt-isca-readonly5-2244ccc` preserved 5/5 `good_pdf`. Treat this as durable bounded cache lift until a later accepted full-10K gate confirms corpus-level movement.
Latest accepted full-gate confirmation published to oxjobs #461: Taxicab run
`pdf-full10k-after-readable-encrypted-f2da963` at commit `f2da963` accepted
2,304/6,293 `good_pdf` (36.61%), +99 versus the prior accepted full gate, with
3,796 missing, 4 encrypted/unreadable, 0 timeout, and 0 `taxicab_error`. Treat
this as measurement/validator lift, not Taxicab-main production-code deployment.
Oxjobs #461 commit `2092c008` publishes the safe summary/report; the next lane
is residual clustering from this gate, not another report publication.
Current tooling slice: generic no-storage provider probing is implemented in
`scripts/provider_pdf_probe.py` with tests in `tests/test_provider_pdf_probe.py`.
It does not call Taxicab POST and does not write R2/DynamoDB. It sanitizes URLs
before artifacts and classifies probe responses through the existing PDF
harness. Provider probe summaries choose the best non-good category per DOI and
host filters normalize `www.` prefixes; this is measurement/reporting-only, not
production scraping behavior. IOP residual
probe `iop-corrupt-provider-probe-3-31663bc` recovered
0/3 PDFs: one PerfDrive/captcha block and two corrupt application/pdf responses
with no page objects. Oxjobs #461 commit `27d5e414` publishes the scrubbed
summary and report. J-STAGE corrupt-provider probe
`jstage-corrupt-provider-probe-3b-31663bc` recovered 0/3 residual corrupt PDFs:
two application/pdf responses still had no page objects and one row timed out
empty; browser HTML returned PDF-viewer shells. Oxjobs #461 commit `416b6fec`
publishes the scrubbed J-STAGE corrupt summary/report. J-STAGE encrypted probe
`jstage-encrypted-provider-probe-3-31663bc` also recovered 0/3: default body
reached application/pdf bytes for all rows but each stayed
`encrypted_or_unreadable_pdf`; browser HTML returned the same 174-byte shells.
Oxjobs #461 commit `a1073dd4` publishes the scrubbed encrypted summary/report.
J-STAGE missing probe `jstage-missing-provider-probe-3-31663bc` recovered 0/3:
two rows stayed JS redirects and one row timed out empty/browser-shell. Oxjobs
#461 commit `e9a4458a` publishes the scrubbed missing summary/report. Use these
probes plus the structured-parser gate to test current residual subtypes before production scraping changes.
Next exact command:
`cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab && python3 - <<'PY'`
`import csv`
`from pathlib import Path`
`with Path("pdf_eval_runs/residual-clusters.csv").open(newline="", encoding="utf-8") as f:`
`    for row in list(csv.DictReader(f))[:20]:`
`        print(f"{row['rank']}\t{row['category']}\t{row['publisher']}\t{row['host']}\t{row['count']}\t{row['recommended_agent']}\t{row['evidence_strength']}")`
`PY`
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
Oxjobs commit `5cca142e` records the remaining-IOP full-gate impact:
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
Begell House tail run `pdf-begellhouse-missing4-reharvest-db7d5fc` recovered
0/4 `good_pdf`; all four rows stayed `missing_pdf_harvest` after status-201
HTML/no-record captures, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`36ba508f` publishes the Begell queue, scrubbed report, and provider packet.
MIT Press Direct tail run `pdf-direct-mit-missing4-reharvest-8643285`
recovered 0/4 `good_pdf`; all four rows returned invalid PDF content and
classified as `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `9fdca746` publishes the MIT Direct queue,
scrubbed report, and provider packet. RSNA tail run
`pdf-rsna-missing4-reharvest-987d362` recovered 0/4 `good_pdf`; all four rows
returned invalid PDF content and classified as `corrupt_or_truncated_pdf`, with
0 timeout and 0 `taxicab_error`. Oxjobs commit `67a5b554` publishes the RSNA
queue, scrubbed report, and provider packet. Gold Journal tail run
`pdf-goldjournal-missing4-reharvest-91c0c88` recovered 0/4 `good_pdf`; two
rows stayed missing after status-201 HTML abstract captures and two returned
invalid PDF content, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`8d1c57b4` publishes the Gold Journal queue, scrubbed report, and provider
packet. Next tail lane is ATS Journals on `www.atsjournals.org` from the latest
full gate. ATS Journals tail run
`pdf-atsjournals-missing4-reharvest-a618e5a` recovered 0/4 `good_pdf`; all
four rows stayed missing after status-201 HTML captures resolving to
`academic.oup.com/atsjournals`, with 0 timeout and 0 `taxicab_error`. Oxjobs
commit `7e4dcc79` publishes the ATS Journals queue, scrubbed report, and
provider packet. Next tail lane is Transcript Verlag on
`www.transcript-verlag.de` from the latest full gate. Transcript Verlag
corrected run `pdf-transcript-verlag-missing4-readonly-previewfix-43ab357`
accepted 0/4 `good_pdf`; all four stored PDFs are
`supplement_or_preview_pdf` because the candidate URLs match
`chunk_prev/prev_*.pdf`. Oxjobs commit `433d621e` publishes the corrected
summary, scrubbed report, and preview-candidate note. PNAS tail run
`pdf-pnas-missing4-reharvest-3d943cf` recovered 0/4 `good_pdf`; all four rows
classified as `corrupt_or_truncated_pdf`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `8ff5fd14` publishes the PNAS queue, scrubbed
report, and provider packet. Next tail lane is Peter Lang on
`www.peterlang.com` from the latest full gate. Peter Lang tail run
`pdf-peterlang-missing4-reharvest-eb523da` recovered 0/4 `good_pdf`; all four
rows stayed `missing_pdf_harvest` after status-201 HTML captures resolving to
`www.peterlang.com/document/...`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `a12417e1` publishes the Peter Lang queue, scrubbed report, and
provider packet. Next tail lane is Nomos eLibrary on
`www.nomos-elibrary.de` from the latest full gate. Nomos eLibrary tail run
`pdf-nomos-elibrary-missing4-reharvest-b4bbab0` recovered 0/4 `good_pdf`; all
four rows stayed `missing_pdf_harvest` after status-201 HTML captures resolving
to `www.inlibra.com/de/document/view/detail/uuid/...`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `d7d1220d` publishes the Nomos queue, scrubbed
report, and provider packet. Journal of Pediatric Surgery tail run
`pdf-jpedsurg-missing4-reharvest-66bf4f1` recovered 0/4 `good_pdf`; all four
rows stayed `missing_pdf_harvest` after status-201 HTML captures resolving to
`www.jpedsurg.org/article/.../abstract`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit `d6c52a5b` publishes the JPedsurg queue,
scrubbed report, and provider packet. JBC tail run
`pdf-jbc-missing4-reharvest-83f5456` recovered 0/4 `good_pdf`; all four rows
stayed `missing_pdf_harvest` after status-201 HTML captures resolving to
`www.jbc.org/article/.../fulltext`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `c5a71e38` publishes the JBC queue, scrubbed report, and
provider packet. ADS tail run `pdf-adsabs-missing4-reharvest-1b03675`
recovered 4/4 `good_pdf`; read-only confirmation
`pdf-adsabs-missing4-readonly-1b03675` preserved the same 4/4 durable records
at `articles.adsabs.harvard.edu`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `34c32f5f` publishes the ADS queue, summaries, and reports. This
does not change accepted full-10K KPI history until a full read-only gate
confirms corpus-level lift. NCTM tail run
`pdf-nctm-missing4-reharvest-97bcaa1` recovered 1/4 `good_pdf`; read-only
confirmation `pdf-nctm-missing4-readonly-97bcaa1` preserved the same 1/4
durable record, with 3 missing rows, 0 timeout, and 0 `taxicab_error`. The
three residual NCTM `downloadpdf/journals` routes stored XML article HTML and
produced no durable PDF record. Oxjobs commit
`877d1107 #461 taxicab-pdf: add nctm recovery` publishes the queue, summaries,
reports, provider packet, and next AAAHQ queue. This does not change accepted
full-10K KPI history until a full read-only gate confirms corpus-level lift.
AAAHQ tail run `pdf-aaahq-missing4-reharvest-7f47ce9` recovered 0/4
`good_pdf`; three rows returned invalid PDF content and one stored article
abstract HTML. Read-only confirmation `pdf-aaahq-missing4-readonly-7f47ce9`
returned all four rows to `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`63789cfc #461 taxicab-pdf: add aaahq tail packet` publishes the queue,
summaries, reports, provider packet, and next EJSO queue. EJSO tail run
`pdf-ejso-missing4-reharvest-30ce1b5` recovered 0/4 `good_pdf`; all four
candidate `/pdf` routes resolved to article `/abstract` HTML and read-only
confirmation `pdf-ejso-missing4-readonly-30ce1b5` returned all four rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`fc590d0f #461 taxicab-pdf: add ejso tail packet` publishes the queue,
summaries, reports, provider packet, and next AUA Journals queue. AUA Journals
tail run `pdf-auajournals-missing4-reharvest-465c495` recovered 0/4
`good_pdf`; all four candidate PDF/EPDF routes resolved to article DOI HTML
and read-only confirmation `pdf-auajournals-missing4-readonly-465c495`
returned all four rows to `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`16f51e88 #461 taxicab-pdf: add auajournals tail packet` publishes the queue,
summaries, reports, provider packet, and next Springer Publishing queue.
Springer Publishing tail run `pdf-springerpub-missing3-reharvest-3720861`
recovered 0/3 `good_pdf`; all three candidate PDF routes resolved to
article/book/chapter HTML and read-only confirmation
`pdf-springerpub-missing3-readonly-3720861` returned all three rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`d56b9fac #461 taxicab-pdf: add springerpub tail packet` publishes the queue,
summaries, reports, provider packet, and next Vestnik/KRSU queue. Vestnik/KRSU
tail run `pdf-vestnik-krsu-missing3-reharvest-d39e366` recovered 0/3
`good_pdf`; all three candidate `article/download` routes resolved to archive
HTML and read-only confirmation `pdf-vestnik-krsu-missing3-readonly-d39e366`
returned all three rows to `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`5a217501 #461 taxicab-pdf: add vestnik krsu tail packet` publishes the queue,
summaries, reports, provider packet, and next Duke University Press queue. Duke
University Press tail run `pdf-dukeupress-missing3-reharvest-c04d081`
recovered 0/3 `good_pdf`; all three candidate `article-pdf` routes resolved to
article abstract HTML with `redirectedFrom=fulltext`, and read-only confirmation
`pdf-dukeupress-missing3-readonly-c04d081` returned all three rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`1e18ffdd #461 taxicab-pdf: add dukeupress tail packet` publishes the queue,
summaries, reports, provider packet, and next GeoScienceWorld queue.
GeoScienceWorld tail run `pdf-geoscienceworld-missing3-reharvest-98bb851`
recovered 0/3 `good_pdf`; all three candidate `article-pdf` routes resolved to
article abstract HTML with `redirectedFrom=fulltext`, and read-only confirmation
`pdf-geoscienceworld-missing3-readonly-98bb851` returned all three rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`b3ba464e #461 taxicab-pdf: add geoscienceworld tail packet` publishes the
queue, summaries, reports, provider packet, and next Indian Journals queue.
Indian Journals tail run `pdf-indianjournals-missing6-reharvest-dcadb4a`
recovered 0/6 `good_pdf`; all six candidate PDF/API routes resolved to HTML
article pages, and read-only confirmation
`pdf-indianjournals-missing6-readonly-dcadb4a` returned all six rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`f4e4fe37 #461 taxicab-pdf: add indianjournals tail packet` publishes the queue,
summaries, reports, provider packet, and next AJConline queue. AJConline tail
run `pdf-ajconline-missing3-reharvest-261a3ca` recovered 0/3 `good_pdf`; all
three candidate article PDF routes resolved to article abstract HTML, and
read-only confirmation `pdf-ajconline-missing3-readonly-261a3ca` returned all
three rows to `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `b4b2a251 #461 taxicab-pdf: add ajconline tail packet` publishes
the queue, summaries, reports, provider packet, and next IATED queue. IATED tail
run `pdf-iated-missing3-reharvest-4a1e0d9` recovered 0/3 `good_pdf`; all three
download routes returned invalid PDF content, and read-only confirmation
`pdf-iated-missing3-readonly-4a1e0d9` returned all three rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`2fb1349a #461 taxicab-pdf: add iated tail packet` publishes the queue,
summaries, reports, provider packet, and next Brepols queue. Brepols tail run
`pdf-brepolsonline-missing3-reharvest-d690cd3` recovered 0/3 `good_pdf`; all
three `doi/epdf` routes returned invalid PDF content, and read-only confirmation
`pdf-brepolsonline-missing3-readonly-d690cd3` returned all three rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`9918c055 #461 taxicab-pdf: add brepols tail packet` publishes the queue,
summaries, reports, provider packet, and next Copernicus queue. Oxjobs commit
`6a85359b #461 taxicab-pdf: expose recent tail artifacts` allowlists the recent
tail assets. Copernicus Meeting Organizer tail run
`pdf-copernicus-meetingorganizer-missing3-reharvest-638dd13` recovered 0/3
`good_pdf`; all three `*.html?pdf` routes stored article HTML and produced no
durable PDF record. Read-only confirmation
`pdf-copernicus-meetingorganizer-missing3-readonly-638dd13` returned all three
rows to `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs
commit `4bc7763f #461 taxicab-pdf: add copernicus tail packet` publishes the
scrubbed summaries, reports, provider packet, and next Google Drive queue.
Google Drive tail run `pdf-google-drive-missing3-reharvest-47e462f` recovered
0/3 `good_pdf`; all three viewer routes stored HTML and produced no durable PDF
record. Read-only confirmation `pdf-google-drive-missing3-readonly-47e462f`
returned all three rows to `missing_pdf_harvest`, with 0 timeout and
0 `taxicab_error`. Oxjobs commit
`3bd2e947 #461 taxicab-pdf: add google drive tail packet` publishes the
scrubbed summaries, reports, provider packet, and next protocols.io queue.
protocols.io tail run `pdf-protocols-io-missing3-reharvest-bc519d2` recovered
2/3 `good_pdf`; read-only confirmation
`pdf-protocols-io-missing3-readonly-bc519d2` preserved 2/3 durable PDFs and
left one `corrupt_or_truncated_pdf`, with 0 timeout and 0 `taxicab_error`.
Oxjobs commit `95fd1945 #461 taxicab-pdf: add protocols io recovery` publishes
the scrubbed summaries, reports, residual packet, and next ASA/Scitation queue.
ASA/Scitation tail run `pdf-asa-scitation-missing3-reharvest-724b48e`
recovered 0/3 `good_pdf`; direct `asa.scitation.org/doi/pdf/...` routes
stored status-201 HTML captures and produced no durable PDF record. Read-only
confirmation `pdf-asa-scitation-missing3-readonly-724b48e` returned all three
rows to `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs
commit `d457927c #461 taxicab-pdf: add asa scitation tail packet` publishes
the scrubbed summaries, reports, provider packet, and next IOS Press queue.
IOS Press tail run `pdf-iospress-missing3-reharvest-c08a1e4` recovered 0/3
`good_pdf`; two explicit IOS Press download routes returned invalid PDF content
and one DOI redirected to Sage-hosted HTML/no durable PDF record. Read-only
confirmation `pdf-iospress-missing3-readonly-c08a1e4` returned all three rows
to `missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`930c773c #461 taxicab-pdf: add iospress tail packet` publishes the scrubbed
summaries, reports, provider packet, and next AAI Journals queue. Next tail
lane AAI Journals run `pdf-aai-journals-missing3-reharvest-24795ac` recovered
0/3 `good_pdf`; every explicit `journals.aai.org/article-pdf/...` route stored
HTML/no durable PDF records. Read-only confirmation
`pdf-aai-journals-missing3-readonly-24795ac` returned all three rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`ebff6475 #461 taxicab-pdf: add aai journals tail packet` publishes the
scrubbed summaries, reports, provider packet, and next JCVA Online queue. JCVA
Online run `pdf-jcvaonline-missing3-reharvest-dc3bba1` recovered 0/3
`good_pdf`; two article PDF routes resolved to abstract HTML/no durable PDF
records and one candidate returned invalid PDF content. Read-only confirmation
`pdf-jcvaonline-missing3-readonly-dc3bba1` returned all three rows to
`missing_pdf_harvest`, with 0 timeout and 0 `taxicab_error`. Oxjobs commit
`e48d73e8 #461 taxicab-pdf: add jcvaonline tail packet` publishes the scrubbed
summaries, reports, provider packet, and next Human Kinetics queue. Next tail
lane Human Kinetics run `pdf-humankinetics-missing3-reharvest-bbd2225`
recovered 1/3 `good_pdf`; read-only confirmation
`pdf-humankinetics-missing3-readonly-bbd2225` preserved one durable PDF and
left two XML-HTML/no-record rows missing. Oxjobs commit
`93b383f6 #461 taxicab-pdf: add humankinetics recovery packet` publishes the
scrubbed summaries, reports, and residual provider packet. Full gate
`pdf-full10k-after-humankinetics-bbd2225` accepted 1,910/6,293 `good_pdf`
(30.35%), +20 versus Karger and +73 versus the denominator baseline, with 0
timeout and 0 `taxicab_error`; oxjobs commit `43ca3830` publishes that report.
Latest Taxicab code/eval commit before this handoff-doc update is `bdcc38a`.

## Agent Operating Rules

- Active repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- `main` auto-deploys to ECS through `.github/workflows/aws.yml`. Work on a `codex/` branch and push only after focused verification.
- For PDF Phase 2, use `codex/taxicab-pdf-phase2` after the HTML Phase 1 main-sync commit is on `main`.
- Never print or commit secret values. Secret names may appear in docs, but raw values for `ZYTE_API_KEY`, `BROWSERBASE_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `R2_SECRET_ACCESS_KEY`, and `CRAWLERA_KEY` must stay out of tracked files and reports.
- Use the local ignored credential files before asking Shubh to authenticate. `.env` contains Taxicab provider/R2/Zyte material, and ignored `/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/.env` contains `BROWSERBASE_API_KEY`; `BROWSERBASE_PROJECT_ID` is optional for the current REST session path. Load credentials into process environment without echoing values.
- AWS CLI/default `.env.aws` session credentials were last verified expired. AWS is not needed for the immediate no-storage evidence loop; when ECS, CloudWatch, Secrets Manager, or SSM discovery is needed, refresh auth with `aws login` or a complete non-expired ignored env pair.
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
python3 scripts/secret_scan.py
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
