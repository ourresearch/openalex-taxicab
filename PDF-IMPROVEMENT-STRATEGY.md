# Taxicab PDF Improvement Strategy

## Purpose

This file explains the PDF improvement work in simple English.

The goal is not only to classify rows. The goal is to find real cases where a
public PDF exists, Taxicab misses it, and then make Taxicab retrieve and store
the real PDF bytes.

Success means:

```text
DOI lookup shows a pdf record
the Taxicab download URL returns status 200
the stored file starts with %PDF-
the file is not a login page, paywall page, bot page, or HTML shell
```

## Correct Repo

Use this repo:

```text
/Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
```

Do not use this duplicate path:

```text
/Users/shubh-trips/Documents/openalex-taxicab
```

## How Taxicab Works When A DOI Is Given

Taxicab has two different modes.

### Lookup Mode

This checks what Taxicab already has:

```text
GET /taxicab/doi/<doi>
```

It returns stored records:

```text
html: stored article pages
pdf: stored PDF files
grobid: stored parsed records, if any
```

Lookup mode does not fetch a new file. It only reads the database.

### Harvest Mode

This fetches a new URL:

```text
POST /taxicab
```

The request includes:

```json
{
  "native_id": "10.xxxx/yyyy",
  "native_id_namespace": "doi",
  "url": "https://doi.org/10.xxxx/yyyy"
}
```

Taxicab then follows the URL, gets content from the publisher, checks whether it
is real HTML or real PDF, and stores the good file.

### Download Mode

This downloads a stored Taxicab file:

```text
GET /taxicab/<uuid>
```

For PDF work, the important check is:

```text
Does the returned file start with %PDF- ?
```

If yes, Taxicab stored a real PDF. If no, it did not.

## How The Fetching Mechanism Works

When Taxicab harvests a URL, it sends the URL to the main fetch function.

The fetch function decides:

```text
Should Taxicab fetch this directly?
Should Taxicab use Zyte normal body fetch?
Should Taxicab use Zyte browser rendering?
Should Taxicab rewrite this URL first?
Is this a known publisher special case?
```

The main paths are:

```text
direct fetch
Zyte normal fetch
Zyte browser fetch
publisher-specific fetch rule
```

Taxicab follows DOI redirects first when the URL starts with `doi.org`.

Example:

```text
https://doi.org/10.xxxx/yyyy
-> publisher article page
```

Then Taxicab may rewrite known bad URL shapes.

Examples:

```text
ScienceDirect signed PDF asset -> ScienceDirect article page
JBC old LinkingHub/PDF URL -> JBC fulltext page
Elsevier-family PDF viewer shell -> article fulltext page
```

After the fetch, Taxicab checks the response:

```text
HTML page
real PDF bytes
empty response
bot block
login/paywall page
invalid file
```

Only good HTML or real PDF bytes should be stored.

## What Counts As A Real PDF Improvement

A real PDF improvement needs before-and-after proof.

Before:

```text
public PDF exists
Taxicab DOI lookup has no valid pdf record
or Taxicab stores HTML/login/bot content instead of PDF bytes
```

After:

```text
Taxicab DOI lookup has a pdf record
Taxicab download URL returns status 200
downloaded bytes start with %PDF-
the file is not corrupt, empty, or tiny
```

Do not count a URL ending in `.pdf` as success by itself. Many publisher PDF
URLs return login HTML, bot HTML, or viewer HTML. The bytes must prove it.

## What Does Not Count As A PDF Improvement

These are useful, but they are not PDF-byte recoveries:

```text
Taxicab reaches better article HTML
Taxicab reaches a fulltext page but stores no PDF
Taxicab finds a paywall or institution login page
Taxicab finds a PDF viewer shell without PDF bytes
Taxicab confirms no public PDF exists
the file label was wrong and Taxicab was already right
```

Those outcomes should still be recorded, but do not call them PDF retrieval
improvements.

## Current Simple Strategy

Work one publisher group at a time.

1. Find rows where a public PDF should exist but Taxicab has no valid PDF.
2. Group those misses by publisher or host.
3. Pick the biggest group first.
4. For a few examples, inspect:
   - Taxicab DOI lookup
   - latest HTML record
   - latest PDF record, if any
   - publisher page
   - real PDF URL
   - Taxicab download bytes
