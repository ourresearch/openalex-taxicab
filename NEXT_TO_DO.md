# Taxicab V1 next work for Codex and Claude

Last updated: 2026-06-13 01:03 PDT.

This file is the handoff contract for the Taxicab retrieval-quality project. Read it before doing new work. Keep it current before ending a long session.

## Absolute paths

- Active Taxicab repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`
- Do not use: `/Users/shubh-trips/Documents/openalex-taxicab`
- Oxjobs #133 report/control repo: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`
- Taxicab issue registry: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-harvest-router-issues` (#329)
- Parseland-only report: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/parseland-work-reporting` (#336). Do not put Taxicab V1 KPIs there.

## Git state to expect

- Taxicab branch: `codex/taxicab-v1-eval-system`
- Latest accepted production measurement is still based on `d1aa4ef taxicab: use browser html for uq espace` plus the Oxford cache refresh. The accepted KPI is **94.48%**, not 95% yet.
- Production `main` now also contains narrow Preprints, JBC, and MDPI retrieval fixes plus deploy-stability/health-check changes:
  - `9ef6c9b taxicab: use browser html for preprints`
  - `ab5de79 taxicab: use resolved browser routes after doi redirects`
  - `5aba149 taxicab: route jbc linkinghub dois to fulltext`
  - `876887a taxicab: use browser html for mdpi`
  - `62b5f01 taxicab: wait for ecs deploy stability`
  - `54bbe83 taxicab: make health check lightweight`
- Those main commits are **not accepted into the public KPI yet** because the ECS service is mixed/unstable and the deploy waiter is failing. Do not run a full 10K acceptance gate or publish a 95% claim until the fleet is stable and live targeted checks are consistent.
- Taxicab branch `codex/taxicab-v1-eval-system` contains the same code-line changes. At this handoff it may be ahead of origin by the deploy-stability and lightweight-health commits; push it after tests and this handoff update.
- Taxicab production `main` auto-deploys to ECS. Further production pushes should be limited to deploy diagnostics/stability unless a targeted recovery has already passed local proof and production risk is understood.
- Oxjobs main has #133 reporting updates through `4fd1fcce #133 taxicab-audit: accept oxford cache refresh gate`. If the next agent changes reporting, stage only `working/taxicab-audit`.

## Current accepted measurement

Accepted full run: `full10k-oxford-reharvest-clean-d1aa4ef`

```text
good_html: 9,448 / 10,000
good_html_rate: 94.48%
gap_to_95_rows: 52
non_good_rows: 552
residual_clusters: current queue in oxjobs evidence/report133-quarry-residual-clusters-oxford-d1aa4ef.json
```

Category counts:

```text
good_html: 9448
router_only: 165
pdf_instead_of_html: 135
empty_response: 67
bot_block_403: 65
js_required: 55
missing_harvest: 48
download_404: 0
invalid_content: 17
taxicab_error: 0
timeout: 0
```

## Current unaccepted recovery candidates

These are local/partial-production wins that should push Taxicab over 95% once ECS is stable and targeted reharvest/read-only gates pass. Do not count them in public reporting yet.

```text
Preprints router cluster: 8/8 recovered locally with browserHtml after DOI redirect routing fix
JBC empty-response cluster: 8/8 recovered locally by rewriting old JBC LinkingHub/PDF URLs to /fulltext
MDPI router cluster: 10/10 sampled recovered locally with browserHtml; residual cluster has 119 rows
Theoretical gross lift if MDPI holds across the residual cluster: enough to clear the 52-row gap to 95%
Current blocker: ECS deployment is mixed/rolling back, so production still intermittently serves old routing or times out
```

Authoritative local artifacts:

```text
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/rows.ndjson
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/summary.json
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/hardness.json
eval_runs/full10k-oxford-reharvest-clean-d1aa4ef/report.html
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
- Live #133 graph verification passed after oxjobs commit `4fd1fcce`: public raw report contains `<svg class="curve"` and not `<img class="curve"`. Latest live report contains `94.48%`, and the Oxford full-gate JSON returns 9,448 `good_html`.
- MDPI Browserbase session evidence was expanded on 2026-06-11: Taxicab stayed `router_only` for 10/10 sampled MDPI rows, while Browserbase full sessions recovered `good_html` for 10/10. Compact public artifact: `working/taxicab-audit/evidence/report133-mdpi-browserbase-session-expanded10-9287bb9.json`.
- IOP Browserbase session evidence was completed on 2026-06-11: current Taxicab read-only stayed `bot_block_403` for 14/14 `iopscience.iop.org` residual rows; Browserbase sessions recovered article-level `good_html` for 2/14 and stayed `bot_block_403` for 12/14, with screenshots captured for 14/14. Compact public artifact: `working/taxicab-audit/evidence/report133-iop-browserbase-session-fc4896d.json`; support packet: `working/taxicab-audit/evidence/report133-iop-zyte-support-packet.md`.
- Browserbase evidence classifier was tightened on branch commits `a6bfebf` and `0522d6e` so generic 404/520/browser error pages no longer count as Browserbase `good_html`. Tests now cover large error pages and real articles that merely mention 404/520 terms.
- DOI.org JS-required cluster was triaged on 2026-06-11: Taxicab remains non-good for 11/11 rows after the error-page guard (10 `js_required`, one `invalid_content`); Browserbase sessions recovered article-level `good_html` for 4/11 and classified 7/11 as invalid/error. Compact public artifact: `working/taxicab-audit/evidence/report133-doiorg-js-browserbase-session-0522d6e.json`; triage note: `working/taxicab-audit/evidence/report133-doiorg-js-triage-0522d6e.md`.
- Wolters Kluwer/Lippincott JS-required cluster was triaged on 2026-06-12: Taxicab read-only remains `js_required` for 11/11 rows on `login.wolterskluwer.com`; the first Browserbase pass exposed a false-positive `good_html` bug on `Page Expired` login pages; branch commit `2acd1eb` fixes expired-login evidence classification; corrected Browserbase session evidence is 0/11 `good_html`, 11/11 `invalid_content`, with 11 screenshots captured locally. Compact public artifact: `working/taxicab-audit/evidence/report133-wolterskluwer-pageexpired-browserbase-session-2acd1eb.json`; triage note: `working/taxicab-audit/evidence/report133-wolterskluwer-pageexpired-triage-2acd1eb.md`.
- ASME JS-required cluster was completed on 2026-06-12: initial Taxicab read-only was 8/8 `js_required`; Browserbase sessions recovered 5/8 article pages; direct Zyte no-storage browserHtml recovered 6/8; production main `fab783d` deployed the narrow ASME browserHtml route; bounded reharvest plus one-row retry recovered 8/8; final read-only confirmation stayed 8/8 `good_html`; full 10K accepted `full10k-asme-deployed-clean-fab783d` at 9,436/10,000 `good_html`. Public artifacts: `working/taxicab-audit/evidence/report133-asme-browserhtml-candidate-619739d.json`, `working/taxicab-audit/evidence/report133-asme-reharvest-live-fab783d.json`, `working/taxicab-audit/evidence/report133-asme-readonly-after-reharvest-fab783d.json`, and `working/taxicab-audit/evidence/report133-asme-fullgate-fab783d.json`.
- UQ eSpace / DOI.org recoverable rows were completed on 2026-06-12: two UQ eSpace DOI.org rows required Zyte `browserHtml=true` to avoid a small browser-compatibility shell, while the ASM Digital Library and Kyobo Scholar rows recovered after DOI.org final-host reharvest/read-back. Production main `d1aa4ef` deployed the narrow UQ eSpace browserHtml route; full 10K accepted `full10k-uq-deployed-clean-d1aa4ef` at 9,440/10,000 `good_html`. Public artifacts: `working/taxicab-audit/evidence/report133-uq-reharvest-d1aa4ef.json`, `working/taxicab-audit/evidence/report133-uq-readonly-d1aa4ef.json`, and `working/taxicab-audit/evidence/report133-uq-fullgate-d1aa4ef.json`.
- Oxford/OUP cache-refresh was completed on 2026-06-12 with no production code change: targeted Oxford reharvest recovered 8/11 non-good rows, read-only confirmation persisted 8/11, and a three-row timeout sentinel cleared aggressive full-run measurement artifacts. The clean full 10K gate accepted `full10k-oxford-reharvest-clean-d1aa4ef` at 9,448/10,000 `good_html` (94.48%), net +8 rows, gap 52, 0 good-to-non-good regressions, 0 `timeout`, and 0 `taxicab_error`. Public artifacts: `working/taxicab-audit/evidence/report133-oxford-reharvest-d1aa4ef.json`, `working/taxicab-audit/evidence/report133-oxford-readonly-d1aa4ef.json`, `working/taxicab-audit/evidence/report133-oxford-timeout-sentinel-d1aa4ef.json`, and `working/taxicab-audit/evidence/report133-oxford-fullgate-d1aa4ef.json`.
- Preprints local recovery was proven on 2026-06-13: the Oxford residual set had eight `router_only` rows on `preprints.org`; default Zyte through the DOI URL returned 2.6-2.8 KB privacy/router shells, while forced `browserHtml` on the resolved Preprints URL returned 331 KB to 1.86 MB article HTML for 8/8 rows. Production main has the narrow route and DOI-redirect fix, but targeted production reharvest initially still saw old behavior before the ECS deploy instability was diagnosed.
- JBC local recovery was proven on 2026-06-13: eight `jbc.org` `empty_response` rows were old Elsevier/LinkingHub DOIs landing on tiny `/pdf` viewer shells; local routing rewrites compact JBC PII URLs to `https://www.jbc.org/article/<PII>/fulltext`; 8/8 no-storage probes classified `good_html`. Production main contains this route, but live `/test-zyte` is mixed because some requests still hit old tasks.
- MDPI local recovery was proven on 2026-06-13: residual cluster has 119 `router_only` rows on `mdpi.com`; 10-row Taxicab read-only confirmation stayed `router_only`; Browserbase session evidence recovered 10/10; local Zyte `browserHtml` on the resolved MDPI URL recovered 10/10 large article pages with article signals. Production main contains the narrow `mdpi.com` browserHtml route, but live `/test-zyte` is mixed and sometimes times out because ECS has not stabilized.
- Deploy-stability instrumentation was added on 2026-06-13: `.github/workflows/aws.yml` now waits for ECS service stability after `update-service`, and `/` plus `/health` are lightweight JSON health endpoints while the old metadata response moved to `/metadata`. The deploy waiter currently fails after about 10 minutes because the service rolls back to older task definitions; this is the active blocker before accepting the MDPI/JBC/Preprints lift.

## Browserbase and secrets

- Do not print secrets.
- Load local ignored credential files before asking Shubh to authenticate. Active Taxicab `.env` has provider/R2/Zyte material and `.env.aws` has AWS CLI-style session variables. Do not echo values. Ask for auth only if a safe command proves the local session is expired or the files are missing.
- Do not say Browserbase credentials are missing until you have checked ignored local env files and safe AWS/env discovery without printing values. Browserbase REST evidence has already worked in this environment; project ID was not required for the current REST session path.
- Live probe result: Browserbase REST session create returned HTTP 201 in 0.22s and release returned HTTP 200.
- Current runner state: local Playwright startup passed, and `--with-browserbase --browserbase-mode session` completed the 10-row MDPI sample under `--row-timeout 150`. Keep using row watchdogs for Browserbase session loops.

## Immediate next actions

### 1. Stabilize ECS before claiming the 95% lift

This is the blocker. Local code is likely enough to cross 95% because MDPI alone has 119 candidate rows and the accepted gap is only 52 rows, but production cannot be measured cleanly while the ECS service is mixed.

Known deploy evidence:

```text
GitHub deploy run for 62b5f01: failed at aws ecs wait services-stable after about 10 minutes
GitHub deploy run for 54bbe83: failed at aws ecs wait services-stable after about 10 minutes
Service rolled back toward older task definition 63 while newer task definitions 65/66/67 were partially present
Live / root sampling returned a mixture of new lightweight health JSON, old metadata JSON, and request timeouts
Live /test-zyte sampling returned a mixture of new JBC/MDPI article recoveries, old JBC /pdf shell behavior, and 504 timeout
```

Next diagnostic, once AWS CLI auth is usable:

```bash
aws ecs describe-services --cluster harvester --services harvester-service
aws ecs list-tasks --cluster harvester --service-name harvester-service --desired-status RUNNING
aws ecs describe-tasks --cluster harvester --tasks <task-arns>
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
aws logs describe-log-groups --log-group-name-prefix /ecs
aws logs tail <log-group> --since 30m
```

If local AWS auth is expired, ask Shubh to refresh with `aws login`. The ignored `.env` and `.env.aws` files exist, but a previous safe check showed the refreshed credentials were still expired. Do not print values from either file.

Avoid another `main` push unless it is specifically for deploy diagnostics/stability. Any `main` push triggers the ECS deploy workflow again.

### 2. Push the Taxicab branch handoff and parity commits

Before pushing branch `codex/taxicab-v1-eval-system`, run:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
git diff --check
```

Then commit this `NEXT_TO_DO.md` update and push the branch. The branch should include the deploy waiter and health endpoint commits so Claude/Codex can continue from the same state.

### 3. MDPI production gate after ECS stabilizes

MDPI is now a Mechanic candidate, not only Envoy. Browserbase proved recoverability, and local Zyte `browserHtml` proved a narrow Taxicab-side route can recover article HTML. The production route is already on `main`, but the fleet must be stable first.

Current evidence:

```text
cluster: router_only / mdpi / mdpi.com
rows: 119
current 10-row Taxicab read-only check before route: 10/10 router_only
Browserbase full session: 10/10 recovered to good_html
local Zyte browserHtml no-storage sample after route: 10/10 good_html
production state: mixed fleet; some /test-zyte calls recover article HTML, some time out or hit old behavior
compact artifact: oxjobs working/taxicab-audit/evidence/report133-mdpi-browserbase-session-expanded10-9287bb9.json
```

After ECS is stable, run:

```bash
python3 scripts/taxicab_eval.py \
  --doi-file /tmp/taxicab-mdpi-expanded10-bd4a8e3.csv \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --out eval_runs \
  --run-id mdpi-after-zyte-response-readonly-<sha> \
  --workers 4 \
  --timeout 45 \
  --retries 2 \
  --progress-every 1
```

If targeted MDPI improves, run the full 119-row cluster reharvest/read-only confirmation and then a full 10K read-only gate before changing the public KPI.

### 4. JBC production gate after ECS stabilizes

Current evidence:

```text
cluster: empty_response / jbc / jbc.org
rows: 8
root cause: old JBC/Elsevier LinkingHub DOI paths land on tiny /pdf viewer shells
local route: rewrite compact JBC PII paths to /fulltext
local no-storage result: 8/8 good_html
production state: mixed fleet; some /test-zyte calls use /fulltext and some still show old /pdf shell behavior
```

After ECS is stable, reharvest the eight JBC DOI rows from the accepted residual set and run read-only confirmation. If it stays 8/8 `good_html`, include it in the next full 10K gate.

### 5. Preprints production gate after ECS stabilizes

Current evidence:

```text
cluster: router_only / rxiv / preprints.org
rows: 8
root cause: DOI URL path returned privacy/router shells while resolved Preprints browserHtml returns article pages
local result after DOI redirect routing fix: 8/8 good_html
production state: initial reharvest before ECS diagnosis still returned router shells; rerun only after stable deploy
```

After ECS is stable, reharvest and read-only confirm the eight Preprints rows. Include it in the next full 10K gate if it stays recovered.

### 6. Report update only after accepted full gate

Do not update oxjobs #133 to claim 95% until a clean full 10K read-only gate confirms:

```text
good_html >= 9500
good-to-non-good regressions: 0 or fully explained
timeout: 0 or sentinel-cleared
taxicab_error: 0
```

When accepted, update the #133 report in the report-336 style: BLUF box, green improvement numbers, red regressions, inline SVG graph, and recovered publishers listed directly under the BLUF.

### 7. IOP bot-block cluster

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

### 3. Oxford/OUP cache-refresh

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

### 4. Optica router/wait shells

Prior Quarry noted `opg.optica.org` rows with `viewmedia.cfm?...html=true` wait shells. Current Oxford summary shows seven `opg.optica.org` router rows.

Next step: create a target DOI file from the Oxford residual cluster artifact, run read-only confirmation, then test URL cleanup or browserHtml no-storage. Do not patch until a narrow hypothesis recovers article HTML.

### 5. Crossref chooser and Project MUSE residuals

Current host matrix includes Crossref chooser/router rows, `muse.jhu.edu` verify/bot rows, preprints.org router rows, and JBC empty responses. These are Taxicab-side candidates only after separate host-specific probes.

Next step: split into separate DOI files by host (`preprints.org`, `jbc.org`, `muse.jhu.edu`, `opg.optica.org`, `crossref.org`), then test URL extraction/rewrite or browserHtml without storage.

### 6. DOI.org JS-required cluster

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

### 7. Wolters Kluwer / Lippincott expired-login cluster

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

### 8. ASME browserHtml route

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

### 9. Missing-harvest residual tail

There are 48 `missing_harvest` rows left, including 35 unknown/unknown. The latest bounded reharvest recovered 0/48, so this is now lower-yield than MDPI, IOP, and host-specific JS/router work. Any further public KPI claim needs:

1. bounded reharvest with `--row-timeout`;
2. read-only confirmation of recovered rows;
3. timeout sentinel if any watchdog artifacts appear;
4. clean full 10K read-only gate.

### 10. UQ eSpace / DOI.org browserHtml route

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

### 11. #133 graph/report verification

Done after oxjobs commit `4fd1fcce`: live report HTML contains `<svg class="curve"`, does not contain `<img class="curve"`, includes `94.48%`, and exposes the accepted Oxford full-gate JSON. Re-run if the report is regenerated:

```bash
curl -L -sS -o /tmp/ox133.html https://oxjobs.org/reports/133
curl -L -sS -o /tmp/ox133-report.html 'https://oxjobs.org/reports/133/raw?path=evidence/report.html'
rg -n '94\.48%|9,448|Oxford cache-refresh|<svg class="curve"|<img class="curve"' /tmp/ox133-report.html
curl -L -sS -o /tmp/ox133-curve.svg -w '%{http_code} %{content_type}\n' 'https://oxjobs.org/reports/133/raw?path=evidence/curve-latest.svg'
curl -L -sS -o /tmp/ox133-oxford-fullgate.json -w '%{http_code} %{content_type}\n' 'https://oxjobs.org/reports/133/raw?path=evidence/report133-oxford-fullgate-d1aa4ef.json'
```

Expected: report HTML contains `94.48%`, `9,448`, `Oxford cache-refresh`, and `<svg class="curve"` but not `<img class="curve"`; the standalone curve asset returns `200 image/svg+xml`; the Oxford full-gate JSON returns `200 application/json`.

### 12. Browserbase session runner

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
