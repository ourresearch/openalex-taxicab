# Taxicab V1 next work for Codex and Claude

Last updated: 2026-06-11 19:44 America/Los_Angeles.

This file is the handoff contract for the Taxicab retrieval-quality project. Read it before doing new work. Keep it current before ending a long session.

## Absolute paths

- Active Taxicab repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`
- Do not use: `/Users/shubh-trips/Documents/openalex-taxicab`
- Oxjobs #133 report/control repo: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`
- Taxicab issue registry: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-harvest-router-issues` (#329)
- Parseland-only report: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/parseland-work-reporting` (#336). Do not put Taxicab V1 KPIs there.

## Git state to expect

- Taxicab branch: `codex/taxicab-v1-eval-system`
- Latest pushed Taxicab branch commit at handoff: `0522d6e taxicab: tighten browserbase error title guard`
- Taxicab production `main` auto-deploys to ECS. Do not push production scraping changes to `main` without targeted proof plus full 10K no-regression proof.
- Oxjobs main has #133 reporting updates through the Browserbase REST runner artifact. If the next agent changes reporting, stage only `working/taxicab-audit`.

## Current accepted measurement

Accepted full run: `full10k-missing-tail-clean-bd4a8e3`

```text
good_html: 9,432 / 10,000
good_html_rate: 94.32%
gap_to_95_rows: 68
non_good_rows: 568
residual_clusters: 184
```

Category counts:

```text
good_html: 9432
router_only: 165
pdf_instead_of_html: 135
js_required: 86
empty_response: 69
bot_block_403: 65
missing_harvest: 48
download_404: 0
invalid_content: 0
taxicab_error: 0
timeout: 0
```

Authoritative local artifacts:

```text
eval_runs/full10k-missing-tail-clean-bd4a8e3/rows.ndjson
eval_runs/full10k-missing-tail-clean-bd4a8e3/summary.json
eval_runs/full10k-missing-tail-clean-bd4a8e3/hardness.json
eval_runs/full10k-missing-tail-clean-bd4a8e3/report.html
eval_runs/full10k-missing-tail-clean-bd4a8e3/residuals/residual-clusters.json
eval_runs/full10k-missing-tail-clean-bd4a8e3/residuals/browserbase-candidates.csv
eval_runs/full10k-missing-tail-clean-bd4a8e3/residuals/zyte-support-candidates.csv
```

## What is already done

- Eval harness exists and is runnable without importing Flask `app.py`.
- Taxonomy and artifact writers exist.
- `--row-timeout` exists and prevents hung live rows from blocking a whole run.
- Browserbase evidence fields stay separate from Taxicab baseline category.
- ScienceDirect PDF asset rewrite was deployed to Taxicab `main` at `bd4a8e3` and accepted by full 10K read-only gate: +19 `good_html`, 0 regressions.
- Residual missing-harvest tail was accepted by full 10K read-only gate: +19 `good_html`, 0 regressions.
- Browserbase evidence runner was changed on branch commit `2df8910` to use Browserbase REST APIs instead of the local Browserbase Python SDK.
- Report #133 has a report-336-style graph. The graph is embedded inline from `evidence/curve-latest.svg`, matching #336's inline-SVG pattern and avoiding iframe-relative asset resolution failures.
- Live #133 graph verification passed after oxjobs deploy: public raw report contains `<svg class="curve"` and the standalone curve asset returns `200 image/svg+xml`.
- MDPI Browserbase session evidence was expanded on 2026-06-11: Taxicab stayed `router_only` for 10/10 sampled MDPI rows, while Browserbase full sessions recovered `good_html` for 10/10. Compact public artifact: `working/taxicab-audit/evidence/report133-mdpi-browserbase-session-expanded10-9287bb9.json`.
- IOP Browserbase session evidence was completed on 2026-06-11: current Taxicab read-only stayed `bot_block_403` for 14/14 `iopscience.iop.org` residual rows; Browserbase sessions recovered article-level `good_html` for 2/14 and stayed `bot_block_403` for 12/14, with screenshots captured for 14/14. Compact public artifact: `working/taxicab-audit/evidence/report133-iop-browserbase-session-fc4896d.json`; support packet: `working/taxicab-audit/evidence/report133-iop-zyte-support-packet.md`.
- Browserbase evidence classifier was tightened on branch commits `a6bfebf` and `0522d6e` so generic 404/520/browser error pages no longer count as Browserbase `good_html`. Tests now cover large error pages and real articles that merely mention 404/520 terms.
- DOI.org JS-required cluster was triaged on 2026-06-11: Taxicab remains non-good for 11/11 rows after the error-page guard (10 `js_required`, one `invalid_content`); Browserbase sessions recovered article-level `good_html` for 4/11 and classified 7/11 as invalid/error. Compact public artifact: `working/taxicab-audit/evidence/report133-doiorg-js-browserbase-session-0522d6e.json`; triage note: `working/taxicab-audit/evidence/report133-doiorg-js-triage-0522d6e.md`.

## Browserbase and secrets

- Do not print secrets.
- Load local ignored credential files before asking Shubh to authenticate. Active Taxicab `.env` has Zyte/R2/AWS-style material, and `.env.aws` has AWS CLI-style session variables. Do not echo values. Ask for auth only if a safe command proves the local session is expired or the files are missing.
- Active Taxicab `.env` does not have `BROWSERBASE_API_KEY` or `BROWSERBASE_PROJECT_ID`.
- Adjacent ignored file `/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/.env` has `BROWSERBASE_API_KEY`.
- `BROWSERBASE_PROJECT_ID` has not been found; Browserbase REST session creation works without it when the API key infers the project.
- Live probe result: Browserbase REST session create returned HTTP 201 in 0.22s and release returned HTTP 200.
- Current runner state: local Playwright startup passed, and `--with-browserbase --browserbase-mode session` completed the 10-row MDPI sample under `--row-timeout 150`. Keep using row watchdogs for Browserbase session loops.

## Immediate next actions

### 1. #133 graph deploy

Done after oxjobs commit `3b195316`: live report HTML contains `<svg class="curve"` and the standalone curve asset returns `200 image/svg+xml`. Re-run if the report is regenerated:

```bash
curl -L -sS -o /tmp/ox133.html https://oxjobs.org/reports/133
curl -L -sS -o /tmp/ox133-report.html 'https://oxjobs.org/reports/133/raw?path=evidence/report.html'
rg -n '<svg class="curve"|<img class="curve"' /tmp/ox133-report.html
curl -L -sS -o /tmp/ox133-curve.svg -w '%{http_code} %{content_type}\n' 'https://oxjobs.org/reports/133/raw?path=evidence/curve-latest.svg'
```

Expected: report HTML contains `<svg class="curve"` and not `<img class="curve"`; the standalone curve asset returns `200 image/svg+xml`.

### 2. MDPI router protection: Envoy, not Mechanic

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

### 3. IOP bot-block cluster

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

Recovered Browserbase examples:

```text
10.1088/0953-8984/18/20/017 -> Formation of clusters in the 2D t-J model: the mechanism for phase separation - IOPscience
10.1088/1674-4926/25050016 -> A RISC-V 32-bit microprocessor on two-dimensional semiconductor platform - IOPscience
```

Do not rerun this cluster unless checking a Zyte-side/provider-side change. Send the support packet or move Lens to the next residual JS/PDF/empty split.

### 4. DOI.org JS-required cluster

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

Browser-recoverable examples:

```text
10.31399/asm.cp.istfa2015p0082 -> ASM Digital Library article page
10.14264/uql.2015.381 -> UQ eSpace article page
10.14264/46e82ab -> UQ eSpace article page
10.9798/kosham.2017.17.6.135 -> Kyobo Scholar article page
```

Do not send this as one broad Zyte packet. Split by final host before deciding whether a Taxicab resolver/rendering fix or host-specific Zyte support packet is justified.

### 5. Missing-harvest residual tail

There are 48 `missing_harvest` rows left, including 35 unknown/unknown. This is now lower-yield than MDPI but still useful. Any further public KPI claim needs:

1. bounded reharvest with `--row-timeout`;
2. read-only confirmation of recovered rows;
3. timeout sentinel if any watchdog artifacts appear;
4. clean full 10K read-only gate.

### 6. Browserbase session runner

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
