# OpenAlex Taxicab Agent Guide

Current goal state: HTML Phase 1 is complete at 9,583/10,000 `good_html`
(95.83%). PDF Phase 2 is active and targets >=95% `good_pdf` on the
PDF-expected portion of the 10K Goldie corpus. Read `GOAL.md` and
`NEXT_TO_DO.md` before changing code.

Latest PDF metric: after the EOF-validator correction, the limit-100 read-only
gate is 15/100 `good_pdf`, 77 `missing_pdf_harvest`, 5
`corrupt_or_truncated_pdf`, two `encrypted_or_unreadable_pdf`, one
`bot_block_403`, and 0 `timeout` / 0 `taxicab_error`. This is measurement
correctness, not production scraping lift.

## Repository

- Use `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- Use `main` only for verified deployable state. Use `codex/taxicab-pdf-phase2` for PDF Phase 2 once the HTML Phase 1 main-sync commit is pushed.
- Preserve unrelated local changes.
- Read `NEXT_TO_DO.md` before choosing a cluster. It is the handoff contract for Codex/Claude continuity.

## Production Safety

- Pushing `main` deploys to ECS through `.github/workflows/aws.yml`.
- Eval harness, tests, docs, and reports are safe setup work.
- Production scraping behavior changes need targeted eval plus no-regression proof before push.
- Do not import `app.py` from eval code or tests; it creates R2 clients at import time.
- Commit and push frequently after focused checks. The required loop is:
  `git status --short`, scoped changes, focused tests, `git add`, `git commit`,
  `git pull --rebase`, `git push`.

## Providers

- Zyte is the production core.
- Browserbase is evidence/recoverability/gold-sample collection unless explicitly promoted later.
- Confirmed Zyte gaps should become reproducible support packets with DOI, URL, category, evidence snippet, and Browserbase comparison when available.

## Secrets

- Never print or commit secret values.
- Load local ignored `.env` / `.env.aws` first for provider, R2, Zyte, and AWS CLI-style variables. Do not ask Shubh to re-auth unless those files are missing or a safe AWS command proves the local session is expired.
- AWS CLI may be used for discovery, but do not echo decrypted Secrets Manager or SSM values.
- Secret variable names can appear in docs and `.env.example`; raw values cannot.

## Verification

Run these before committing eval-system changes:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
rg -n "ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY" .
```

The broad scan above intentionally finds variable names in docs and code.
Inspect matches and reject raw values, tokens, cookies, or signed provider URLs.

For live read-only smoke:

```bash
python3 scripts/taxicab_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --smoke \
  --out /tmp/taxicab-live-smoke
```

For a limited baseline:

```bash
python3 scripts/taxicab_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --limit 100 \
  --out eval_runs/
```

For PDF Phase 2:

```bash
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke
python3 scripts/taxicab_pdf_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --smoke \
  --out /tmp/taxicab-pdf-live-smoke
python3 scripts/taxicab_pdf_eval.py \
  --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com \
  --out pdf_eval_runs/ \
  --workers 8
```

For explicit low-concurrency reharvest samples, bound each row with
`--row-timeout` so a pathological Taxicab/Zyte request records `timeout`
instead of holding the whole run open:

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

For Browserbase evidence mode, the harness uses Browserbase REST plus Playwright. The local Browserbase Python SDK is intentionally not required because SDK import hung in this environment.

```bash
python3 -m playwright --version
python3 scripts/taxicab_eval.py --with-browserbase --browserbase-mode session ...
```

Current Browserbase state: Browserbase REST session create/release is healthy. Local Playwright startup now passes, and the expanded 10-row MDPI Browserbase session run completed under `--row-timeout 150`.

## Reporting

- oxjobs control surface: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`.
- PDF Phase 2 uses oxjobs #461 `taxicab-pdf` with its own report surface at `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf`.
- Keep Taxicab retrieval KPIs separate from Parseland extraction KPIs.
- Keep HTML and PDF Taxicab KPIs separate. Report `good_html_rate` for #133 and `good_pdf_rate` for the new PDF job.
