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
