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
  pending creation via scripts/create-job.py
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
Next exact command: cd /Users/shubh-trips/Documents/OpenAlex/oxjobs && git pull --rebase
```

After Gate 0 is pushed:

```text
Gate 1: create codex/taxicab-pdf-phase2 from current origin/main. [done]
Gate 2: create new auto-ID oxjobs taxicab-pdf job and report scaffold.
Gate 3: implement PDF harness and offline validator tests.
Gate 4: run PDF baseline on the 10K Goldie corpus.
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
  baseline pending
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
