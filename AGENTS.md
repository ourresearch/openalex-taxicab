# OpenAlex Taxicab Agent Guide

## Repository

- Use `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- Use `codex/taxicab-v1-eval-system` for the Taxicab V1 eval system unless a newer `codex/` branch is already active.
- Preserve unrelated local changes.

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
- AWS CLI may be used for discovery, but do not echo decrypted Secrets Manager or SSM values.
- Secret variable names can appear in docs and `.env.example`; raw values cannot.

## Verification

Run these before committing eval-system changes:

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
rg -n "ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY" .
```

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

## Reporting

- oxjobs control surface: `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit`.
- Keep Taxicab retrieval KPIs separate from Parseland extraction KPIs.
- Report `good_html_rate`, denominator, category counts, publisher/host clusters, support candidates, and next actions.
