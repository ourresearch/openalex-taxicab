# OpenAlex Taxicab

Academic content harvesting API. Fetches HTML and PDFs from publisher websites via Zyte API, stores in Cloudflare R2 + DynamoDB.

## Project Structure

- `app.py` - Flask REST API endpoints
- `openalex_taxicab/harvest.py` - Core harvesting logic, soft-block detection, S3/DynamoDB storage
- `openalex_taxicab/http_cache.py` - HTTP requests via Zyte API, DOI resolution, publisher-specific handling
- `openalex_taxicab/util.py` - Utility functions (MIME type detection, timing)

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
