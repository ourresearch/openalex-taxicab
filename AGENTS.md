# OpenAlex Taxicab Agent Guide

## Repository

- Use `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- Use `codex/taxicab-v1-eval-system` for the Taxicab V1 eval system unless a newer `codex/` branch is already active.
- Preserve unrelated local changes.
- Read `NEXT_TO_DO.md` before choosing a cluster. It is the handoff contract for Codex/Claude continuity.

## Production Safety

- Pushing `main` deploys to ECS through `.github/workflows/aws.yml`.
- Eval harness, tests, docs, and reports are safe setup work.
- Production scraping behavior changes need targeted eval plus no-regression proof before push.
- Do not import `app.py` from eval code or tests; it creates R2 clients at import time.

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
- Keep Taxicab retrieval KPIs separate from Parseland extraction KPIs.
- Report `good_html_rate`, denominator, category counts, publisher/host clusters, support candidates, and next actions.