5. Decide the fix:
   - URL rewrite
   - extract PDF link from HTML
   - use Zyte browser rendering
   - use Zyte normal body fetch
   - use direct fetch for a narrow safe host
   - send a Zyte support packet if Zyte cannot retrieve a public PDF
6. Add one narrow route fix.
7. Reharvest the test DOI.
8. Read Taxicab back by DOI.
9. Download the stored PDF.
10. Confirm the bytes start with `%PDF-`.
11. Run regression checks before claiming the improvement.

## Main Target

Casey's target is practical:

```text
Find the largest publisher groups where public PDFs exist but Taxicab misses them.
Recover enough real PDFs to improve coverage by about 15-20 points.
Then call the Taxicab PDF work done, with remaining blockers documented.
```

This means the main work is not random label cleanup. Label cleanup helps the
score make sense, but the main Taxicab work is real PDF recovery.

## Current Important Example: Gastrojournal

For this DOI:

```text
10.1016/0016-5085(85)90672-9
```

Taxicab can currently reach the useful fulltext page:

```text
https://www.gastrojournal.org/article/0016-5085(85)90672-9/fulltext
```

But the real PDF is:

```text
https://www.gastrojournal.org/action/showPdf?pii=0016-5085%2885%2990672-9
```

The improvement target is:

```text
fulltext page
-> discover or build showPdf?pii=... URL
-> fetch it through the right path
-> verify bytes start with %PDF-
-> store it as a Taxicab PDF record
```

Do not claim this as fixed until Taxicab DOI lookup shows a PDF record and the
Taxicab download URL returns `%PDF-` bytes.

## Known Clear PDF-Byte Recovery Examples

These are examples of the kind of proof required.

### AJESS

DOI:

```text
10.9734/ajess/2023/v47i31023
```

Taxicab recovered a real PDF from `journalajess.com`.

Proof shape:

```text
Taxicab PDF record exists
download status 200
content starts with %PDF-1.5
file size about 677 KB
```

### Erudit

DOI:

```text
10.7202/013935ar
```

Taxicab recovered a real PDF from `erudit.org`.

Proof shape:

```text
Taxicab PDF record exists
download status 200
content starts with %PDF-1.4
file size about 3.7 MB
```

## Interactive Diagnostic Webapp

There is a small local web app for fast DOI checking:

```text
scripts/parseland_webapp.py
```

Run it:

```bash
python3 scripts/parseland_webapp.py
# then open http://localhost:8000
```

Enter a DOI and it runs the full chain for you:

```text
1. POST /taxicab        (optional re-harvest, off by default)
2. GET  /taxicab/doi    -> latest stored scrape UUID
3. GET  /parseland/<uuid> -> parsed landing page
4. extract the candidate PDF URL from Parseland's links
```

It shows the candidate PDF URL, the landing page, the scrape UUID, and every
URL Parseland returned. It is read-only by default: it tells you what link
Parseland found, it does not make Taxicab fetch or store the PDF. Tick the
"Re-harvest first" box only when a DOI has no stored scrape yet, because that
POST costs Zyte credits.

This tool is for triage. The real PDF recovery still goes through the
reharvest-and-confirm loop in "Current Simple Strategy".

### Fix Found While Exploring: Image Previews Were Counted As PDFs

The candidate extractor matched any URL containing `pdf`, `pdfft`, or
`download`. That wrongly accepted preview images.

Example, DOI `10.1253/circj.cj-12-0636` on J-STAGE returned only:

```text
https://www.jstage.jst.go.jp/pub/pdfpreview/circj/76/8_76_CJ-12-0636.jpg
```

The word `pdfpreview` matched, but the file is a `.jpg` thumbnail, not a PDF.

The extractor now drops any URL whose path ends in an image extension
(`.jpg .jpeg .png .gif .webp .svg .tif`). So that DOI now correctly shows zero
PDF candidates instead of a fake one.

This is the kind of small accuracy fix that improves Taxicab over time:
each false candidate we remove stops a wasted fetch and stops a non-PDF from
being treated as a public PDF. The same image-extension guard is now applied in
both `scripts/parseland_webapp.py` and `scripts/taxicab_batch_e2e.py`.

### Important: The Parseland Candidate Is Not What Taxicab Stored

The webapp shows the candidate PDF URL that Parseland extracted from the landing
page. That is a guess from the HTML. It is not proof of what Taxicab actually
fetched and stored. The two can disagree in both directions:

```text
Parseland finds a junk/off-site link, but Taxicab stored the real PDF.
Parseland finds a clean PDF link, but Taxicab stored only HTML.
```

