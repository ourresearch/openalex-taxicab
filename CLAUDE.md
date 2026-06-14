# OpenAlex Taxicab

Academic content harvesting API. Fetches HTML and PDFs from publisher websites via Zyte API, stores in Cloudflare R2 + DynamoDB.

Current goal state: HTML retrieval Phase 1 is complete at 9,583/10,000
`good_html` (95.83%). PDF retrieval Phase 2 is active and targets >=95%
`good_pdf` on the PDF-expected subset of the 10K Goldie corpus. Use
`GOAL.md` as the current control file and update it before long handoffs.
Latest PDF measurement gate: denominator-enriched full 10K read-only baseline
is 1,837/6,293 `good_pdf` (29.19%), with 3,707 `no_pdf_expected`, 3,939
`missing_pdf_harvest`, 373 `corrupt_or_truncated_pdf`, 102
`encrypted_or_unreadable_pdf`, 0 timeout, and 0 Taxicab API errors.
Gated PDF reharvest mode is pushed at `8193c47`; the first committed smoke
recovered 0/5. The Springer seed queue from oxjobs #461 recovered 1/12
(`10.1007/bf03544238`) and left 11 missing. Reharvest post-context
instrumentation is pushed at `b9d5918`; the rerun shows the 11 remaining
Springer misses were POST 201 HTML captures, not PDF records. A no-storage
two-step Zyte probe also returned HTML for a failed sample, so prepare/support
packet evidence before changing production routing.
PDF Browserbase evidence mode is pushed at `f424129`: it annotates non-good PDF rows
separately from the Taxicab verdict. The first Springer Browserbase session
smoke returned `html_not_pdf`, not a recoverable PDF.
PDF row-timeout watchdog is pushed at `be2f5c7`. Use `--row-timeout` before
scaling reharvest samples. The resumed Elsevier true-missing sample finished
with 4/25 `good_pdf`, 15 `missing_pdf_harvest`, 6 `corrupt_or_truncated_pdf`,
0 timeout, and 0 Taxicab errors. Treat this as localized sample evidence until
full 10K gate proof. Read-only confirmation
`pdf-elsevier-missing-readonly-after-reharvest-be2f5c7` preserved the same four
`good_pdf` rows and left 21 rows missing, with 0 timeout and 0 Taxicab errors.
The 100-row Elsevier run exposed an eval bug: a ScienceDirect `first-page-pdf`
preview was counted as `good_pdf`. Current branch code classifies first-page or
preview PDF URLs as `supplement_or_preview_pdf`. Corrected Elsevier 100-row
read-only result: 7/100 `good_pdf`, 92 missing, one preview, 0 timeout, and
0 Taxicab errors.

## Agent Operating Rules

- Active repo: `/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab`.
- Do not use `/Users/shubh-trips/Documents/openalex-taxicab`; it is an empty duplicate checkout.
- `main` auto-deploys to ECS through `.github/workflows/aws.yml`. Work on a `codex/` branch and push only after focused verification.
- For PDF Phase 2, use `codex/taxicab-pdf-phase2` after the HTML Phase 1 main-sync commit is on `main`.
- Never print or commit secret values. Secret names may appear in docs, but raw values for `ZYTE_API_KEY`, `BROWSERBASE_API_KEY`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`, `R2_SECRET_ACCESS_KEY`, and `CRAWLERA_KEY` must stay out of tracked files and reports.
- Use the local ignored credential files before asking Shubh to authenticate. `.env` contains Taxicab provider/R2/Zyte material, and `.env.aws` contains AWS CLI-style session variables. Load them into process environment without echoing values; ask for auth only if the files are missing or a safe command proves the session is expired.
- Zyte remains the production retrieval core. Browserbase is evidence/recoverability unless a later, separately tested production fallback is approved.
- Taxicab V1 reporting lives in `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit` (#133). #336 is Parseland-only.
- PDF Phase 2 gets a separate auto-ID oxjob named `taxicab-pdf`; do not mix PDF KPIs into #133's HTML target.
- Evaluation code must not import `app.py`; Flask app import requires R2 credentials at import time.
- Before continuing the improvement loop, read `NEXT_TO_DO.md` in this repo and in oxjobs `working/taxicab-audit/NEXT_TO_DO.md`.
- Commit and push frequently after focused checks: `git status --short`, tests,
  `git add`, `git commit`, `git pull --rebase`, `git push`.

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

Known current Browserbase state: REST session create/release works with the ignored Parseland eval env key. Local Playwright startup now passes, and the expanded 10-row MDPI Browserbase session run completed under `--row-timeout 150`. See `NEXT_TO_DO.md` before spending more Browserbase time.

Before push, run a secret scan:

```bash
rg -n "ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY" .
```

Inspect matches before committing; variable names are OK, secret values and signed provider URLs are not.

## Taxicab PDF Phase 2 Eval Commands

```bash
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --out /tmp/taxicab-pdf-live-smoke
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --out pdf_eval_runs/ --workers 8
```

PDF Phase 2 reports live in oxjobs #461 at `/Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf`.

## Project Structure

- `app.py` - Flask REST API endpoints
- `openalex_taxicab/harvest.py` - Core harvesting logic, soft-block detection, S3/DynamoDB storage
- `openalex_taxicab/http_cache.py` - HTTP requests via Zyte API, DOI resolution, publisher-specific handling
- `openalex_taxicab/eval_harness.py` - Taxicab V1 retrieval-quality classifier and artifact writer
- `openalex_taxicab/pdf_eval_harness.py` - Taxicab PDF retrieval-quality classifier and artifact writer
- `openalex_taxicab/publisher_index.py` - DOI-prefix/domain publisher classifier, vendored from Parseland
- `openalex_taxicab/util.py` - Utility functions (MIME type detection, timing)
- `scripts/taxicab_eval.py` - Read-only/reharvest eval CLI
- `scripts/taxicab_pdf_eval.py` - Read-only PDF eval CLI

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
