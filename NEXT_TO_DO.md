# Taxicab V1 next work for Codex and Claude

Last updated: 2026-06-13 02:35 PDT.

This file is the handoff contract for the Taxicab retrieval-quality project. Read it before doing new work. Keep it current before ending a long session.

## Absolute paths

- Active Taxicab repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`
- Do not use: `/Users/shubh-trips/Documents/openalex-taxicab`
- Oxjobs #133 report/control repo: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`
- Taxicab issue registry: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-harvest-router-issues` (#329)
- Parseland-only report: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/parseland-work-reporting` (#336). Do not put Taxicab V1 KPIs there.

## Git state to expect

- Taxicab branch: `codex/taxicab-v1-eval-system`
- Latest accepted production measurement is `full10k-mdpi-jbc-preprints-clean-e22b60e`: **9,583/10,000 `good_html` (95.83%)**, target crossed by 83 rows, +135 rows over the Oxford gate, 0 good-to-non-good regressions.
- Production `main` contains the accepted Preprints, JBC, and MDPI retrieval fixes plus deploy-stability/health-check changes:
  - `9ef6c9b taxicab: use browser html for preprints`
  - `ab5de79 taxicab: use resolved browser routes after doi redirects`
  - `5aba149 taxicab: route jbc linkinghub dois to fulltext`
  - `876887a taxicab: use browser html for mdpi`
  - `62b5f01 taxicab: wait for ecs deploy stability`
  - `54bbe83 taxicab: make health check lightweight`
  - `e22b60e taxicab: use threaded gunicorn workers`
- Taxicab branch `codex/taxicab-v1-eval-system` contains the same code-line changes and this handoff update.
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

## Immediate next actions

### 1. Continue from the post-95 residual queue

Use the accepted post-95 queue:

```text
oxjobs: working/taxicab-audit/evidence/report133-quarry-residual-clusters-e22b60e.json
browserbase candidates: working/taxicab-audit/evidence/report133-browserbase-candidates-e22b60e.csv
zyte candidates: working/taxicab-audit/evidence/report133-zyte-support-candidates-e22b60e.csv
```

The next high-signal work is PDF-vs-landing splitting, IOP/MUSE bot-block evidence, Optica/Crossref/router cleanup, residual DOI.org JS host splitting, and unknown-publisher interpretability. MDPI, JBC, and Preprints are complete unless new residual rows appear.

### 2. If making production scraping changes

Keep the loop strict:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
targeted cluster eval
full 10K read-only gate if production behavior changed
```

Do not update the public KPI from a targeted gate alone. Full gate acceptance still requires 0 unexplained good-to-non-good regressions, 0 `taxicab_error`, and no unresolved timeout artifacts.

### 3. ECS deploy notes

The default `aws ecs wait services-stable` can time out on this large service even after useful tasks are serving. The accepted `e22b60e` rollout was validated by live LB checks and targeted/full retrieval gates after the waiter timed out. When AWS auth is fresh, inspect target health directly instead of relying only on the GitHub waiter:

```bash
aws ecs describe-services --cluster harvester --services harvester-service
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
aws logs tail <log-group> --since 30m
```

If local AWS auth is expired, ask Shubh to refresh with `aws login`. The ignored `.env` and `.env.aws` files exist, but a previous safe check showed the refreshed credentials were still expired. Do not print values from either file.

### 4. IOP bot-block cluster

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
