# Taxicab Goal State

Last updated: 2026-06-13 PDT.

## Goal

```text
HTML Phase 1: complete, target hit.
PDF Phase 2: active, target >=95% good_pdf on pdf_expected_total.
Stretch target: >=98% good_pdf after the 95% gate is stable.
```

## Active Repositories

```text
Taxicab implementation:
  /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab

Do not use:
  /Users/shubh-trips/Documents/openalex-taxicab

Oxjobs reports:
  /Users/shubh-trips/Documents/OpenAlex/oxjobs

HTML report/control:
  /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit

PDF report/control:
  /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf
  job #461
```

## Current Gate

```text
Gate 0: HTML Phase 1 main sync.
Status: complete.
Commit: 07c974e taxicab: sync phase 1 eval context
Pushed: origin/main

Gate 1: Taxicab PDF branch.
Status: in progress.
Branch: codex/taxicab-pdf-phase2
Current phase: Gate 17, Elsevier route/support clustering. In progress.
Next exact command: cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab && git switch codex/taxicab-pdf-phase2 && python3 -m unittest tests.test_pdf_eval_harness
```

After Gate 0 is pushed:

```text
Gate 1: create codex/taxicab-pdf-phase2 from current origin/main. [done]
Gate 2: create new auto-ID oxjobs taxicab-pdf job and report scaffold. [done, #461]
Gate 3: implement PDF harness, offline validator tests, and live smoke. [done]
Gate 4: run PDF limit-100 and full 10K baseline on the Goldie corpus. [done]
Gate 5: publish full baseline to oxjobs #461. [done]
Gate 6: enrich PDF-expected denominator. [done]
Gate 7: publish denominator-enriched baseline to oxjobs #461. [done]
Gate 8: add gated PDF reharvest mode. [done]
Gate 9: add reharvest POST-context instrumentation. [done]
Gate 10: create Springer Zyte support/evidence packet. [done]
Gate 11: add PDF Browserbase evidence mode. [done]
Gate 12: add PDF row-timeout watchdog for slow PDF/CDN rows. [done]
Gate 13: Elsevier missing-PDF bounded sample. [done]
Gate 14: confirm recovered Elsevier PDFs with read-only follow-up. [done]
Gate 15: generate and run Elsevier 100-row queue. [done]
Gate 16: correct first-page/preview PDF classifier. [done]
Gate 17: publish corrected Elsevier 100-row gate to oxjobs #461. [done, oxjobs 3d8a5fa0]
Gate 18: split Elsevier into ScienceDirect, Lancet, Cell, direct-asset, router, corrupt/truncated, and Zyte-support clusters. [done, oxjobs 825c2e2d]
Gate 19: run ScienceDirect no-storage route probe and create Zyte packet. [done, taxicab 741e9a7, oxjobs 666d0ed6]
Gate 20: run Lancet no-storage route probe and create Zyte packet. [done, oxjobs 2105c8f1]
Gate 21: run Cell Press no-storage route probe and create Zyte packet. [done, oxjobs a160ec1a]
Gate 22: push verified PDF production changes to Taxicab main after >=95% gate and full regression proof.
```

## Latest Accepted Metrics