So the candidate URL alone never tells you if the row is good. To know the
truth, byte-check Taxicab's own stored PDF records:

```text
GET /taxicab/doi/<doi>        -> read the pdf record list
GET /taxicab/<pdf_uuid>       -> download the stored bytes
check the bytes start with %PDF-
```

### Real Example: Régiókutatás Szemle (OJS, unideb.hu)

DOI:

```text
10.30716/rsz/21/2/15
```

The webapp candidate looked wrong. Parseland returned only one link, on a
different host than the journal, with an unrelated file number:

```text
landing:    https://ojs.lib.unideb.hu/regiokutatasszemle/article/view/12750
candidate:  https://mek.oszk.hu/10000/10080/10080.pdf   (foreign host, looks like a reference link)
```

But the byte-check of Taxicab storage showed Taxicab was already correct:

```text
2 pdf records
resolved_url: https://ojs.lib.unideb.hu/regiokutatasszemle/article/download/12750/11195
download status: 200
content-type: application/pdf
size: about 623 KB
first bytes: %PDF-1.5  -> real PDF
```

Lesson: Taxicab found the real PDF through the OJS `/article/download/` path,
even though Parseland's extracted candidate pointed at an unrelated off-site
file. If we had trusted the candidate URL, we would have wrongly called this row
a miss. Always confirm with the `%PDF-` byte-check before deciding a row is
missing or recovered.

This means the webapp candidate view is good for triage but is not the verdict.
The webapp now has a "Taxicab stored PDF" panel that lists the pdf records and
byte-checks each one (`%PDF-` or not), so the Parseland candidate and the real
stored result sit side by side. The stored-PDF panel is the verdict; the
Parseland candidate is just the guess.

### Real Example: DOI That Resolves Straight To A PDF (No HTML Page)

Some DOIs do not have an HTML landing page at all. The DOI redirects directly to
a PDF file. The old webapp could not see these: its flow was DOI -> HTML ->
Parseland -> candidate, so when there was no HTML record it wrongly said "No
stored HTML scrape" and showed nothing, even when Taxicab already had the PDF.

DOI:

```text
10.36838/v4i6.14
```

Taxicab storage for this DOI:

```text
html records: 0
pdf records:  several, all pointing at the same file
resolved_url: https://terra-docs.s3.us-east-2.amazonaws.com/IJHSR/Articles/volume4-issue6/2022_46_p80_Nguyen.pdf
download status: 200
content-type: application/pdf
size: about 485 KB
first bytes: %PDF-1.7  -> real PDF
```

So Taxicab had already fully recovered this row, but the HTML-only view made it
look like a miss. Lesson: never decide a row is missing from the HTML/Parseland
path alone. Always read Taxicab's stored pdf records and byte-check them. The
webapp now does this for every DOI, HTML or not.

### Real Example: A `.pdf` URL That Redirects To A Paywall (OUP)

A candidate URL that ends in `.pdf` can still be a trap. Some publisher PDF
URLs do not return PDF bytes. They redirect back to the article page, which is a
paywall or login HTML page.

DOI:

```text
10.1016/s0378-1097(99)00346-8
```

The webapp candidate looked perfect. It ends in `.pdf` and sits on the same
publisher host:

```text
landing:    https://academic.oup.com/femsle/article-abstract/177/2/289/447451
candidate:  https://academic.oup.com/femsle/article-pdf/177/2/289/19096376/177-2-289.pdf
```

But fetching that `article-pdf` URL redirects to the same paywalled article
page. The response is HTML, not PDF bytes. So this is not a real PDF, even
though the URL looks like one.

Lesson: the URL shape is not proof. Taxicab must measure the fetched bytes, not
trust the link:

```text
follow the candidate URL
check the final response after redirects
if the bytes start with %PDF-      -> real PDF
if the bytes are HTML / login / paywall -> not a PDF, do not count it
```

This is the same rule as "Do not count a URL ending in `.pdf` as success by
itself" from earlier in this file, shown with a concrete OUP redirect example.
Publishers like Oxford Academic, Elsevier, Wiley, and SAGE often do this: the
`article-pdf` or `/doi/pdf/` link bounces an unauthenticated fetch back to the
paywalled landing page. Only the byte check tells the truth.

### Recovery Target: PDF Lives On An Open Aggregator, Not The DOI Host

