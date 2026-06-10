# Taxicab Codebase Understanding

## Service Overview

Taxicab is OpenAlex's harvesting service for publisher landing-page HTML, PDFs, and Grobid XML. The Flask API in `app.py` wraps a `Harvester` from `openalex_taxicab/harvest.py`, stores content in Cloudflare R2, and indexes records in DynamoDB. `openalex_taxicab/http_cache.py` owns DOI redirect resolution, direct-fetch exceptions, Zyte API calls, browserHtml routing, publisher-specific Zyte actions, and DSpace 7 synthetic HTML.

`main` deploys automatically to ECS through `.github/workflows/aws.yml`. The workflow builds a Docker image, pushes it to ECR repository `harvester`, registers a new `harvest-task` task definition, and updates ECS service `harvester-service` in cluster `harvester`.

## Endpoint Inventory

- `GET /`: returns table counts and recent HTML/PDF/Grobid samples from DynamoDB.
- `POST /taxicab`: requires `native_id`, `native_id_namespace`, and `url`; fetches content through `Harvester.harvest`, stores valid non-blocked content, and returns harvest metadata.
- `GET /test-zyte?url=...`: calls `http_get` and returns status, resolved URL, preview, and guessed content type.
- `GET /taxicab/doi/<doi>`: queries DynamoDB by normalized DOI and returns `html`, `pdf`, and `grobid` record lists.
- `GET /taxicab/pmh/<pmh_id>`: queries by PMH native ID.
- `GET /taxicab/<uuid>`: probes current R2 buckets for HTML/PDF/XML by UUID, then falls back to legacy S3 HTML, returning 404 when metadata points to no available object.

## Read Path

`GET /taxicab/doi/<doi>` calls `Harvester.fetch_by_doi`, which normalizes the DOI and queries the `by_normalized_doi` GSI across `harvested-html`, `harvested-pdf`, and `grobid-xml`. Each item becomes a response dict with ID, original URL, resolved URL, native ID, download URL, S3 path, version, and created date.

`GET /taxicab/<uuid>` does not query DynamoDB. It probes R2 keys under `openalex-html`, `openalex-pdfs`, and `openalex-grobid-xml`, then probes legacy AWS S3 bucket `openalex-harvested-html`. HTML and XML are server-side gunzipped before being returned.

The eval harness uses this read path in default mode. It deliberately avoids importing `app.py` and talks to the deployed HTTP API instead.

## Write Path

`POST /taxicab` calls `Harvester.harvest`, which:

1. Generates a UUID.
2. Calls `http_get(url, ask_slowly=True)`.
3. Classifies content with `guess_mime_type`.
4. Runs `_check_soft_block` for non-PDF content.
5. Rejects invalid PDFs and unknown content types.
6. Stores only HTTP 200, non-empty, non-soft-blocked content.
7. Writes compressed HTML or raw PDF to R2 and metadata to DynamoDB.

Stored DynamoDB items include ID, URL, native ID, namespace, normalized DOI, resolved URL, S3 key/path, and created date. They do not persist the upstream HTTP status code, so the eval classifier must infer many failure modes from Taxicab responses and content.

## Zyte, Direct Fetch, and Browser HTML

`http_cache.py` handles all network retrieval strategy:

- `DIRECT_FETCH_URLS` bypasses Zyte for selected open repositories and DSpace-like hosts.
- `BROWSER_HTML_URLS` enables Zyte `browserHtml=True` and `javascript=True` for selected JS-heavy publishers.
- DOI/handle URLs are resolved before Zyte fetch when possible.
- Crossref chooser pages are detected and followed.
- DSpace 7 bare Angular shells can be replaced with synthetic citation-meta HTML using the DSpace REST API.
- Some publishers use explicit Zyte actions, cookies, selector waits, or click/evaluate steps.

Zyte remains the production core. Browserbase evidence in Taxicab V1 is report-only unless a later production fallback is explicitly designed and regression-tested.

## Known Failure Classes

- Missing harvest: DOI lookup returns no HTML/PDF/Grobid records.
- R2/DynamoDB mismatch: DOI lookup returns a UUID but UUID download returns 404.
- Bot block: captcha, access denied, WAF, ShieldSquare, Akamai, Cloudflare challenge, APA PsycNet, or similar page.
- Timeout: API lookup, UUID download, reharvest POST, or evidence fetch exceeds retry budget.
- Empty/tiny response: content is blank or too small to be article HTML.
- JS required: empty SPA shell or page asks the user to enable JavaScript.
- Router only: DOI.org, Crossref chooser, meta refresh, or publisher router page without article content.
- PDF instead of HTML: PDF content returned when landing-page HTML was expected.
- Invalid content: binary or unsupported non-HTML/non-PDF payload.
- Taxicab error: non-200 service response, bad JSON, unexpected response shape, or unclassified service failure.

## Eval Harness Boundaries

Default eval mode is read-only and uses only `GET /taxicab/doi/<doi>` plus `GET /taxicab/<uuid>`. `--reharvest` is opt-in and is the only mode that issues `POST /taxicab`. Browserbase mode records evidence beside the Taxicab verdict and never changes the baseline category.