```text
HTML accepted full gate:
  run_id: full10k-mdpi-jbc-preprints-clean-e22b60e
  good_html: 9,583 / 10,000
  good_html_rate: 95.83%
  rows_above_95: 83
  latest lift: +135 good_html rows
  regressions: 0 good-to-non-good
  taxicab_error: 0
  timeout: 0

Recovered in latest gate:
  MDPI: +119
  Elsevier/JBC: +8
  Rxiv/Preprints: +8

PDF:
  full 10K baseline: 2,148/10,000 good_pdf (21.48%)
  denominator-enriched full baseline: 1,837/6,293 good_pdf (29.19%)
  no_pdf_expected: 3,707
  denominator-enriched gap to 95%: 4,142 rows
  gap to 95%: 7,352 rows
  dominant category: 7,230 missing_pdf_harvest
  other major categories: 453 corrupt_or_truncated_pdf; 121 encrypted_or_unreadable_pdf
  timeout: 0
  taxicab_error: 0
  run_id: pdf-full10k-readonly-22b78b7
  denominator run_id: pdf-full10k-denominator-3f7cd47
  denominator-enriched limit-100: 13/65 good_pdf (20.00%); 35 no_pdf_expected
  reharvest smoke: pdf-reharvest-smoke-8193c47, 0/5 good_pdf; 3 corrupt_or_truncated_pdf; 2 missing_pdf_harvest; 0 timeout; 0 taxicab_error
  springer seed reharvest: pdf-springer-missing-reharvest-12, 1/12 good_pdf; 11 missing_pdf_harvest; 0 timeout; 0 taxicab_error
  springer post-context reharvest: pdf-springer-missing-reharvest-12-post-context-b9d5918, 1/12 good_pdf; 11 missing_pdf_harvest; all 11 missing rows have POST status 201, post content_type html, and resolved Springer article/chapter/rwe HTML URLs
  springer no-storage Zyte two-step probe: failed sample still returned HTML, not PDF; treat as Zyte support candidate before production code changes
  browserbase credential source: ignored /Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/.env contains BROWSERBASE_API_KEY; Taxicab .env/.env.aws do not
  browserbase evidence commit: f424129 taxicab: add pdf browserbase evidence mode
  springer browserbase smoke: pdf-browserbase-springer-1-f424129, verdict html_not_pdf for 10.1007/978-1-4419-6247-8_15015; final URL https://link.springer.com/rwe/10.1007/978-1-4419-6247-8_15015; content_type text/html; not PDF
  row-timeout watchdog commit: be2f5c7 taxicab: add pdf row timeout watchdog
  elsevier missing queue: 25 true missing_pdf_harvest rows generated from pdf-full10k-denominator-3f7cd47
  elsevier interrupted sample: 23/25 rows completed before KeyboardInterrupt; 4 good_pdf, 6 corrupt_or_truncated_pdf, 13 missing_pdf_harvest, 0 timeout/taxicab_error among completed rows
  elsevier bounded sample: pdf-elsevier-missing-reharvest-25-84b2c05 resumed with --row-timeout 120; 4/25 good_pdf, 15 missing_pdf_harvest, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  elsevier read-only confirmation: pdf-elsevier-missing-readonly-after-reharvest-be2f5c7, 4/25 good_pdf, 21 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  elsevier note: the four recovered rows are durable sample records; this is not a full-10K KPI lift until a full gate
  elsevier 100-row reharvest: pdf-elsevier-missing-reharvest-100-41d0378, 6/100 good_pdf, 48 missing_pdf_harvest, 45 corrupt_or_truncated_pdf, 1 timeout, 0 taxicab_error
  elsevier 100-row corrected read-only: pdf-elsevier-missing-readonly-previewfix-9b7d84b, 7/100 good_pdf, 92 missing_pdf_harvest, 1 supplement_or_preview_pdf, 0 timeout, 0 taxicab_error
  preview classifier fix: first-page-pdf URLs classify as supplement_or_preview_pdf, not good_pdf
  oxjobs #461 commit: 3d8a5fa0 #461 taxicab-pdf: publish elsevier 100 gate
  oxjobs #461 route split commit: 825c2e2d #461 taxicab-pdf: add elsevier route split
  elsevier route split: 34 ScienceDirect route rows, 23 journal-host/long-tail rows, 11 invalid-PDF POST rows, 8 Lancet rows, 7 durable recoveries, 5 cross-publisher candidates, 4 DOI-router candidates, 4 direct-asset rows, 3 Cell Press rows, 1 preview row
  sciencedirect probe commit: 741e9a7 taxicab: add sciencedirect pdf probe
  sciencedirect probe run: sciencedirect-route-probe-3-741e9a7, 3 DOI candidates, 12 variants, 0 good_pdf, best category html_instead_of_pdf for 3/3
  oxjobs #461 sciencedirect probe commit: 666d0ed6 #461 taxicab-pdf: record sciencedirect probe
  lancet probe run: lancet-route-probe-3-741e9a7, 3 DOI candidates, 3 variants, 0 good_pdf, 2 empty_response, 1 download_404
  oxjobs #461 lancet probe commit: 2105c8f1 #461 taxicab-pdf: record lancet probe
  cell probe run: cell-route-probe-3-741e9a7, 3 DOI candidates, 3 variants, 0 good_pdf, 3 js_redirect_unresolved
  oxjobs #461 cell probe commit: a160ec1a #461 taxicab-pdf: record cell probe
  offline fixture smoke: 15 categories represented
  live smoke: 1/5 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf
  live smoke after EOF/concurrent runner: 3/5 good_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  limit-100 initial: 1/100 good_pdf, 77 missing_pdf_harvest, 19 corrupt_or_truncated_pdf, 2 encrypted_or_unreadable_pdf, 1 bot_block_403
  limit-100 corrected after EOF validator fix: 15/100 good_pdf, 77 missing_pdf_harvest, 5 corrupt_or_truncated_pdf, 2 encrypted_or_unreadable_pdf, 1 bot_block_403
  note: the 1/100 -> 15/100 lift is measurement/validator correctness, not production scraping behavior.
  target denominator: pdf_expected_total
```

## Required Commit Loop

