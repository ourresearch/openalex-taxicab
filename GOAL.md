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
Next exact command: python3 -m unittest discover -s tests
```

After Gate 0 is pushed:

```text
Gate 1: create codex/taxicab-pdf-phase2 from current origin/main. [done]
Gate 2: create new auto-ID oxjobs taxicab-pdf job and report scaffold. [done, #461]
Gate 3: implement PDF harness, offline validator tests, and live smoke. [done]
Gate 4: run PDF limit-100 and full 10K baseline on the Goldie corpus. [limit-100 corrected; full 10K next]
Gate 5: run PDF improvement loop until >=95% good_pdf.
Gate 6: push verified PDF production changes to Taxicab main.
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
  full 10K baseline pending
  offline fixture smoke: 15 categories represented
  live smoke: 1/5 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf
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