Sometimes the DOI resolves to a publisher page that has no public PDF, but the
same article is openly available as a PDF on a different host (an aggregator or
repository). Taxicab currently misses these because it only looks at the host
the DOI resolved to.

DOI:

```text
10.7256/2454-0730.2019.1.20595
```

Taxicab resolved this to the nbpublish reader page and found no PDF:

```text
landing:   https://nbpublish.com/library_read_article.php   (no PDF link, generic reader page)
candidate: (none)
```

But the same article is openly available as a real PDF on CyberLeninka:

```text
open pdf: https://cyberleninka.ru/article/n/servisologiya-kak-nauchnaya-osnova-razvitiya-sfery-servisa.pdf
```

So a public PDF exists; Taxicab just looked in the wrong place. This is a real
recovery opportunity, not a "no PDF expected" row.

The improvement target:

```text
DOI resolves to publisher host with no public PDF
-> also check known open aggregators/repositories for the same article
   (e.g. CyberLeninka, and similar)
-> fetch the aggregator PDF
-> verify bytes start with %PDF-
-> store it as a Taxicab PDF record
```

Do not claim this as fixed until Taxicab DOI lookup shows a PDF record and the
Taxicab download URL returns `%PDF-` bytes. Treat the aggregator-PDF lane as a
provider/route candidate to test through the no-storage probe first, then the
reharvest-and-confirm loop.

## Big Recurring Class: ScienceDirect / Elsevier Paywall PDF Redirects

This is not a one-off. It is one of the largest single failure classes in the
corpus, so it deserves a real solution, not a per-DOI patch.

### The Pattern

The DOI resolves to a ScienceDirect abstract page, and the `/pdf` URL we build
from it just bounces back to that same paywalled page.

DOI:

```text
10.1016/0963-8695(91)90937-x
```

```text
landing:   https://www.sciencedirect.com/science/article/abs/pii/096386959190937X
candidate: https://www.sciencedirect.com/science/article/pii/096386959190937X/pdf
```

Fetching the candidate does not return PDF bytes. It redirects to the abstract
page, which shows the Elsevier paywall: "Access through your organization" and
"Purchase PDF". So the bytes are HTML, not a PDF.

The tell-tale signs of this closed class:

```text
landing path contains /article/abs/pii/   (abs = abstract, usually closed)
fetched page text contains: "Access through your organization"
                            "Purchase PDF"
                            "Get rights and content"
                            "Sign in"
the response is HTML, not %PDF-
```

### Why One-Off Fixes Do Not Work Here

There are many such rows (Elsevier/ScienceDirect, and the same shape on Wiley,
OUP, SAGE, etc.). Rewriting one URL or reharvesting one DOI does not move the
number, because the blocker is access, not a wrong URL. The `/pdf` URL is
already the "right" shape; the publisher just refuses it without a paywall
login.

### Strong Solution (Two Steps)

Step 1 — Detect and stop lying to ourselves. Make Taxicab measure bytes, not
trust the URL, and recognize the paywall signature:

```text
fetch candidate -> follow redirects -> read final bytes
if bytes start with %PDF-                         -> real PDF, store it
if final page is the publisher abstract/paywall   -> NOT a PDF
   (matches /abs/ landing + paywall text above)
```

A row in this state is a closed publisher article. Do not store the HTML as a
PDF, and do not count it as a Taxicab retrieval miss either. It is "no public
PDF at the publisher".

Step 2 — Look for a public copy somewhere else before giving up. For each closed
publisher row, check open locations for the same work:

```text
OpenAlex open-access location (best_oa_location / oa_url) for the DOI
open aggregators and repositories (e.g. CyberLeninka, institutional repos, preprint servers)
```

If an open copy exists, fetch that URL (not the publisher paywall URL), verify
`%PDF-`, and store it. This is the same lesson as the aggregator example above
and the earlier candidate_url reharvest work: when Taxicab is handed the correct
open URL, its fetch code works; the failure is URL selection, not retrieval.

### How To Work This Class

```text
1. Cluster all rows whose landing is /article/abs/pii/ on sciencedirect.com.
2. Split them with the byte check + paywall signature into:
   - genuinely closed (no public PDF anywhere)  -> mark no_public_pdf, stop chasing
   - has an open copy elsewhere                  -> recover via the open URL
3. For the open-copy group, test the open URL through the no-storage probe,
   then the bounded reharvest-and-confirm loop.
4. Only the proven %PDF- recoveries count toward the KPI.
```

