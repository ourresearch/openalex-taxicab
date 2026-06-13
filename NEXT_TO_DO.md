# Taxicab V1 next work for Codex and Claude

Last updated: 2026-06-12 22:20 America/Los_Angeles.

This file is the handoff contract for the Taxicab retrieval-quality project. Read it before doing new work. Keep it current before ending a long session.

## Absolute paths

- Active Taxicab repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`
- Do not use: `/Users/shubh-trips/Documents/openalex-taxicab`
- Oxjobs #133 report/control repo: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`
- Taxicab issue registry: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-harvest-router-issues` (#329)
- Parseland-only report: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/parseland-work-reporting` (#336). Do not put Taxicab V1 KPIs there.

## Git state to expect

- Taxicab branch: `codex/taxicab-v1-eval-system`
- Latest Taxicab production main includes `d1aa4ef taxicab: use browser html for uq espace`; ECS deploy completed green.
- Taxicab branch history includes `1cc9f6c taxicab: use browser html for uq espace`; production main cherry-picked it as `d1aa4ef`.
- Taxicab production `main` auto-deploys to ECS. Do not push production scraping changes to `main` without targeted proof plus full 10K no-regression proof.
- Oxjobs main has #133 reporting updates through `a0a55bd6 #133 taxicab-audit: accept uq espace gate`. If the next agent changes reporting, stage only `working/taxicab-audit`.

## Current accepted measurement

Accepted full run: `full10k-uq-deployed-clean-d1aa4ef`

```text
good_html: 9,440 / 10,000
good_html_rate: 94.40%
gap_to_95_rows: 60
non_good_rows: 560
residual_clusters: current queue in oxjobs evidence/report133-quarry-residual-clusters-uq-d1aa4ef.json
```

Category counts:

```text
good_html: 9440
router_only: 165
pdf_instead_of_html: 135
empty_response: 68
bot_block_403: 65
js_required: 62
missing_harvest: 48
download_404: 0
invalid_content: 17
taxicab_error: 0
timeout: 0
```

Authoritative local artifacts:

```text
eval_runs/full10k-uq-deployed-clean-d1aa4ef/rows.ndjson
eval_runs/full10k-uq-deployed-clean-d1aa4ef/summary.json
eval_runs/full10k-uq-deployed-clean-d1aa4ef/hardness.json
eval_runs/full10k-uq-deployed-clean-d1aa4ef/report.html
/tmp/taxicab-uq-espace/uq2-reharvest-retry-d1aa4ef/summary.json
/tmp/taxicab-uq-espace/doiorg-recoverable4-readonly-final-d1aa4ef/summary.json
/tmp/taxicab-uq-espace/quarry-full10k-uq-d1aa4ef/residual-clusters.json
/tmp/taxicab-uq-espace/quarry-full10k-uq-d1aa4ef/browserbase-candidates.csv
/tmp/taxicab-uq-espace/quarry-full10k-uq-d1aa4ef/zyte-support-candidates.csv
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
- Live #133 graph verification passed after oxjobs commit `a0a55bd6`: public raw report contains `<svg class="curve"` and not `<img class="curve"`. Latest live report contains `94.40%`, and the UQ full-gate JSON returns 9,440 `good_html`.
- MDPI Browserbase session evidence was expanded on 2026-06-11: Taxicab stayed `router_only` for 10/10 sampled MDPI rows, while Browserbase full sessions recovered `good_html` for 10/10. Compact public artifact: `working/taxicab-audit/evidence/report133-mdpi-browserbase-session-expanded10-9287bb9.json`.
- IOP Browserbase session evidence was completed on 2026-06-11: current Taxicab read-only stayed `bot_block_403` for 14/14 `iopscience.iop.org` residual rows; Browserbase sessions recovered article-level `good_html` for 2/14 and stayed `bot_block_403` for 12/14, with screenshots captured for 14/14. Compact public artifact: `working/taxicab-audit/evidence/report133-iop-browserbase-session-fc4896d.json`; support packet: `working/taxicab-audit/evidence/report133-iop-zyte-support-packet.md`.
- Browserbase evidence classifier was tightened on branch commits `a6bfebf` and `0522d6e` so generic 404/520/browser error pages no longer count as Browserbase `good_html`. Tests now cover large error pages and real articles that merely mention 404/520 terms.
- DOI.org JS-required cluster was triaged on 2026-06-11: Taxicab remains non-good for 11/11 rows after the error-page guard (10 `js_required`, one `invalid_content`); Browserbase sessions recovered article-level `good_html` for 4/11 and classified 7/11 as invalid/error. Compact public artifact: `working/taxicab-audit/evidence/report133-doiorg-js-browserbase-session-0522d6e.json`; triage note: `working/taxicab-audit/evidence/report133-doiorg-js-triage-0522d6e.md`.
- Wolters Kluwer/Lippincott JS-required cluster was triaged on 2026-06-12: Taxicab read-only remains `js_required` for 11/11 rows on `login.wolterskluwer.com`; the first Browserbase pass exposed a false-positive `good_html` bug on `Page Expired` login pages; branch commit `2acd1eb` fixes expired-login evidence classification; corrected Browserbase session evidence is 0/11 `good_html`, 11/11 `invalid_content`, with 11 screenshots captured locally. Compact public artifact: `working/taxicab-audit/evidence/report133-wolterskluwer-pageexpired-browserbase-session-2acd1eb.json`; triage note: `working/taxicab-audit/evidence/report133-wolterskluwer-pageexpired-triage-2acd1eb.md`.
- ASME JS-required cluster was completed on 2026-06-12: initial Taxicab read-only was 8/8 `js_required`; Browserbase sessions recovered 5/8 article pages; direct Zyte no-storage browserHtml recovered 6/8; production main `fab783d` deployed the narrow ASME browserHtml route; bounded reharvest plus one-row retry recovered 8/8; final read-only confirmation stayed 8/8 `good_html`; full 10K accepted `full10k-asme-deployed-clean-fab783d` at 9,436/10,000 `good_html`. Public artifacts: `working/taxicab-audit/evidence/report133-asme-browserhtml-candidate-619739d.json`, `working/taxicab-audit/evidence/report133-asme-reharvest-live-fab783d.json`, `working/taxicab-audit/evidence/report133-asme-readonly-after-reharvest-fab783d.json`, and `working/taxicab-audit/evidence/report133-asme-fullgate-fab783d.json`.
- UQ eSpace / DOI.org recoverable rows were completed on 2026-06-12: two UQ eSpace DOI.org rows required Zyte `browserHtml=true` to avoid a small browser-compatibility shell, while the ASM Digital Library and Kyobo Scholar rows recovered after DOI.org final-host reharvest/read-back. Production main `d1aa4ef` deployed the narrow UQ eSpace browserHtml route; full 10K accepted `full10k-uq-deployed-clean-d1aa4ef` at 9,440/10,000 `good_html`. Public artifacts: `working/taxicab-audit/evidence/report133-uq-reharvest-d1aa4ef.json`, `working/taxicab-audit/evidence/report133-uq-readonly-d1aa4ef.json`, and `working/taxicab-audit/evidence/report133-uq-fullgate-d1aa4ef.json`.

## Browserbase and secrets

- Do not print secrets.
- Load local ignored credential files before asking Shubh to authenticate. Active Taxicab `.env` has provider/R2/Zyte material and `.env.aws` has AWS CLI-style session variables. Do not echo values. Ask for auth only if a safe command proves the local session is expired or the files are missing.
- Do not say Browserbase credentials are missing until you have checked ignored local env files and safe AWS/env discovery without printing values. Browserbase REST evidence has already worked in this environment; project ID was not required for the current REST session path.
- Live probe result: Browserbase REST session create returned HTTP 201 in 0.22s and release returned HTTP 200.
- Current runner state: local Playwright startup passed, and `--with-browserbase --browserbase-mode session` completed the 10-row MDPI sample under `--row-timeout 150`. Keep using row watchdogs for Browserbase session loops.

## Immediate next actions

### 1. MDPI router protection: Envoy, not Mechanic

This is the largest residual cluster and can cross the 95% target if Zyte recovers it.

Current evidence:

```text
cluster: router_only / mdpi / mdpi.com
rows: 119
current 10-row Taxicab read-only check: 10/10 router_only
Zyte-core reharvest sample: 0/5 recovered, all bm-verify/router shells
Browserbase Fetch: 0/5 recovered
Browserbase full session: 10/10 recovered to good_html, 9/10 screenshots captured locally
support packet: oxjobs working/taxicab-audit/evidence/report133-mdpi-zyte-support-packet.md
compact artifact: oxjobs working/taxicab-audit/evidence/report133-mdpi-browserbase-session-expanded10-9287bb9.json
```

Next step: send or otherwise escalate the MDPI support packet to Zyte. Do not patch Taxicab production behavior for MDPI unless Zyte support evidence or a narrow routing/config hypothesis says Taxicab can safely fix it. After Zyte responds or provider-side behavior changes, run:

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

If targeted MDPI improves, run a full 10K read-only gate before changing the public KPI.

### 2. IOP bot-block cluster

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

### 3. OUP / Oxford JS shells

Current UQ residuals show Oxford/OUP JS rows as the next plausible Taxicab-side browserHtml probe after MDPI/IOP support lanes.

```text
publisher: oxford
main host: academic.oup.com
current matrix: 9 js_required, one missing_harvest under oxford
recommended agents: Quarry + Lens + Mechanic
```

Next step: build a small DOI file from `working/taxicab-audit/evidence/report133-quarry-residual-clusters-uq-d1aa4ef.json`, run read-only confirmation, then run a no-storage direct Zyte `browserHtml=true` probe before proposing any production route.

### 4. Optica router/wait shells

Prior Quarry noted `opg.optica.org` rows with `viewmedia.cfm?...html=true` wait shells. Current UQ summary shows seven `opg.optica.org` router rows.

Next step: create a target DOI file from the UQ residual cluster artifact, run read-only confirmation, then test URL cleanup or browserHtml no-storage. Do not patch until a narrow hypothesis recovers article HTML.

### 5. Crossref chooser and Project MUSE residuals

Current host matrix includes Crossref chooser/router rows and `muse.jhu.edu` verify/bot rows. These are Taxicab-side candidates only after separate host-specific probes.

Next step: split into two DOI files, one for Crossref chooser and one for MUSE verify, then test URL extraction/rewrite without storage.

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

Done after oxjobs commit `a0a55bd6`: live report HTML contains `<svg class="curve"`, does not contain `<img class="curve"`, includes `94.40%`, and exposes the accepted UQ full-gate JSON. Re-run if the report is regenerated:

```bash
curl -L -sS -o /tmp/ox133.html https://oxjobs.org/reports/133
curl -L -sS -o /tmp/ox133-report.html 'https://oxjobs.org/reports/133/raw?path=evidence/report.html'
rg -n '<svg class="curve"|<img class="curve"' /tmp/ox133-report.html
curl -L -sS -o /tmp/ox133-curve.svg -w '%{http_code} %{content_type}\n' 'https://oxjobs.org/reports/133/raw?path=evidence/curve-latest.svg'
```

Expected: report HTML contains `<svg class="curve"` and not `<img class="curve"`; the standalone curve asset returns `200 image/svg+xml`.

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
