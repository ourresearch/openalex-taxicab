# OpenAlex Taxicab

Academic content harvesting API. Fetches HTML and PDFs from publisher websites via Zyte API, stores in Cloudflare R2 + DynamoDB.

## Agent Operating Rules

- Active repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- `main` auto-deploys to ECS through `.github/workflows/aws.yml`. Work on a `codex/` branch and push only after focused verification.
- Never print or commit secret values. Secret names may appear in docs, but raw values for `ZYTE_API_KEY`, `BROWSERBASE_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `R2_SECRET_ACCESS_KEY`, and `CRAWLERA_KEY` must stay out of tracked files and reports.
- Zyte remains the production retrieval core. Browserbase is evidence/recoverability unless a later, separately tested production fallback is approved.
- Taxicab V1 reporting lives in `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit` (#133). #336 is Parseland-only.
- Evaluation code must not import `app.py`; Flask app import requires R2 credentials at import time.
- Before continuing the improvement loop, read `NEXT_TO_DO.md` in this repo and in oxjobs `working/taxicab-audit/NEXT_TO_DO.md`.

## Taxicab V1 Eval Commands

```bash
python3 -m unittest discover -s tests
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke
python3 scripts/taxicab_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --out /tmp/taxicab-live-smoke
python3 scripts/taxicab_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out eval_runs/
```

For live reharvest samples, prefer a per-row watchdog:

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

Optional Browserbase evidence mode uses Browserbase REST plus Playwright. The local Browserbase Python SDK is no longer required for `scripts/taxicab_eval.py` because SDK import hung in this environment.

```bash
python3 -m playwright --version
python3 scripts/taxicab_eval.py --with-browserbase --browserbase-mode session ...
```

Known current Browserbase state: REST session create/release works with the ignored Parseland eval env key, but local Playwright startup/CDP connection hung during the expanded MDPI sample. See `NEXT_TO_DO.md` before spending more Browserbase time.

Before push, run a secret scan:

```bash
rg -n "ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY" .
```

Inspect matches before committing; variable names are OK, secret values and signed provider URLs are not.

## Project Structure

- `app.py` - Flask REST API endpoints
- `openalex_taxicab/harvest.py` - Core harvesting logic, soft-block detection, S3/DynamoDB storage
- `openalex_taxicab/http_cache.py` - HTTP requests via Zyte API, DOI resolution, publisher-specific handling
- `openalex_taxicab/eval_harness.py` - Taxicab V1 retrieval-quality classifier and artifact writer
- `openalex_taxicab/publisher_index.py` - DOI-prefix/domain publisher classifier, vendored from Parseland
- `openalex_taxicab/util.py` - Utility functions (MIME type detection, timing)
- `scripts/taxicab_eval.py` - Read-only/reharvest eval CLI

## Testing Locally

Uses `.venv` and `.env` (no `python-dotenv` installed, load env vars manually).

### Test a URL fetch + soft-block check

```bash
.venv/bin/python -c "
import os
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip()

from openalex_taxicab.http_cache import http_get
from openalex_taxicab.harvest import Harvester
import re

url = 'http://dx.doi.org/10.1088/0256-307x/40/10/100401'
response = http_get(url)
print('Status code:', response.status_code)
print('Resolved URL:', response.url)

content = response.content if isinstance(response.content, str) else response.content.decode('utf-8', 'ignore')
print('Content length:', len(content))

h = Harvester.__new__(Harvester)
is_soft_block = h._check_soft_block(content.encode('utf-8') if isinstance(content, str) else content)
print('Is soft block:', is_soft_block)

title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
if title_match:
    print('Page title:', title_match.group(1).strip())
"
```

### Test DOI redirect resolution only

```bash
.venv/bin/python -c "
import os
with open('.env') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            os.environ[key.strip()] = val.strip()

from openalex_taxicab.http_cache import resolve_doi_redirects

result = resolve_doi_redirects('https://doi.org/10.1088/0256-307x/40/10/100401')
print('Final URL:', result['final_url'])
print('Chain:', ' -> '.join(result['redirect_chain']))
"
```

## Key Concepts

- **BROWSER_HTML_URLS**: Domains requiring Zyte browser rendering (`browserHtml=True` + `javascript=True`). Add domains here when a publisher uses JS-based bot protection.
- **BOT_PROTECTION_DOMAINS**: Known bot protection services (e.g. `perfdrive.com`). DOI redirect resolution walks back the chain if it lands on one of these.
- **Soft blocks**: Pages that return HTTP 200 but contain captcha/verification content. Detected by pattern matching in `Harvester._check_soft_block()`.
- **Publisher-specific handling**: Some publishers need special Zyte params (cookies, JS actions, waitForSelector). See `http_get()` and `call_with_zyte_api()` in `http_cache.py`.