The win here is twofold: stop counting paywall HTML as PDF (accuracy), and
recover the subset that really is open somewhere else (real lift). Chasing the
publisher paywall URL itself is a dead end without provider/login access.

## Be Careful With Springer, Elsevier, Wiley, And Similar Publishers

Do not say a publisher improved just because Taxicab currently has some valid
PDFs from that publisher.

To claim improvement, show:

```text
before: Taxicab missed the public PDF
change: specific route/fetch fix
after: Taxicab stores valid PDF bytes
```

For example, a Springer DOI that already had PDF records before the change only
proves Taxicab can retrieve some Springer PDFs. It does not prove a new Springer
fix.

## Simple Standup Language

Use this wording when explaining the work:

```text
I am separating two things.
First, I check whether a public PDF really exists.
Second, when a public PDF exists and Taxicab misses it, I fix the fetch path.

I only count a PDF recovery when Taxicab stores a file and the file starts with
%PDF-. If the publisher returns a login page, paywall page, bot page, or HTML
viewer, I do not count that as a PDF.
```

## Safe Commands For Local Checking

Lookup a DOI:

```bash
curl -sS 'http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com/taxicab/doi/10.xxxx/yyyy'
```

Download a stored Taxicab file and check the first bytes:

```bash
python3 - <<'PY'
import requests
url = 'http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com/taxicab/<uuid>'
r = requests.get(url, timeout=30)
print(r.status_code)
print(r.headers.get('content-type'))
print(r.content[:12])
print(r.content.startswith(b'%PDF-'))
PY
```

Do not print secrets, cookies, signed URLs, Browserbase session IDs, or raw
private provider evidence.

## Dated Verification Log

Short, dated notes from manual spot-checks. Each entry records the date, the
DOI, what was checked, and the reason for the outcome. These are evidence, not
conclusions about the whole corpus.

### 2026-06-26 — Springer DOI looked like a miss but was already recovered

DOI:

```text
10.1007/s10705-024-10386-1
```

URL inspected:

```text
https://link.springer.com/content/pdf/10.1007/s10705-024-10386-1.pdf
```

First impression was that "Taxicab + Parseland could not get it". The byte-check
disproved that:

```text
Parseland candidate: https://link.springer.com/content/pdf/10.1007/s10705-024-10386-1.pdf  (correct)
Taxicab stored pdf records: 3, all application/pdf, all start with %PDF-
size: about 1.25 MB
```

Reason for the confusion: a naive direct fetch of that Springer URL from the
local sandbox failed (`urlopen error`, local network/SSL block). That local
failure is not Taxicab. Taxicab fetches through Zyte, which retrieved the real
PDF, and Parseland had already extracted the correct candidate. So this is a
clean success, not a miss.

Lesson: do not judge a row from a naive direct fetch or from an empty candidate
panel. The verdict is Taxicab's stored bytes (`%PDF-`). Both Parseland and
Taxicab succeeded here.

### 2026-06-26 — APS Physical Review B: PDF button exists but page is paywalled

DOI:

```text
10.1103/physrevb.44.3757
```

```text
landing:   https://journals.aps.org/prb/abstract/10.1103/PhysRevB.44.3757
candidate: http://link.aps.org/pdf/10.1103/PhysRevB.44.3757
Taxicab stored pdf records: 0   (real miss)
```

Parseland extracted a clean-looking candidate, and the APS page even shows a
"PDF" button. But the page itself says "Authorization Required — We need you to
provide your credentials before accessing this content" with "Log in via your
institution / Access through your institution". So the article (1991 Phys. Rev.
B) is paywalled: the `link.aps.org/pdf/` URL redirects to this login/paywall
page and returns HTML, not PDF bytes.

Reason this is a real miss, not a tooling bug: Taxicab has 0 stored PDF records,
and the candidate URL is access-gated. This is the same paywall-redirect class
as the ScienceDirect and Oxford Academic examples above, just on APS
(`journals.aps.org` / `link.aps.org`). It matches the APS provider lane in the
handoff, where Zyte strategies return `js_redirect_unresolved` and recovered
0/24.

Handling: treat as closed publisher access. Do not store the login HTML as a
PDF. Only recover if an open copy exists elsewhere (OpenAlex OA location,
arXiv/repository), tested through the no-storage probe first. Chasing the APS
PDF URL directly is a dead end without provider/login access.
