#!/usr/bin/env python3
"""Tiny DOI -> Taxicab -> Parseland -> candidate PDF URL web app.

Enter a DOI in the browser. The backend:
  1. Optionally POSTs the DOI to the Harvester to kick off a fresh lookup (/taxicab).
  2. GETs the latest stored scrape (UUID) for that DOI (/taxicab/doi/<doi>).
  3. GETs Parseland's parse of that stored HTML record (/parseland/<uuid>).
  4. Pulls the candidate PDF URL out of Parseland's extracted links.

Stdlib only. Run:  python3 scripts/parseland_webapp.py  then open http://localhost:8000
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, quote, urlparse, urlsplit, urlunsplit

TAXICAB = "http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com"
PARSELAND = "http://parseland-load-balancer-667160048.us-east-1.elb.amazonaws.com"
PDF_RE = re.compile(r"pdf|pdfft|download", re.IGNORECASE)
# pdfpreview/.../x.jpg etc. match PDF_RE but are image previews, not PDFs.
IMG_EXT_RE = re.compile(r"\.(jpe?g|png|gif|webp|svg|tiff?)$", re.IGNORECASE)


def clean_url(url: str) -> str:
    parts = urlsplit((url or "").strip())
    if not parts.scheme or not parts.netloc:
        return (url or "").strip()
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def normalize_doi(raw: str) -> str:
    doi = (raw or "").strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE)
    return doi.strip().strip("/")


def latest(records: list[dict]) -> dict | None:
    if not records:
        return None
    return sorted(records, key=lambda r: str(r.get("created_date") or r.get("created_timestamp") or ""), reverse=True)[0]


def extract_pdf_candidates(parseland: dict) -> list[str]:
    """Mirror the batch loop: PDF candidates are extracted-link URLs that look like PDFs."""
    out: list[str] = []
    for item in parseland.get("urls") or []:
        value = item.get("url") if isinstance(item, dict) else str(item)
        if value and PDF_RE.search(value):
            cleaned = clean_url(value)
            if IMG_EXT_RE.search(urlsplit(cleaned).path):
                continue
            if cleaned not in out:
                out.append(cleaned)
    return out


def http_get(url: str, timeout: float) -> tuple[int | None, bytes, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status, resp.read(), ""
    except urllib.error.HTTPError as e:
        return e.code, e.read() if hasattr(e, "read") else b"", ""
    except Exception as e:  # noqa: BLE001 - surface any transport error to the UI
        return None, b"", str(e)


def http_post_json(url: str, payload: dict, timeout: float) -> tuple[int | None, str]:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def bytecheck_pdf(uuid: str, timeout: float) -> dict:
    """Download a stored Taxicab object and report whether it is real PDF bytes."""
    status, body, err = http_get(f"{TAXICAB}/taxicab/{quote(uuid, safe='')}", timeout)
    return {
        "uuid": uuid,
        "download_status": status,
        "size_bytes": len(body),
        "is_pdf": body.startswith(b"%PDF-"),
        "error": err,
    }


def stored_pdf_records(records: dict, timeout: float, limit: int = 5) -> list[dict]:
    """Byte-check Taxicab's stored pdf records, newest first, deduped by resolved URL."""
    out: list[dict] = []
    seen: set[str] = set()
    pdfs = sorted(
        records.get("pdf") or [],
        key=lambda r: str(r.get("created_date") or r.get("created_timestamp") or ""),
        reverse=True,
    )
    for rec in pdfs:
        url = clean_url(str(rec.get("resolved_url") or rec.get("url") or ""))
        if url in seen:
            continue
        seen.add(url)
        check = bytecheck_pdf(str(rec.get("id") or ""), timeout)
        out.append({"resolved_url": url, **check})
        if len(out) >= limit:
            break
    return out