Every meaningful slice must use this loop:

```bash
git status --short
# make scoped changes
# run focused tests/checks
git add <owned files>
git commit -m "<specific message>"
git pull --rebase
git push
```

Taxicab production behavior changes require targeted eval plus full no-regression
proof before pushing to `main`.

Oxjobs uses `main` as the reporting source of truth. Push report/docs changes
to oxjobs `main` frequently after checks.

## Last Verification

```text
Taxicab main-sync commit: 07c974e
python3 -m unittest discover -s tests: 54 tests passed
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke: passed, 20 fixtures, 11 categories
python3 scripts/taxicab_eval.py --smoke --out /tmp/taxicab-html-main-sync-smoke: passed, 8 rows, 0 timeout, 0 taxicab_error
git diff --cached --check: passed
secret pattern scan: no raw secret pattern findings

PDF harness setup:
python3 -m unittest discover -s tests: 62 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke: passed, 15 fixtures, 15 categories
git diff --check: passed
secret pattern scan: no raw secret pattern findings

PDF read-only live smoke:
python3 -m unittest discover -s tests: 64 tests passed
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --run-id pdf-live-smoke --out /tmp/taxicab-pdf-live-smoke --timeout 30 --retries 1 --progress-every 1: passed
result: 5 rows; 1 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error

PDF limit-100 read-only baseline:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out pdf_eval_runs/ --run-id pdf-limit100-readonly-6661cde --timeout 45 --retries 1 --progress-every 10: passed
result: 1/100 good_pdf; 77 missing_pdf_harvest; 19 corrupt_or_truncated_pdf; 2 encrypted_or_unreadable_pdf; 1 bot_block_403; 0 timeout; 0 taxicab_error

PDF EOF validator correction:
python3 -m unittest tests.test_pdf_eval_harness: 11 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-eof --out /tmp/taxicab-pdf-fixture-smoke-eof: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out pdf_eval_runs/ --run-id pdf-limit100-readonly-eof-fix --timeout 45 --retries 1 --progress-every 10: passed
result: 15/100 good_pdf; 77 missing_pdf_harvest; 5 corrupt_or_truncated_pdf; 2 encrypted_or_unreadable_pdf; 1 bot_block_403; 0 timeout; 0 taxicab_error

PDF concurrent read-only runner:
python3 -m unittest discover -s tests: 66 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-workers --out /tmp/taxicab-pdf-fixture-smoke-workers: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --run-id pdf-live-smoke-workers-358111f --out /tmp/taxicab-pdf-live-smoke-workers --timeout 30 --retries 1 --workers 4 --progress-every 1: passed
result: 5 rows; 3 good_pdf; 2 missing_pdf_harvest; 0 timeout; 0 taxicab_error

PDF full 10K read-only baseline:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --out pdf_eval_runs/ --run-id pdf-full10k-readonly-22b78b7 --workers 8 --timeout 45 --retries 1 --progress-every 100: passed
result: 2,148/10,000 good_pdf (21.48%); 7,230 missing_pdf_harvest; 453 corrupt_or_truncated_pdf; 121 encrypted_or_unreadable_pdf; 13 html_instead_of_pdf; 13 js_redirect_unresolved; 11 supplement_or_preview_pdf; 9 interstitial_or_paywall; 2 bot_block_403; 0 timeout; 0 taxicab_error

PDF denominator enrichment:
python3 -m unittest discover -s tests: 68 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-denominator --out /tmp/taxicab-pdf-fixture-smoke-denominator: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out pdf_eval_runs/ --run-id pdf-limit100-denominator --workers 8 --timeout 45 --retries 1 --progress-every 10: passed
result: pdf_expected_total 65; 13 good_pdf; 35 no_pdf_expected; 45 missing_pdf_harvest; 5 corrupt_or_truncated_pdf; 1 encrypted_or_unreadable_pdf; 1 bot_block_403; 0 timeout; 0 taxicab_error

PDF denominator-enriched full 10K baseline:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --out pdf_eval_runs/ --run-id pdf-full10k-denominator-3f7cd47 --workers 8 --timeout 45 --retries 1 --progress-every 100: passed
result: 1,837/6,293 good_pdf (29.19%); 3,707 no_pdf_expected; 3,939 missing_pdf_harvest; 373 corrupt_or_truncated_pdf; 102 encrypted_or_unreadable_pdf; 11 html_instead_of_pdf; 11 js_redirect_unresolved; 10 supplement_or_preview_pdf; 8 interstitial_or_paywall; 2 bot_block_403; 0 timeout; 0 taxicab_error

PDF reharvest mode:
python3 -m unittest discover -s tests: 69 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-reharvest --out /tmp/taxicab-pdf-fixture-smoke-reharvest: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 5 --reharvest --workers 2 --out /tmp/taxicab-pdf-reharvest-smoke --run-id pdf-reharvest-smoke-5 --timeout 45 --retries 1 --progress-every 1: passed
result: 0/5 good_pdf; 3 corrupt_or_truncated_pdf from Taxicab invalid-PDF POST responses; 2 missing_pdf_harvest after read-back; 0 timeout; 0 taxicab_error

PDF Springer seed queue:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv --reharvest --workers 2 --out pdf_eval_runs/ --run-id pdf-springer-missing-reharvest-12 --timeout 60 --retries 1 --progress-every 1: passed
result: 1/12 good_pdf; 11 missing_pdf_harvest; recovered DOI 10.1007/bf03544238; 0 timeout; 0 taxicab_error

PDF reharvest POST-context instrumentation:
python3 -m unittest tests.test_pdf_eval_harness: 16 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-post-context --out /tmp/taxicab-pdf-fixture-smoke-post-context: passed, 15 fixtures, 15 categories
python3 -m unittest discover -s tests: 70 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-post-context-final --out /tmp/taxicab-pdf-fixture-smoke-post-context-final: passed, 15 fixtures, 15 categories
git diff --check: passed
secret pattern scan: no raw secret pattern findings

PDF Springer post-context seed rerun:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv --reharvest --workers 2 --out pdf_eval_runs/ --run-id pdf-springer-missing-reharvest-12-post-context-b9d5918 --timeout 60 --retries 1 --progress-every 1: passed
result: 1/12 good_pdf; 11 missing_pdf_harvest; 11/11 misses had POST status 201 and post content_type html

PDF Browserbase evidence mode:
python3 -m unittest tests.test_pdf_eval_harness: 17 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-browserbase-mode --out /tmp/taxicab-pdf-fixture-smoke-browserbase-mode: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv --limit 1 --with-browserbase --browserbase-mode session --browserbase-timeout 60 --out pdf_eval_runs/ --run-id pdf-browserbase-springer-1-f424129 --timeout 30 --retries 1 --progress-every 1: passed with ignored Parseland env Browserbase key
result: Browserbase verdict html_not_pdf; browserbase_available false; final URL was Springer RWE HTML page, not PDF

PDF row-timeout watchdog:
python3 -m unittest tests.test_pdf_eval_harness: 18 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-row-timeout --out /tmp/taxicab-pdf-fixture-smoke-row-timeout: passed, 15 fixtures, 15 categories
python3 -m unittest discover -s tests: 72 tests passed
git diff --check: passed
secret pattern scan: no raw secret pattern findings

PDF Elsevier bounded missing sample:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-25.csv --reharvest --workers 2 --row-timeout 120 --resume --out pdf_eval_runs/ --run-id pdf-elsevier-missing-reharvest-25-84b2c05 --timeout 60 --retries 1 --progress-every 1: passed
result: 4/25 good_pdf; 15 missing_pdf_harvest; 6 corrupt_or_truncated_pdf; 0 timeout; 0 taxicab_error

PDF Elsevier read-only confirmation:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-25.csv --out pdf_eval_runs/ --run-id pdf-elsevier-missing-readonly-after-reharvest-be2f5c7 --workers 4 --row-timeout 120 --timeout 60 --retries 1 --progress-every 1: passed
result: 4/25 good_pdf; 21 missing_pdf_harvest; 0 timeout; 0 taxicab_error

PDF preview URL classifier:
python3 -m unittest tests.test_pdf_eval_harness: 19 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-preview-url --out /tmp/taxicab-pdf-fixture-smoke-preview-url: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-100.csv --out pdf_eval_runs/ --run-id pdf-elsevier-missing-readonly-previewfix-9b7d84b --workers 4 --row-timeout 120 --timeout 60 --retries 1 --progress-every 10: passed
result: 7/100 good_pdf; 92 missing_pdf_harvest; 1 supplement_or_preview_pdf; 0 timeout; 0 taxicab_error
```

## Provider Policy

```text
Zyte:
  production retrieval core.

Browserbase:
  evidence, recoverability checks, and gold-sample collection only.
  not a production fallback unless explicitly approved later.

Secrets:
  never print or commit key/token/cookie values.
  local ignored .env and .env.aws can be loaded without echoing values.
```

## Do Not

```text
Do not use /Users/shubh-trips/Documents/openalex-taxicab.
Do not mix HTML and PDF KPIs.
Do not put PDF Phase 2 results into #133 as the primary report.
Do not use Browserbase as production fallback.
Do not print secrets, signed URLs, cookies, or decrypted AWS secret values.
Do not push broad production scraping changes without full regression proof.
```