def lookup(doi: str, *, harvest: bool, timeout: float) -> dict:
    doi = normalize_doi(doi)
    if not doi:
        return {"error": "Enter a DOI."}
    steps: list[str] = []
    input_url = f"https://doi.org/{doi}"

    if harvest:
        status, err = http_post_json(f"{TAXICAB}/taxicab",
                                     {"native_id": doi, "native_id_namespace": "doi", "url": input_url},
                                     timeout)
        steps.append(f"1. Harvester POST /taxicab -> {err or status}")
    else:
        steps.append("1. Harvester POST skipped (use existing stored scrape)")

    status, body, err = http_get(f"{TAXICAB}/taxicab/doi/{quote(doi, safe='')}", timeout)
    steps.append(f"2. Taxicab GET /taxicab/doi -> {err or status}")
    if status != 200 or err:
        return {"doi": doi, "steps": steps, "error": f"Taxicab DOI lookup failed ({err or status})."}
    try:
        records = json.loads(body.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"doi": doi, "steps": steps, "error": f"Taxicab returned bad JSON: {e}"}

    # Always report what Taxicab actually stored, byte-checked. This is the verdict,
    # and it works even for direct-to-PDF DOIs that have no HTML landing page.
    stored = stored_pdf_records(records, timeout)
    good = sum(1 for r in stored if r.get("is_pdf"))
    steps.append(f"   Taxicab stored PDFs -> {len(stored)} record(s), {good} real %PDF-")
    result: dict = {"doi": doi, "steps": steps, "stored_pdfs": stored}

    html = latest(records.get("html") or [])
    if not html:
        result["note"] = (
            "No HTML landing scrape for this DOI (it may resolve straight to a PDF). "
            "See Taxicab stored PDFs below for the real verdict."
        )
        return result

    uuid = str(html.get("id") or "")
    landing_url = clean_url(str(html.get("resolved_url") or html.get("url") or ""))
    result.update({"uuid": uuid, "landing_url": landing_url})
    steps.append(f"   latest scrape UUID -> {uuid}")

    status, body, err = http_get(f"{PARSELAND}/parseland/{quote(uuid, safe='')}", timeout)
    steps.append(f"3. Parseland GET /parseland/<uuid> -> {err or status}")
    if status != 200 or err:
        result["error"] = f"Parseland failed ({err or status})."
        return result
    try:
        parsed = json.loads(body.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        result["error"] = f"Parseland returned bad JSON: {e}"
        return result

    candidates = extract_pdf_candidates(parsed if isinstance(parsed, dict) else {})
    steps.append(f"4. Candidate PDF URLs found -> {len(candidates)}")
    result.update({
        "candidate_pdf_url": candidates[0] if candidates else "",
        "candidate_pdf_urls": candidates,
        "all_urls": [clean_url(u.get("url") if isinstance(u, dict) else str(u)) for u in (parsed.get("urls") or [])],
        "parseland_error": str(parsed.get("error") or "") if isinstance(parsed, dict) else "",
    })
    return result


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DOI -> Parseland candidate PDF</title>
<style>
:root{--bg:#0f1117;--card:#1a1d27;--line:#2a2f3d;--text:#e6e8ee;--mut:#9aa3b2;--accent:#4f9cf9;--ok:#3ddc84}
*{box-sizing:border-box}body{margin:0;font:16px/1.5 system-ui,sans-serif;background:var(--bg);color:var(--text)}
main{max-width:760px;margin:0 auto;padding:48px 20px}
h1{font-size:1.4rem;margin:0 0 4px}p.sub{color:var(--mut);margin:0 0 28px}
form{display:flex;gap:8px;flex-wrap:wrap}
input{flex:1;min-width:240px;padding:12px 14px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--text);font-size:1rem}
button{padding:12px 20px;border:0;border-radius:10px;background:var(--accent);color:#04101f;font-weight:600;cursor:pointer}
button:disabled{opacity:.5;cursor:wait}
label.cb{display:flex;align-items:center;gap:6px;color:var(--mut);font-size:.85rem;margin-top:10px}
.card{margin-top:24px;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;display:none}
.card.show{display:block}
.lbl{color:var(--mut);font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;margin:14px 0 4px}
.lbl:first-child{margin-top:0}
.pdf{font-size:1.05rem;word-break:break-all}
.pdf a{color:var(--ok)}
a{color:var(--accent)}
.mono{font:13px/1.5 ui-monospace,Menlo,monospace;color:var(--mut);white-space:pre-wrap;word-break:break-all}
.err{color:#ff6b6b}
ul{margin:6px 0;padding-left:18px}li{word-break:break-all;margin:2px 0}
</style></head><body><main>
<h1>DOI &rarr; candidate PDF link</h1>
<p class="sub">Harvester &rarr; latest scrape &rarr; Parseland &rarr; PDF URL it extracted from the landing page.</p>
<form id="f">
  <input id="doi" placeholder="10.1016/0550-3213(92)90256-b" autofocus>
  <button id="go" type="submit">Look up</button>
</form>
<label class="cb"><input type="checkbox" id="harvest"> Re-harvest first (POST to Harvester, costs Zyte credits &amp; slower)</label>
<div class="card" id="card"></div>
<script>
const f=document.getElementById('f'),card=document.getElementById('card'),go=document.getElementById('go');
f.onsubmit=async e=>{
  e.preventDefault();
  const doi=document.getElementById('doi').value.trim();
  if(!doi)return;
  go.disabled=true;go.textContent='Working...';
  card.className='card show';card.innerHTML='<div class="mono">Looking up '+doi+' ...</div>';
  try{
    const r=await fetch('/lookup?doi='+encodeURIComponent(doi)+'&harvest='+document.getElementById('harvest').checked);
    const d=await r.json();
    card.innerHTML=render(d);
  }catch(err){card.innerHTML='<div class="err">Request failed: '+err+'</div>';}
  go.disabled=false;go.textContent='Look up';
};
function esc(s){return (s||'').replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));}
function link(u){return u?'<a href="'+esc(u)+'" target="_blank" rel="noopener">'+esc(u)+'</a>':'';}
function render(d){
  let h='';
  h+='<div class="lbl">Candidate PDF URL (Parseland guess)</div>';
  if(d.candidate_pdf_url){h+='<div class="pdf">'+link(d.candidate_pdf_url)+'</div>';}
  else{h+='<div class="err">No candidate PDF URL extracted.'+(d.error?' '+esc(d.error):'')+'</div>';}
  if(d.candidate_pdf_urls&&d.candidate_pdf_urls.length>1){
    h+='<div class="lbl">Other candidates</div><ul>'+d.candidate_pdf_urls.slice(1).map(u=>'<li>'+link(u)+'</li>').join('')+'</ul>';
  }
  // Taxicab stored PDFs = the real verdict (byte-checked), independent of Parseland.
  h+='<div class="lbl">Taxicab stored PDF (byte-checked = verdict)</div>';
  if(d.stored_pdfs&&d.stored_pdfs.length){
    h+='<ul>'+d.stored_pdfs.map(p=>{
      const ok=p.is_pdf;
      const badge='<span style="color:'+(ok?'var(--ok)':'#ff6b6b')+'">'+(ok?'%PDF- OK':'NOT pdf')+'</span>';
      const kb=p.size_bytes?(' '+Math.round(p.size_bytes/1024)+' KB'):'';
      return '<li>'+badge+' ('+(p.download_status||'?')+kb+')<br>'+link(p.resolved_url)+'</li>';
    }).join('')+'</ul>';
  } else {
    h+='<div class="err">Taxicab has no stored PDF for this DOI.</div>';
  }
  if(d.note){h+='<div class="lbl">Note</div><div class="mono">'+esc(d.note)+'</div>';}
  if(d.landing_url){h+='<div class="lbl">Landing page</div><div>'+link(d.landing_url)+'</div>';}
  if(d.uuid){h+='<div class="lbl">Scrape UUID</div><div class="mono">'+esc(d.uuid)+'</div>';}
  if(d.all_urls&&d.all_urls.length){h+='<div class="lbl">All Parseland URLs ('+d.all_urls.length+')</div><ul>'+d.all_urls.map(u=>'<li>'+link(u)+'</li>').join('')+'</ul>';}
  if(d.steps){h+='<div class="lbl">Steps</div><div class="mono">'+esc(d.steps.join('\\n'))+'</div>';}
  return h;
}
</script></main></body></html>"""


class Handler(BaseHTTPRequestHandler):
    timeout_s = 120.0

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        parts = urlparse(self.path)
        if parts.path == "/":
            self._send(200, PAGE.encode(), "text/html; charset=utf-8")
            return
        if parts.path == "/lookup":
            q = parse_qs(parts.query)
            doi = (q.get("doi") or [""])[0]
            harvest = (q.get("harvest") or ["false"])[0].lower() == "true"
            result = lookup(doi, harvest=harvest, timeout=self.timeout_s)
            self._send(200, json.dumps(result).encode(), "application/json")
            return
        self._send(404, b"not found", "text/plain")

    def log_message(self, *args) -> None:  # quiet
        pass


def _selftest() -> None:
    sample = {"urls": [
        {"url": "https://x.org/article/abs"},
        {"url": "https://x.org/article/full.pdf?download=1#frag"},
        {"url": "https://x.org/pdfft/123"},
        {"url": "https://x.org/pub/pdfpreview/123.jpg"},
        "https://x.org/plain",
    ]}
    cands = extract_pdf_candidates(sample)
    assert cands == ["https://x.org/article/full.pdf", "https://x.org/pdfft/123"], cands
    assert normalize_doi("https://doi.org/10.1/AB") == "10.1/AB"
    assert normalize_doi("  10.1/AB/ ") == "10.1/AB"
    assert latest([{"id": "a", "created_date": "1"}, {"id": "b", "created_date": "2"}])["id"] == "b"
    print("selftest ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--timeout", type=float, default=120.0)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    Handler.timeout_s = args.timeout
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"Serving on http://localhost:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
