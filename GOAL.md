# Taxicab Goal State

Last updated: 2026-06-17 PDT.

## Goal

```text
HTML Phase 1: complete, target hit.
PDF Phase 2: active, target >=95% good_pdf on pdf_expected_total.
Stretch target: >=98% good_pdf after the 95% gate is stable.
```

## Active Repositories

```text
Taxicab implementation:
  /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab

Do not use:
  /Users/shubh-trips/Documents/openalex-taxicab

Oxjobs reports:
  /Users/shubh-trips/Documents/OpenAlex/oxjobs

HTML report/control:
  /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-audit

PDF report/control:
  /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf
  job #461
```

## Current Gate

```text
Gate 0: HTML Phase 1 main sync.
Status: complete.
Commit: 07c974e taxicab: sync phase 1 eval context
Pushed: origin/main

Gate 1: Taxicab PDF branch.
Status: in progress.
Branch: codex/taxicab-pdf-phase2
Current publish status: oxjobs #461 commit `58d55a98` publishes the scrubbed
AHA/Lippincott summary asset; prior commit `07bc9d9f` publishes the
AHA/Lippincott gold check in the report, and `4984229f` publishes the
graph-first minimalist PDF progress report. These are evidence/reporting-only
updates and do not change the accepted KPI. The accepted full 10K metric remains
`pdf-full10k-after-atlantis-3b13642` from Taxicab commit `3b13642`:
2,383/6,293 `good_pdf` (37.87%), +2 versus the DOI.org/OSTI gate and +546
versus denominator baseline, with 3,789 `missing_pdf_harvest`, 65
corrupt/truncated, 4 encrypted/unreadable, 23 supplement/preview, 6
interstitial/paywall, 0 timeout, and 0 `taxicab_error`. This is bounded
cache/reharvest lift, not a Taxicab-main production scraping push. The
AHA/Lippincott one-row lane `www.ahajournals.org:/doi/pdf/:doi/:id` recovered
0/1 through Zyte no-storage provider probing and 0/1 through Browserbase gold
evidence; Browserbase reached a 403 challenge and ended
`download_started_not_captured`. No Taxicab POST/R2/DynamoDB writes occurred,
no route code was written, and no production behavior changed. Earlier oxjobs
commit `74a062c6` publishes the aggregate-only Wiley PDF-direct
validator/provider Zyte recheck from Taxicab commit `9b01df6`; it recovered
0/10 current corrupt/truncated rows, all direct PDF-byte strategies returned
`empty_response`, and browser HTML returned HTML/interstitial/JS outcomes. The
residual refresh keeps 3,910 non-good rows across 655 clusters and 1,426
subclusters, but top-240 `probe_next` is now 0 and
`confirm_existing_branch_candidate` is 0 after ACS, ACM, Wiley, IOP,
bioRxiv/CSHLP, Elsevier DOI.org, and AHA/Lippincott moved out of route
promotion. Current phase: choose the next non-route provider/gold/validator
lane before any Taxicab main push.
Do not
promote SAGE, Wiley, ACS, IOP, Elsevier DOI.org, rank-39 DOI.org, ACM,
bioRxiv/CSHLP, IngentaConnect, ICE Virtual Library, Ecologica, ASTM Compass,
CCCC, Atlantis Press, IWA/AMPP/Sage Knowledge/RSNA/AJOG/Elgar, or broad
Elsevier article-PDF lanes without a narrower or provider-advised recipe. Do
not push Taxicab main before the full PDF 95% proof.
Current handoff override: `/goal` is active for PDF Phase 2. The top-level
accepted metric is `pdf-full10k-after-atlantis-3b13642`, 2,383/6,293
`good_pdf` (37.87%), with a 3,596-row gap to 95%. Latest oxjobs #461 commit
`0e59e67f` publishes the PeerJ branch evidence; prior `0f9fcaa2` publishes the
current Elsevier DOI.org Browserbase recheck; prior
`58d55a98` publishes the AHA/Lippincott summary asset, `07bc9d9f` publishes the
AHA/Lippincott gold check, and `4984229f` publishes the graph-first report.
None changes the accepted full-gate KPI.
Earlier oxjobs commit `74a062c6` remains the Wiley PDF-direct
validator/provider Zyte recheck from Taxicab commit `9b01df6`: 0/10 recovered,
all direct PDF-byte strategies returned `empty_response`, browser HTML returned
HTML/interstitial/JS outcomes, no Taxicab POST/R2/DynamoDB writes, no
production behavior change, and no accepted KPI change. AHA/Lippincott
`www.ahajournals.org:/doi/pdf/:doi/:id` also recovered 0/1 through Zyte and
0/1 through Browserbase, with Browserbase ending at a 403 challenge; it is
negative provider/access-flow evidence, not route-code evidence. Elsevier
DOI.org current Browserbase recheck `elsevier-doi-browserbase-gold5-5d5d0fc`
recovered 0/5, with four `download_started_not_captured` verdicts and one
`html_not_pdf`; keep it as provider/gold evidence, not route-code evidence.
PeerJ branch commit `bf1632f` recovers 1/1 current PeerJ `html_instead_of_pdf`
residual and preserves 1/1 already-good PeerJ row with 0 regressions, but the
remaining PeerJ `missing_pdf_harvest` row does not recover. This is branch
evidence only; no accepted KPI lift and no Taxicab main push.
Browserbase can run for
evidence/gold collection using `BROWSERBASE_API_KEY` from ignored
`/Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/.env`;
`BROWSERBASE_PROJECT_ID` is optional for the current REST session path.
Browserbase verdicts stay separate from Taxicab baseline categories. AWS
CLI/default `.env.aws` session credentials are expired; AWS is not required for
the immediate no-storage Zyte/Browserbase evidence loop. Top-240 `probe_next`
remains 0, and `confirm_existing_branch_candidate` remains 0. Gate 21.999fz
closed AHA/Lippincott as negative evidence; Gate 21.999ga closed current
Elsevier DOI.org Browserbase recheck as negative evidence; Gate 21.999gb
validated PeerJ as branch-only evidence; next Gate 21.999gc is choosing the
next non-route provider/gold/validator lane from the residual queue.
Historical sections below may use "current" relative to older gates; this block
is authoritative.
Next exact command:
cd /Users/shubh-trips/Documents/OpenAlex/openalex-taxicab
python3 scripts/taxicab_cluster_residuals.py --rows pdf_eval_runs/pdf-full10k-after-atlantis-3b13642/rows.ndjson --out pdf_eval_runs --run-id residual-clusters-after-peerj-branch-bf1632f --sample-size 5 --top-n 240
python3 - <<'PY'
import json
from pathlib import Path
rows = json.loads(Path('pdf_eval_runs/residual-subclusters.json').read_text())['top_subclusters']
for row in rows:
    if row.get('priority_band') == 'provider_lane_do_not_duplicate':
        continue
    print(row.get('count'), row.get('priority_band'), row.get('prior_evidence_status'), row.get('category'), row.get('publisher'), row.get('host'), row.get('candidate_source'), row.get('path_pattern'))
PY

After Gate 0 is pushed:

```text
Gate 1: create codex/taxicab-pdf-phase2 from current origin/main. [done]
Gate 2: create new auto-ID oxjobs taxicab-pdf job and report scaffold. [done, #461]
Gate 3: implement PDF harness, offline validator tests, and live smoke. [done]
Gate 4: run PDF limit-100 and full 10K baseline on the Goldie corpus. [done]
Gate 5: publish full baseline to oxjobs #461. [done]
Gate 6: enrich PDF-expected denominator. [done]
Gate 7: publish denominator-enriched baseline to oxjobs #461. [done]
Gate 8: add gated PDF reharvest mode. [done]
Gate 9: add reharvest POST-context instrumentation. [done]
Gate 10: create Springer Zyte support/evidence packet. [done]
Gate 11: add PDF Browserbase evidence mode. [done]
Gate 12: add PDF row-timeout watchdog for slow PDF/CDN rows. [done]
Gate 13: Elsevier missing-PDF bounded sample. [done]
Gate 14: confirm recovered Elsevier PDFs with read-only follow-up. [done]
Gate 15: generate and run Elsevier 100-row queue. [done]
Gate 16: correct first-page/preview PDF classifier. [done]
Gate 17: publish corrected Elsevier 100-row gate to oxjobs #461. [done, oxjobs 3d8a5fa0]
Gate 18: split Elsevier into ScienceDirect, Lancet, Cell, direct-asset, router, corrupt/truncated, and Zyte-support clusters. [done, oxjobs 825c2e2d]
Gate 19: run ScienceDirect no-storage route probe and create Zyte packet. [done, taxicab 741e9a7, oxjobs 666d0ed6]
Gate 20: run Lancet no-storage route probe and create Zyte packet. [done, oxjobs 2105c8f1]
Gate 21: run Cell Press no-storage route probe and create Zyte packet. [done, oxjobs a160ec1a]
Gate 21.5: run Cell Browserbase evidence sample and publish scrubbed public summary. [done, oxjobs d0344d1d]
Gate 21.75: run Wiley bounded reharvest and publish scrubbed provider packet. [done, oxjobs 3d7356bc]
Gate 21.9: run De Gruyter bounded reharvest and publish scrubbed provider packet. [done, oxjobs de7d0f2d]
Gate 21.95: run Lippincott bounded reharvest and publish scrubbed provider packet. [done, oxjobs b88a5a79]
Gate 21.98: run Oxford bounded reharvest and publish scrubbed provider packet. [done, oxjobs e1fe9deb]
Gate 21.99: run CUP/Cambridge bounded reharvest and publish scrubbed provider packet. [done, oxjobs df7784c9]
Gate 21.995: test documented CUP/Cambridge Zyte strategy variants. [done, oxjobs 77e793a8]
Gate 21.996: run SSRN bounded reharvest and publish scrubbed provider packet. [done, oxjobs ade1b60f]
Gate 21.997: run IOP bounded reharvest and read-only confirmation. [done, oxjobs 7d376fa0]
Gate 21.998: run accepted full 10K read-only gate after IOP. [done, oxjobs fbba7e56]
Gate 21.999: run remaining IOP rows and accepted full 10K read-only gate. [done, oxjobs 5cca142e]
Gate 21.999a: run RSC bounded reharvest and publish provider packet. [done, oxjobs 68025078]
Gate 21.999b: run AIP targeted sample and publish provider packet. [done, oxjobs 85584ddd]
Gate 21.999c: run Taylor samples and accepted full 10K gate. [done, oxjobs 574539d2]
Gate 21.999d: run ACS targeted sample and publish provider packet. [done, oxjobs 482cc4fd]
Gate 21.999e: run SPIE targeted sample and publish provider packet. [done, oxjobs c5792694]
Gate 21.999f: run Thieme targeted sample and publish provider packet. [done, oxjobs 8cb377c7]
Gate 21.999g: run Sage targeted sample and publish provider packet. [done, oxjobs ca3b11fe]
Gate 21.999h: run Brill targeted sample and publish provider packet. [done, oxjobs 172b7580]
Gate 21.999i: run AMA/JAMA targeted sample and publish provider packet. [done, oxjobs d82e9ba6]
Gate 21.999j: run APS targeted sample and publish provider packet. [done, oxjobs 147a9e65]
Gate 21.999k: run ACM targeted sample and publish provider packet. [done, oxjobs 32d6a637]
Gate 21.999l: run BMJ targeted sample and publish provider packet. [done, oxjobs 3319e184]
Gate 21.999m: run Karger targeted sample, read-only confirmation, and provider packet. [done, oxjobs ecae684b]
Gate 21.999n: run full 10K read-only gate after Karger. [done, oxjobs 5ccb3df5]
Gate 21.999o: run Optica/opg targeted sample and publish provider packet. [done, oxjobs 826bd689]
Gate 21.999p: run JSTOR targeted sample and publish provider packet. [done, oxjobs 19ca1aff]
Gate 21.999q: run Inlibra targeted sample and publish provider packet. [done, oxjobs 0df48262]
Gate 21.999r: run Scientific.net targeted sample and publish provider packet. [done, oxjobs 3b84fb4b]
Gate 21.999s: run Persee targeted sample and publish provider packet. [done, oxjobs 1a7d1ddb]
Gate 21.999t: run Nature targeted sample, read-only confirmation, and provider packet. [done, oxjobs 33c8c71c]
Gate 21.999u: run J-STAGE targeted sample, read-only confirmation, and provider packet. [done, oxjobs 59789f72]
Gate 21.999v: run University of Chicago journals targeted sample and provider packet. [done, oxjobs 95bde36b]
Gate 21.999w: run ASME targeted sample and provider packet. [done, oxjobs 10d80d80]
Gate 21.999x: run Cairn targeted sample and provider packet. [done, oxjobs 97b61e38]
Gate 21.999y: run Physiology targeted sample and provider packet. [done, oxjobs 33d5cb5b]
Gate 21.999z: run ASCE targeted sample and provider packet. [done, oxjobs b57dba2f]
Gate 21.999aa: run PDCNet targeted sample and provider packet. [done, oxjobs a1663d3f]
Gate 21.999ab: run EurekaSelect targeted sample and provider packet. [done, oxjobs 357c4ee1]
Gate 21.999ac: run ActaHort targeted sample and provider packet. [done, oxjobs be526662]
Gate 21.999ad: run V&R eLibrary targeted sample and provider packet. [done, oxjobs c3d3b00b]
Gate 21.999ae: run IWA Publishing targeted sample and provider packet. [done, oxjobs 98a037c1]
Gate 21.999af: run AMS journals targeted sample and provider packet. [done, oxjobs 8fe1d510]
Gate 21.999ag: run JPET/ASPET targeted sample and provider packet. [done, oxjobs ae72a1ff]
Gate 21.999ah: run OnePetro targeted sample and provider packet. [done, oxjobs 029f9ac9]
Gate 21.999ai: run Mary Ann Liebert targeted sample and provider packet. [done, oxjobs c9eafb75]
Gate 21.999aj: run AACR Figshare targeted sample and provider packet. [done, oxjobs dd7ab56d]
Gate 21.999ak: run AMPP targeted sample and provider packet. [done, oxjobs ef843caa]
Gate 21.999al: run Healio targeted sample and provider packet. [done, oxjobs 64517b97]
Gate 21.999am: run Sage Knowledge targeted sample and provider packet. [done, oxjobs 79af39d8]
Gate 21.999an: run IGI Global targeted sample, read-only confirmation, and provider packet. [done, oxjobs 471f9ee3]
Gate 21.999ao: run UC Press targeted sample and provider packet. [done, oxjobs e435bc5e]
Gate 21.999ap: run RUPress targeted sample, read-only confirmation, and provider packet. [done, oxjobs fa847b5a]
Gate 21.999aq: run Emerald targeted sample and provider packet. [done, oxjobs f191f0eb]
Gate 21.999ar: run JACC targeted sample and provider packet. [done, oxjobs eea013bf]
Gate 21.999as: run AJO targeted sample and provider packet. [done, oxjobs a72d7c09]
Gate 21.999at: run BioOne targeted sample and provider packet. [done, oxjobs b60d7147]
Gate 21.999au: run Canadian Science Publishing targeted sample and provider packet. [done, oxjobs 634173b9]
Gate 21.999av: run Edward Elgar targeted sample, read-only confirmation, and provider packet. [done, oxjobs 9771940c]
Gate 21.999aw: run American Concrete Institute targeted sample and provider packet. [done, oxjobs 9fbae749]
Gate 21.999ax: run American Journal of Surgery targeted sample and provider packet. [done, oxjobs 1b4912ec]
Gate 21.999ay: run AJOG targeted sample, read-only confirmation, and provider packet. [done, oxjobs 2e492500]
Gate 21.999az: run Scholarly Publishing Collective targeted sample and provider packet. [done, oxjobs 362d2b2f]
Gate 21.999ba: run Royal Society Publishing targeted sample and provider packet. [done, oxjobs cfeb6d34]
Gate 21.999bb: run KoreaScience targeted sample and provider packet. [done, oxjobs 53c6d7fe]
Gate 21.999bc: run Journal of Pharmaceutical Sciences targeted sample and provider packet. [done, oxjobs c1f26ec8]
Gate 21.999bd: run CHEST targeted sample, read-only confirmation, and provider packet. [done, oxjobs ee27cd5e]
Gate 21.999be: run Green Journal targeted sample and provider packet. [done, oxjobs 0e0bb05f]
Gate 21.999bf: run SciELO targeted sample, read-only confirmation, and provider packet. [done, oxjobs 41a903e6]
Gate 21.999bg: run AIP `pubs.aip.org` targeted sample and provider packet. [done, oxjobs b7940463]
Gate 21.999bh: run DOI-router PDF URL targeted sample and provider packet. [done, oxjobs 4c711418]
Gate 21.999bi: run ScienceDirect direct PDF asset URL sample and provider packet. [done, oxjobs 58ab0e73]
Gate 21.999bj: run Springer `link.springer.com` high-volume sample and provider packet. [done, oxjobs 469a996b]
Gate 21.999bk: run De Gruyter Brill `www.degruyterbrill.com` residual sample and provider packet. [done, oxjobs ddb8a16f]
Gate 21.999bl: run AIAA `arc.aiaa.org` tail sample and provider packet. [done, oxjobs 83c0b0fe]
Gate 21.999bm: run Neurology `www.neurology.org` tail sample and provider packet. [done, oxjobs d9ede76b]
Gate 21.999bn: run Begell House `www.dl.begellhouse.com` tail sample and provider packet. [done, oxjobs 36ba508f]
Gate 21.999bo: run MIT Press Direct `direct.mit.edu` tail sample and provider packet. [done, oxjobs 9fdca746]
Gate 21.999bp: run RSNA `pubs.rsna.org` tail sample and provider packet. [done, oxjobs 67a5b554]
Gate 21.999bq: run Gold Journal `www.goldjournal.net` tail sample and provider packet. [done, oxjobs 8d1c57b4]
Gate 21.999br: run ATS Journals `www.atsjournals.org` tail sample and provider packet. [done, oxjobs 7e4dcc79]
Gate 21.999bs: run Transcript Verlag `www.transcript-verlag.de` preview-candidate correction. [done, oxjobs 433d621e]
Gate 21.999bt: run PNAS `www.pnas.org` tail sample and provider packet. [done, oxjobs 8ff5fd14]
Gate 21.999bu: run Peter Lang `www.peterlang.com` tail sample and provider packet. [done, oxjobs a12417e1]
Gate 21.999bv: run Nomos eLibrary `www.nomos-elibrary.de` tail sample and provider packet. [done, oxjobs d7d1220d]
Gate 21.999bw: run Journal of Pediatric Surgery `www.jpedsurg.org` tail sample and provider packet. [done, oxjobs d6c52a5b]
Gate 21.999bx: run JBC `www.jbc.org` tail sample and provider packet. [done, oxjobs c5a71e38]
Gate 21.999by: run ADS `ui.adsabs.harvard.edu` tail sample and read-only confirmation. [done, oxjobs 34c32f5f]
Gate 21.999bz: run NCTM `pubs.nctm.org` tail sample, read-only confirmation, and provider packet. [done, oxjobs 877d1107]
Gate 21.999ca: run AAAHQ `publications.aaahq.org` tail sample, read-only confirmation, and provider packet. [done, oxjobs 63789cfc]
Gate 21.999cb: run EJSO `www.ejso.com` tail sample, read-only confirmation, and provider packet. [done, oxjobs fc590d0f]
Gate 21.999cc: run AUA Journals `www.auajournals.org` tail sample and provider packet. [done, oxjobs 16f51e88]
Gate 21.999cd: run Springer Publishing `connect.springerpub.com` tail sample and provider packet. [done, oxjobs d56b9fac]
Gate 21.999ce: run Vestnik/KRSU `vestnik.krsu.kg` tail sample and provider packet. [done, oxjobs 5a217501]
Gate 21.999cf: run Duke University Press `read.dukeupress.edu` tail sample and provider packet. [done, oxjobs 1e18ffdd]
Gate 21.999cg: run GeoScienceWorld `pubs.geoscienceworld.org` tail sample and provider packet. [done, oxjobs b3ba464e]
Gate 21.999ch: run Indian Journals `indianjournals.com` tail sample and provider packet. [done, oxjobs f4e4fe37]
Gate 21.999ci: run AJConline `ajconline.org` tail sample and provider packet. [done, oxjobs b4b2a251]
Gate 21.999cj: run IATED `library.iated.org` tail sample and provider packet. [done, oxjobs 2fb1349a]
Gate 21.999ck: run Brepols `www.brepolsonline.net` tail sample and provider packet. [done, oxjobs 9918c055 and 6a85359b]
Gate 21.999cl: run Copernicus Meeting Organizer `meetingorganizer.copernicus.org` tail sample and provider packet. [done, oxjobs 4bc7763f]
Gate 21.999cm: run Google Drive `drive.google.com` tail sample and provider packet. [done, oxjobs 3bd2e947]
Gate 21.999cn: run protocols.io `www.protocols.io` tail sample and residual packet. [done, oxjobs 95fd1945]
Gate 21.999co: run ASA/Scitation `asa.scitation.org` tail sample and provider packet. [done, oxjobs d457927c]
Gate 21.999cp: run IOS Press `content.iospress.com` tail sample and provider packet. [done, oxjobs 930c773c]
Gate 21.999cq: run AAI Journals `journals.aai.org` tail sample and provider packet. [done, oxjobs ebff6475]
Gate 21.999cr: run JCVA Online `www.jcvaonline.com` tail sample and provider packet. [done, oxjobs e48d73e8]
Gate 21.999cs: run Human Kinetics `journals.humankinetics.com` tail sample and residual packet. [done, oxjobs 93b383f6]
Gate 21.999ct: run full 10K read-only gate after Human Kinetics and bounded recoveries. [done, oxjobs 43ca3830]
Gate 21.999cu: add generic no-storage provider probe and publish residual IOP no-storage probe result. [done, taxicab 31663bc, oxjobs 27d5e414]
Gate 21.999cv: run J-STAGE corrupt-PDF subtype provider probe from accepted full-gate rows. [done, oxjobs 416b6fec]
Gate 21.999cw: run J-STAGE encrypted and missing/login provider probes, add structured PDF parser, run Wiley corrupt probe, run Wiley 67-row read-only gate, and publish full 10K structured-parser gate. [done, taxicab a61d34b, oxjobs dcb7bb14]
Gate 21.999cx: run residual Wiley corrupt-PDF 5-row provider probe from current structured-parser full-gate rows. [done, oxjobs 9569e1f6]
Gate 21.999cy: run residual Wiley corrupt-PDF all-row provider probe from current structured-parser full-gate rows. [done, oxjobs 6ba84787]
Gate 21.999cz: inspect and implement narrow Wiley PDF-byte strategy candidate. [done, taxicab 3b2d218]
Gate 21.999da: publish Wiley PDF-direct candidate evidence to oxjobs #461. [done, oxjobs d4f99eee]
Gate 21.999db: decide bounded confirmation path without Taxicab main push and run Wiley/Springer no-storage follow-up probes. [done, oxjobs 31d28693]
Gate 21.999dc: run current ScienceDirect missing-PDF no-storage provider probe. [done, taxicab 69553ae, oxjobs c15cd194]
Gate 21.999dd: refresh combined Zyte PDF-byte support packet with current follow-up evidence. [done, oxjobs d8e62ef8]
Gate 21.999de: wait for or test Zyte-advised PDF-byte recipe through no-storage probes. [blocked on/provider-guidance lane]
Gate 21.999df: classify missing-PDF rows from source PDF URL publisher domains and publish triage impact. [done, taxicab e584811, oxjobs 8b1d1b2f]
Gate 21.999dg: run read-only full-10K measurement refresh with improved publisher attribution. [done, taxicab 8a35869, oxjobs ebe97f4d]
Gate 21.999dh: run current Springer missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 8585a77, oxjobs 84760121]
Gate 21.999di: run current Wiley missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab fa95e59, oxjobs 3480ae82]
Gate 21.999dj: run current Elsevier missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 8abd909, oxjobs 68c2eb46]
Gate 21.999dk: run current De Gruyter missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab eb75f5e, oxjobs b04396d6]
Gate 21.999dl: run current Lippincott missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 4689af7, oxjobs 40cf1b9e]
Gate 21.999dm: run current Oxford missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 67187dc, oxjobs d4b6da1b]
Gate 21.999dn: run current CUP/Cambridge missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 41a9df8, oxjobs 38844dea]
Gate 21.999do: run current Taylor missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 70f8f8a, oxjobs af13892d]
Gate 21.999dp: run current SSRN missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 863d7aa, oxjobs 2c171c7e]
Gate 21.999dq: run current JSTOR missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab fe0d018, oxjobs 463bb712]
Gate 21.999dr: run current AIP Publishing missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab af746d4, oxjobs 14f254ac]
Gate 21.999ds: run current RSC missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab f709792, oxjobs e3621c28]
Gate 21.999dt: run current ACS missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 7e4b5e5, oxjobs 21a7697c]
Gate 21.999du: run current Brill missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 88bc77f, oxjobs e2bac29b]
Gate 21.999dv: run current Thieme missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 3f45c6a, oxjobs 4838bd1c]
Gate 21.999dw: run current SPIE missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 9fa4596, oxjobs fe048cca]
Gate 21.999dx: run current BMJ missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 9ccfeaf, oxjobs 6de28ec3]
Gate 21.999dy: run current Sage missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 1f57c9b, oxjobs d059488d]
Gate 21.999dz: run current AMA missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 2198bc2, oxjobs eddf9c5a]
Gate 21.999ea: run current Karger missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 4427b24, oxjobs 69b2780a]
Gate 21.999eb: run current APS missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab cf3d845, oxjobs 5da73adb]
Gate 21.999ec: run current ACM missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab dba7e2f, oxjobs 88c2fddb]
Gate 21.999ed: run current Optica missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 1b0823d, oxjobs f57bad44]
Gate 21.999ee: run current IOP missing-PDF no-storage provider probe from the refreshed full gate. [done, taxicab 8aaf717, oxjobs bd7396fb]
Gate 21.999ef: run all-current IOP missing-PDF no-storage confirmation from the refreshed full gate. [done, taxicab ad609f7, oxjobs 51b4665a]
Gate 21.999eg: implement narrow IOP article-PDF route candidate on branch only. [done, taxicab 07c8f95]
Gate 21.999eh: publish IOP route candidate validation to oxjobs #461 and sync handoff docs. [done, oxjobs c3c9b0ac]
Gate 21.999ei: run BMJ 25-row current missing-PDF no-storage confirmation from the refreshed full gate. [done, taxicab 622512f, oxjobs e5b648f6]
Gate 21.999ej: run RSC 25-row current missing-PDF no-storage confirmation from the refreshed full gate. [done, taxicab 05b1a38, oxjobs 84f1c8ea]
Gate 21.999ek: run APS 25-row current missing-PDF no-storage confirmation from the refreshed full gate. [done, taxicab 576c058, oxjobs 5435e2c7]
Gate 21.999el: run ACM 25-row current missing-PDF no-storage confirmation from the refreshed full gate. [done, taxicab 26f35ea, oxjobs 88b3d53f]
Gate 21.999em: implement narrow ACM PDF-byte route candidate on branch only. [done, taxicab 39fa9c2, oxjobs 695fb51d]
Gate 21.999en: publish readable encrypted full gate and sync handoff docs. [done, taxicab 3b07f3e, oxjobs 2092c008]
Gate 21.999eo: cluster readable-encrypted residuals and probe current corrupt clusters. [done, local no-storage probes: Wiley 9/18, ACS 6/6, Sage 0/6]
Gate 21.999ep: implement and publish narrow ACS PDF-byte route candidate on branch only. [done, taxicab 6d11e24, oxjobs 82e4812f, local validation acs-http-get-local-route-precommit-8912673 recovered 6/6]
Gate 21.999eq: run Hindawi current corrupt no-storage provider probe. [done, taxicab 6d11e24, oxjobs 66cc6c44, hindawi-current-corrupt-provider-probe2-6d11e24 recovered 0/2]
Gate 21.999er: run Springer current corrupt no-storage provider probe. [done, taxicab d1f3edb, oxjobs 79f0b3d2, springer-current-corrupt-provider-probe5-6d11e24 recovered 0/5]
Gate 21.999es: run Elsevier-attributed current corrupt no-storage provider probe. [done, taxicab 9b795af, oxjobs f57d9036, elsevier-current-corrupt-provider-probe3-d1f3edb recovered 0/3]
Gate 21.999et: run unknown-attribution current corrupt no-storage provider probe. [done, taxicab 48f425c, oxjobs ffb66370, unknown-current-corrupt-provider-probe5-9b795af recovered 0/5]
Gate 21.999eu: run unknown `revistas.uach.cl` current corrupt no-storage provider probe. [done, taxicab f52b57e, oxjobs 37926446, unknown-revistasuach-current-corrupt-provider-probe1-48f425c recovered 0/1]
Gate 21.999ev: run unknown `journal.uniga.ac.id` current corrupt no-storage provider probe. [done, taxicab 7a00e39, oxjobs aec51cf8, unknown-journaluniga-current-corrupt-provider-probe1-f52b57e recovered 1/1]
Gate 21.999ew: run unknown `sciresol.s3.us-east-2.amazonaws.com` current corrupt no-storage provider probe. [done, taxicab 815a979, oxjobs ca6e5e05, unknown-sciresol-current-corrupt-provider-probe1-7a00e39 recovered 0/1]
Gate 21.999ex: run unknown `oejournal.org` current corrupt no-storage provider probe. [done, taxicab d1106f7, oxjobs 42da202d, unknown-oejournal-current-corrupt-provider-probe1-815a979 recovered 0/1]
Gate 21.999ey: run unknown `authorea.com` current corrupt no-storage provider probe. [done, taxicab 60ac8e3, oxjobs b405108f, unknown-authorea-current-corrupt-provider-probe1-d1106f7 recovered 0/1]
Gate 21.999ez: run unknown `mjle.journals.ekb.eg` current corrupt no-storage provider probe. [done, taxicab add6ef1, oxjobs b6a214a5, unknown-mjle-current-corrupt-provider-probe1-60ac8e3 recovered 0/1]
Gate 21.999fa: publish residual cluster refresh after unknown corrupt singleton tail. [done, taxicab 586189b, oxjobs cea24883, residual-clusters-after-unknown-tail-add6ef1 found 3,989 non-good rows across 174 clusters]
Gate 21.999fb: publish candidate-host residual clustering for missing-PDF rows. [done, taxicab a230505, oxjobs 65411a6c, top concrete hosts link.springer.com 813, onlinelibrary.wiley.com 544, degruyterbrill.com 199, sciencedirect.com 143, api.taylorfrancis.com 52]
Gate 21.999fc: run Taylor API host-specific no-storage provider probe. [done, taxicab cc6689c, oxjobs 48ffd7d9, 0/10 good_pdf, all 40 attempts download_404, no Taxicab POST/R2/DynamoDB writes]
Gate 21.999fd: run Taylor direct TandF host-specific no-storage provider probe. [done, taxicab ae2655d, oxjobs cca3d122, 0/10 good_pdf, best categories 9 interstitial_or_paywall and 1 js_redirect_unresolved, no Taxicab POST/R2/DynamoDB writes]
Gate 21.999fe: publish route-shape residual subclusters. [done, taxicab 1b303a5, oxjobs 106a93f8, residual-subclusters-after-taylor-1b303a5, 1,481 path-pattern subclusters, no KPI lift]
Gate 21.999ff: publish prioritized route-shape subclusters. [done, taxicab fffb10f, oxjobs df99a77f, residual-subclusters-prioritized-fffb10f, top-160 bands: 105 provider-lane, 29 gold-first, 17 fresh probes]
Gate 21.999ff2: publish normalized prioritized route-shape subclusters. [done, taxicab 30121a7, oxjobs c28d77b7, residual-subclusters-prioritized-30121a7, top-160 bands: 113 provider-lane, 30 gold-first, 8 fresh probes]
Gate 21.999ff3: run and publish first fresh-tail direct-PDF candidate loop. [done, taxicab f6e9c80, oxjobs 7b551e72, unifsa-current-missing-provider-probe2-f6e9c80 recovered 2/2 direct PDF bytes; DOI-only reharvest 0/2; direct-PDF-URL reharvest/read-only confirmation 2/2]
Gate 21.999ff4: run and publish second fresh-tail direct-PDF candidate loop. [done, taxicab 8edb8ac, oxjobs 2d9bed14, turkishstudies-current-missing-provider-probe2-8edb8ac recovered 1/2 direct PDF bytes; direct-PDF-URL reharvest/read-only confirmation 1/2; one upstream download_404]
Gate 21.999ff5: run and publish third fresh-tail direct-PDF candidate loop. [done, taxicab 828c377, oxjobs 3f09cbf8, even3-current-missing-provider-probe2-828c377 recovered 2/2 direct PDF bytes; direct-PDF-URL reharvest/read-only confirmation 2/2]
Gate 21.999ff6: run and publish fourth fresh-tail no-storage candidate loop. [done, taxicab 85443df, oxjobs fcb43925, asha-current-missing-provider-probe2-85443df recovered 0/2; one bot_block_403 and one html_instead_of_pdf; no reharvest]
Gate 21.999ff7: run and publish fifth fresh-tail no-storage candidate loop. [done, taxicab fed64e3, oxjobs 3a2e3903, pmresearch-current-missing-provider-probe2-fed64e3 recovered 0/2; one empty_response and one js_redirect_unresolved; no reharvest]
Gate 21.999ff8: run and publish sixth fresh-tail no-storage candidate loop. [done, taxicab 3f70f96, oxjobs 9d011684, mapsmla-current-missing-provider-probe2-3f70f96 recovered 0/2; all tested strategies empty_response; no reharvest]
Gate 21.999ff9: run and publish seventh fresh-tail no-storage candidate loop. [done, taxicab 54052bb, oxjobs 02bc9a19, journalijar-current-missing-provider-probe2-54052bb recovered 0/2; all tested strategies download_404; no reharvest]
Gate 21.999fg: add Browserbase PDF download-start evidence handling. [done, taxicab bdcc38a, no production scraping behavior change]
Gate 21.999fh: refresh residual clusters after rank61 and publish post-rank61 branch confirmations. [done, oxjobs dbe90e51, ACM 15/19 current missing recovered through local no-storage http_get, ACS 0/19 current missing, Wiley 0/8 current corrupt]
Gate 21.999fi: run ACM already-good preservation proof from the rank61 full gate. [done, taxicab bf64d87, oxjobs b9f5c28e, 5/6 preserved and 1/6 regressed to js_redirect_unresolved; ACM route promotion blocked]
Gate 21.999fj: run rank61 Browserbase/Zyte gold sample. [done, taxicab 18e2a76, oxjobs 079cf28f, Browserbase 0/5 PDFs, paired Zyte provider probe 0/1; negative gold evidence only]
Gate 21.999fk: choose next non-duplicate residual lane or provider-advised PDF-byte recipe. [done, taxicab 7f3dc9a, oxjobs b8ef1f42, IngentaConnect no-storage provider probe recovered 0/2 and becomes provider/access-flow evidence only]
Gate 21.999fl: choose another non-duplicate residual lane or provider-advised PDF-byte recipe. [done, taxicab 1fbdc57, oxjobs dcbec19c, ICE Virtual Library no-storage provider probe recovered 0/2 and becomes provider/access-flow evidence only]
Gate 21.999fm: choose another non-duplicate residual lane or provider-advised PDF-byte recipe. [done, taxicab 4d76a3c, oxjobs 261d973d, Ecologica no-storage provider probe recovered 0/2 and becomes provider/access-flow evidence only]
Gate 21.999fn: choose another non-duplicate residual lane or provider-advised PDF-byte recipe. [done, taxicab b1da453, oxjobs 808fc018, ASTM Compass no-storage provider probe recovered 0/2 and becomes provider/access-flow evidence only]
Gate 21.999fo: choose another non-duplicate residual lane or provider-advised PDF-byte recipe. [done, taxicab d2c69a2, oxjobs 48758ccb, CCCC no-storage provider probe recovered 0/2 and becomes provider/access-flow evidence only]
Gate 21.999fp: choose another non-duplicate residual lane or provider-advised PDF-byte recipe. [done, taxicab 3b13642, oxjobs 9263ff09, Atlantis Press no-storage provider probe recovered 2/2; direct-PDF-URL reharvest/read-only confirmation preserved 2/2; full gate accepted +2 with 0 regressions]
Gate 21.999fq: refresh residual clusters after Atlantis. [done, taxicab 12edf68, oxjobs f84e7931, planning-only refresh found 3,910 non-good rows across 655 clusters and 1,426 subclusters; no accepted KPI lift]
Gate 21.999fr: reconcile residual prior-evidence mapping before the next provider probe. [done, taxicab ebfbda7, oxjobs 7aacac3f, provider-lane/do-not-duplicate 156->195, probe_next 42->2, no accepted KPI lift]
Gate 21.999fs: run Mattech/EDP bounded no-storage provider probe and mark it as prior provider evidence. [done, taxicab e9cec98, oxjobs 27cef9f9, recovered 0/2, provider-lane/do-not-duplicate now 196, probe_next now 1, no accepted KPI lift]
Gate 21.999ft: run bioRxiv/CSHLP bounded no-storage provider probe and branch route confirmation. [done, taxicab 3c80154, oxjobs 05596e21, provider probe recovered 1/2, branch http_get recovered 2/2, production reharvest recovered 0/1, top-240 probe_next now 0, no accepted KPI lift]
Gate 21.999fu: demote ACS residual branch lane after current confirmation. [done, taxicab 4256097, oxjobs 37e7fc47, current branch http_get recovered 0/19 ACS residual rows, ACS moved to provider-lane/do-not-duplicate, confirm_existing_branch_candidate now 7, no accepted KPI lift]
Gate 21.999fv: run ACM already-good preservation before branch promotion. [done, taxicab f106e20, oxjobs 1127bc8b, 0/6 already-good rows preserved and 6/6 regressed, ACM moved to provider-lane/do-not-duplicate, confirm_existing_branch_candidate now 5, no accepted KPI lift]
Gate 21.999fw: run Wiley already-good preservation before any branch promotion. [done, taxicab 3a599cd, oxjobs 276fc6a3, 0/12 already-good rows preserved and 12/12 regressed to empty_response, Wiley moved to provider-lane/do-not-duplicate, confirm_existing_branch_candidate now 2, no accepted KPI lift]
Gate 21.999fx: run IOP already-good preservation before any branch promotion. [done, taxicab 6741b06, oxjobs b2d97360, 11/12 already-good rows preserved but 1/12 regressed to bot_block_403, IOP moved to provider-lane/do-not-duplicate, confirm_existing_branch_candidate now 1, no accepted KPI lift]
Gate 21.999fy: run bioRxiv/CSHLP already-good preservation before any branch promotion. [done, taxicab ba5c3a6, oxjobs 6e7a3158, 2/12 already-good rows preserved and 10/12 regressed, bioRxiv/CSHLP moved to provider-lane/do-not-duplicate, confirm_existing_branch_candidate now 0, no accepted KPI lift]
Gate 21.999fz: choose a non-route provider/gold/validator residual lane. [next, no Taxicab main push]
Gate 22: push verified PDF production changes to Taxicab main after >=95% gate and full regression proof.
```

## Latest Accepted Metrics

```text
HTML accepted full gate:
  run_id: full10k-mdpi-jbc-preprints-clean-e22b60e
  good_html: 9,583 / 10,000
  good_html_rate: 95.83%
  rows_above_95: 83
  latest lift: +135 good_html rows
  regressions: 0 good-to-non-good
  taxicab_error: 0
  timeout: 0

Recovered in latest gate:
  MDPI: +119
  Elsevier/JBC: +8
  Rxiv/Preprints: +8

PDF:
  full 10K baseline: 2,148/10,000 good_pdf (21.48%)
  denominator-enriched full baseline: 1,837/6,293 good_pdf (29.19%)
  latest accepted full gate: pdf-full10k-after-readable-encrypted-f2da963, 2,304/6,293 good_pdf (36.61%)
  latest accepted lift: +467 good_pdf vs denominator baseline, +99 vs unknown-refresh gate
  readable-encrypted note: validator/measurement correctness for PDFs with EOF, nonzero pages, and >=500 extracted text chars; encrypted_or_unreadable_pdf dropped from 104 to 4
  latest focused evidence: residual-clusters-candidate-host-a230505 splits 3,989 non-good rows by candidate host; top concrete hosts are link.springer.com 813, onlinelibrary.wiley.com 544, degruyterbrill.com 199, sciencedirect.com 143, journals.lww.com 133, academic.oup.com 132, cambridge.org 122, papers.ssrn.com 73, jstor.org 60, and api.taylorfrancis.com 52
  latest implementation candidates: 3b2d218 taxicab: fetch Wiley pdfdirect as PDF bytes; 07c8f95 taxicab: fetch IOP article PDFs as bytes; Taxicab commit 39fa9c2 ACM /doi/pdf byte route implemented on branch; Taxicab commit 6d11e24 ACS /doi/pdf byte route implemented on branch
  local candidate validation: Wiley 13/19 current residual rows classified good_pdf through local http_get; IOP article-PDF route validation `iop-http-get-local-route-precommit` returned 11/16 good_pdf and 5 bot_block_403; ACM route validation `acm-http-get-local-route-precommit-1950532` returned 5/22 classifier good_pdf, 4/22 strict URL-match recoveries, one candidate-DOI mismatch, and no Taxicab POST/R2/DynamoDB writes; ACS route validation `acs-http-get-local-route-precommit-8912673` returned 6/6 good_pdf with no Taxicab POST/R2/DynamoDB writes
  latest oxjobs publication: 02bc9a19 #461 taxicab-pdf: publish journalijar fresh tail evidence
  latest follow-up probes: Wiley /doi/pdf as-is 0/10; Wiley rewrite-to-pdfdirect 2/10 with one DOI mismatch; Springer content/pdf 0/10; ScienceDirect current missing 0/10 after host-filter normalization; combined Zyte packet refreshed
  current code slice: publisher classification uses source PDF URL/candidate PDF URL host fallback; accepted full-gate missing_pdf_harvest unknown-publisher rows drop from 966 to 642, measurement/reporting-only
  current read-only refresh: pdf-full10k-after-readable-encrypted-f2da963 at taxicab f2da963, 2,304/6,293 good_pdf (36.61%), +99 current read-only movement, 3,796 missing_pdf_harvest, 65 corrupt_or_truncated_pdf, 4 encrypted_or_unreadable_pdf, 0 timeout, 0 taxicab_error, 3,675-row gap to 95%; validator/measurement lift, not production scraping-code lift
  latest provider probe: taylor-tandfonline-current-missing-provider-probe10-ae2655d at taxicab ae2655d recovered 0/10 current tandfonline.com missing rows; best categories were 9 interstitial_or_paywall and 1 js_redirect_unresolved; both Taylor API and direct TandF residuals stay in provider/Zyte support before route code
  latest planning slice: residual-subclusters-prioritized-30121a7 at taxicab 30121a7 and oxjobs c28d77b7 normalizes prior-evidence host variants and keeps priority bands on 1,481 normalized path-pattern subclusters; top 160 split into 113 provider-lane/do-not-duplicate, 30 Browserbase/Zyte-gold-first, 8 fresh probes, 4 existing branch candidates, 4 validator/provider lanes, 1 inspect-first; accepted KPI stays 2,304/6,293 good_pdf (36.61%)
  latest bounded lift: unifsa-current-missing-provider-probe2-f6e9c80 recovered 2/2 direct PDF bytes, turkishstudies-current-missing-provider-probe2-8edb8ac recovered 1/2 direct PDF bytes, and even3-current-missing-provider-probe2-828c377 recovered 2/2 direct PDF bytes; direct-PDF-URL reharvest/read-only confirmation preserved 5/6 across those three fresh-tail loops; asha-current-missing-provider-probe2-85443df, pmresearch-current-missing-provider-probe2-fed64e3, mapsmla-current-missing-provider-probe2-3f70f96, and journalijar-current-missing-provider-probe2-54052bb recovered 0/2 each, so they move to provider/upstream evidence; accepted full gate stays 2,304/6,293 until a full gate confirms the cache lift
  no_pdf_expected: 3,707
  denominator-enriched gap to 95%: 3,675 rows on current accepted refresh
  dominant category: 3,796 missing_pdf_harvest
  other major categories: 93 supplement_or_preview_pdf; 65 corrupt_or_truncated_pdf; 4 encrypted_or_unreadable_pdf
  timeout: 0
  taxicab_error: 0
  run_id: pdf-full10k-readonly-22b78b7
  denominator run_id: pdf-full10k-denominator-3f7cd47
  denominator-enriched limit-100: 13/65 good_pdf (20.00%); 35 no_pdf_expected
  reharvest smoke: pdf-reharvest-smoke-8193c47, 0/5 good_pdf; 3 corrupt_or_truncated_pdf; 2 missing_pdf_harvest; 0 timeout; 0 taxicab_error
  springer seed reharvest: pdf-springer-missing-reharvest-12, 1/12 good_pdf; 11 missing_pdf_harvest; 0 timeout; 0 taxicab_error
  springer post-context reharvest: pdf-springer-missing-reharvest-12-post-context-b9d5918, 1/12 good_pdf; 11 missing_pdf_harvest; all 11 missing rows have POST status 201, post content_type html, and resolved Springer article/chapter/rwe HTML URLs
  springer no-storage Zyte two-step probe: failed sample still returned HTML, not PDF; treat as Zyte support candidate before production code changes
  browserbase credential source: ignored /Users/shubh-trips/Documents/OpenAlex/parseland-eval/eval/.env contains BROWSERBASE_API_KEY; Taxicab .env/.env.aws do not
  browserbase evidence commit: f424129 taxicab: add pdf browserbase evidence mode
  springer browserbase smoke: pdf-browserbase-springer-1-f424129, verdict html_not_pdf for 10.1007/978-1-4419-6247-8_15015; final URL https://link.springer.com/rwe/10.1007/978-1-4419-6247-8_15015; content_type text/html; not PDF
  row-timeout watchdog commit: be2f5c7 taxicab: add pdf row timeout watchdog
  elsevier missing queue: 25 true missing_pdf_harvest rows generated from pdf-full10k-denominator-3f7cd47
  elsevier interrupted sample: 23/25 rows completed before KeyboardInterrupt; 4 good_pdf, 6 corrupt_or_truncated_pdf, 13 missing_pdf_harvest, 0 timeout/taxicab_error among completed rows
  elsevier bounded sample: pdf-elsevier-missing-reharvest-25-84b2c05 resumed with --row-timeout 120; 4/25 good_pdf, 15 missing_pdf_harvest, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  elsevier read-only confirmation: pdf-elsevier-missing-readonly-after-reharvest-be2f5c7, 4/25 good_pdf, 21 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  elsevier note: the four recovered rows are durable sample records; Elsevier still needs route-specific/provider work before any broad production claim
  elsevier 100-row reharvest: pdf-elsevier-missing-reharvest-100-41d0378, 6/100 good_pdf, 48 missing_pdf_harvest, 45 corrupt_or_truncated_pdf, 1 timeout, 0 taxicab_error
  elsevier 100-row corrected read-only: pdf-elsevier-missing-readonly-previewfix-9b7d84b, 7/100 good_pdf, 92 missing_pdf_harvest, 1 supplement_or_preview_pdf, 0 timeout, 0 taxicab_error
  preview classifier fix: first-page-pdf URLs classify as supplement_or_preview_pdf, not good_pdf
  oxjobs #461 commit: 3d8a5fa0 #461 taxicab-pdf: publish elsevier 100 gate
  oxjobs #461 route split commit: 825c2e2d #461 taxicab-pdf: add elsevier route split
  elsevier route split: 34 ScienceDirect route rows, 23 journal-host/long-tail rows, 11 invalid-PDF POST rows, 8 Lancet rows, 7 durable recoveries, 5 cross-publisher candidates, 4 DOI-router candidates, 4 direct-asset rows, 3 Cell Press rows, 1 preview row
  sciencedirect probe commit: 741e9a7 taxicab: add sciencedirect pdf probe
  sciencedirect probe run: sciencedirect-route-probe-3-741e9a7, 3 DOI candidates, 12 variants, 0 good_pdf, best category html_instead_of_pdf for 3/3
  oxjobs #461 sciencedirect probe commit: 666d0ed6 #461 taxicab-pdf: record sciencedirect probe
  lancet probe run: lancet-route-probe-3-741e9a7, 3 DOI candidates, 3 variants, 0 good_pdf, 2 empty_response, 1 download_404
  oxjobs #461 lancet probe commit: 2105c8f1 #461 taxicab-pdf: record lancet probe
  cell probe run: cell-route-probe-3-741e9a7, 3 DOI candidates, 3 variants, 0 good_pdf, 3 js_redirect_unresolved
  oxjobs #461 cell probe commit: a160ec1a #461 taxicab-pdf: record cell probe
  cell Browserbase evidence: pdf-browserbase-cell-1-3de630f, 1 DOI candidate, Browserbase verdict html_not_pdf, browserbase_available false
  oxjobs #461 Cell Browserbase commit: d0344d1d #461 taxicab-pdf: record cell browserbase evidence
  Cell Browserbase publication note: only scrubbed summary is public because the raw final URL contained a Cloudflare challenge token
  wiley bounded reharvest: pdf-wiley-missing-reharvest-25-4267740, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  wiley finding: POST returned status 201 but captured HTML landing pages at Wiley DOI routes, not PDF bytes
  oxjobs #461 Wiley provider packet commit: 3d7356bc #461 taxicab-pdf: add wiley provider packet
  combined provider request: evidence/zyte-support/pdf-byte-fetch-provider-request-4267740.md covers ScienceDirect, Lancet, Cell, and Wiley
  de gruyter bounded reharvest: pdf-degruyter-missing-reharvest-25-95308b7, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  de gruyter finding: POST accepted HTML /html pages; direct no-storage /pdf probes returned JS robot-verification HTML
  oxjobs #461 De Gruyter provider packet commit: de7d0f2d #461 taxicab-pdf: add degruyter provider packet
  combined provider request now covers ScienceDirect, Lancet, Cell, Wiley, and De Gruyter
  lippincott bounded reharvest: pdf-lippincott-missing-reharvest-25-0405edf, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  lippincott finding: POST accepted article/abstract HTML pages; direct no-storage downloadpdf.aspx probes returned secured-browser HTML
  oxjobs #461 Lippincott provider packet commit: b88a5a79 #461 taxicab-pdf: add lippincott provider packet
  combined provider request now covers ScienceDirect, Lancet, Cell, Wiley, De Gruyter, and Lippincott
  oxford bounded reharvest: pdf-oxford-missing-reharvest-25-b259f2e, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxford finding: POST accepted article/abstract HTML pages; direct no-storage article-pdf probes returned Zyte 520 empty responses
  oxjobs #461 Oxford provider packet commit: e1fe9deb #461 taxicab-pdf: add oxford provider packet
  combined provider request now covers ScienceDirect, Lancet, Cell, Wiley, De Gruyter, Lippincott, and Oxford
  cup/cambridge bounded reharvest: pdf-cup-missing-reharvest-25-39517e5, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  cup/cambridge finding: POST accepted Cambridge Core HTML pages; direct no-storage explicit PDF probes returned status 200 text/html Cambridge Core pages, not PDF bytes
  oxjobs #461 CUP/Cambridge provider packet commit: df7784c9 #461 taxicab-pdf: add cup provider packet
  combined provider request now covers ScienceDirect, Lancet, Cell, Wiley, De Gruyter, Lippincott, Oxford, and CUP/Cambridge
  cup/cambridge strategy probe: cup-zyte-strategy-probe-1-26d3d5c, 0 PDF bodies across default HTTP, PDF Accept header, residential variants, and browser network capture
  oxjobs #461 CUP/Cambridge strategy probe commit: 77e793a8 #461 taxicab-pdf: record cup strategy probe
  ssrn bounded reharvest: pdf-ssrn-missing-reharvest-25-64b787f, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  ssrn finding: POST mostly accepted SSRN HTML delivery/landing pages; direct delivery probes returned SSRN HTML or removed-paper HTML
  oxjobs #461 SSRN provider packet commit: ade1b60f #461 taxicab-pdf: add ssrn provider packet
  iop bounded reharvest: pdf-iop-missing-reharvest-25-2e2c123, 25 DOI candidates, 16 good_pdf, 6 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 1 timeout, 0 taxicab_error
  iop read-only confirmation: pdf-iop-missing-readonly-after-reharvest-2e2c123, 16 durable good_pdf, 7 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 IOP positive sample commit: 7d376fa0 #461 taxicab-pdf: publish iop positive sample
  after-IOP full gate: pdf-full10k-after-iop-d6fb6bb, 1,861/6,293 good_pdf (29.57%), +24 good_pdf, 3,912 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 after-IOP full gate commit: fbba7e56 #461 taxicab-pdf: publish iop full gate
  remaining IOP read-only confirmation: pdf-iop-remaining45-readonly-e5bcd30, 21 durable good_pdf, 18 missing_pdf_harvest, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  after-remaining-IOP full gate: pdf-full10k-after-iop-remaining-e5bcd30, 1,882/6,293 good_pdf (29.91%), +45 good_pdf, 3,885 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 remaining IOP full gate commit: 5cca142e #461 taxicab-pdf: publish remaining iop gate
  rsc bounded reharvest: pdf-rsc-missing48-reharvest-008fe7f, 48 DOI candidates, 0 good_pdf, 47 missing_pdf_harvest, 1 timeout, 0 taxicab_error
  rsc finding: POST accepted RSC /articlelanding/.../unauth HTML pages instead of articlepdf bytes
  oxjobs #461 RSC provider packet commit: 68025078 #461 taxicab-pdf: add rsc provider packet
  aip bounded reharvest: pdf-aip-missing45-reharvest-8ce7e7e, 45 DOI candidates, 0 good_pdf, 44 missing_pdf_harvest, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  aip finding: POST returned status 201 HTML/no durable PDF for missing rows; one candidate returned invalid PDF content
  oxjobs #461 AIP provider packet commit: 85584ddd #461 taxicab-pdf: add aip provider packet
  taylor mixed sample: pdf-taylor-missing25-readonly-e7d1361, 2/25 durable good_pdf, 23 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  taylor TandF expansion: pdf-taylor-tandfonline29-readonly-e7d1361, 3/29 durable good_pdf, 26 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  taylor full gate: pdf-full10k-after-taylor-e7d1361, 1,887/6,293 good_pdf (29.99%), +5 vs prior gate, 0 regressions, 0 timeout, 0 taxicab_error
  oxjobs #461 Taylor full gate commit: 574539d2 #461 taxicab-pdf: publish taylor full gate
  acs bounded reharvest: pdf-acs-missing25-reharvest-2b7996a, 25 DOI candidates, 0 good_pdf, 19 missing_pdf_harvest, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  acs finding: POST returned status 201 HTML/no durable PDF for most rows; six ACS PDF/EPDF responses failed validation
  oxjobs #461 ACS provider packet commit: 482cc4fd #461 taxicab-pdf: add acs provider packet
  spie bounded reharvest: pdf-spie-missing25-reharvest-62c6a33, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  spie finding: POST returned status 201 HTML/no durable PDF for explicit SPIE PDF/download routes
  oxjobs #461 SPIE provider packet commit: c5792694 #461 taxicab-pdf: add spie provider packet
  thieme bounded reharvest: pdf-thieme-missing25-reharvest-d0ea198, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  thieme finding: POST resolved PDF routes to abstract, ebook lookinside, or Science of Synthesis start-page HTML
  oxjobs #461 Thieme provider packet commit: 8cb377c7 #461 taxicab-pdf: add thieme provider packet
  sage bounded reharvest: pdf-sage-missing25-reharvest-2705643, 25 DOI candidates, 0 good_pdf, 11 missing_pdf_harvest, 14 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  sage finding: POST resolved PDF routes to abstract HTML/no durable records or invalid PDF-like responses with no page objects
  oxjobs #461 Sage provider packet commit: ca3b11fe #461 taxicab-pdf: add sage provider packet
  brill bounded reharvest: pdf-brill-missing30-reharvest-7520bc1, 30 DOI candidates, 0 good_pdf, 30 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  brill finding: POST returned status 200 on Brill downloadpdf URLs but no durable PDF records were readable afterward
  oxjobs #461 Brill provider packet commit: 172b7580 #461 taxicab-pdf: add brill provider packet
  ama/jama bounded reharvest: pdf-ama-jama-missing25-reharvest-005b032, 25 DOI candidates, 0 good_pdf, 18 missing_pdf_harvest, 7 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  ama/jama finding: POST returned article HTML/no durable PDF records or invalid PDF-like responses
  oxjobs #461 AMA/JAMA provider packet commit: d82e9ba6 #461 taxicab-pdf: add ama jama provider packet
  aps bounded reharvest: pdf-aps-missing23-reharvest-65feabe, 23 DOI candidates, 0 good_pdf, 23 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  aps finding: POST resolved APS/link.aps.org PDF routes to journals.aps.org article/abstract HTML/no durable PDF records; one candidate resolved to a journals.aps.org PDF URL but still had no readable durable PDF record
  oxjobs #461 APS provider packet commit: 147a9e65 #461 taxicab-pdf: add aps provider packet
  acm bounded reharvest: pdf-acm-missing22-reharvest-5f81111, 22 DOI candidates, 0 good_pdf, 16 missing_pdf_harvest, 5 corrupt_or_truncated_pdf, 1 timeout, 0 taxicab_error
  acm finding: POST returned ACM HTML/no durable PDF records, invalid PDF-like responses, or a row timeout
  oxjobs #461 ACM provider packet commit: 32d6a637 #461 taxicab-pdf: add acm provider packet
  bmj bounded reharvest: pdf-bmj-missing32-reharvest-4c213b6, 32 DOI candidates, 0 good_pdf, 31 missing_pdf_harvest, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  bmj finding: POST returned BMJ article HTML/no durable PDF records or one invalid PDF-like response
  oxjobs #461 BMJ provider packet commit: 3319e184 #461 taxicab-pdf: add bmj provider packet
  karger bounded reharvest: pdf-karger-missing28-reharvest-9a8466e, 28 DOI candidates, 3 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  karger read-only confirmation: pdf-karger-missing28-readonly-9a8466e, 3 durable good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  karger finding: modern karger.com article-pdf routes can persist real PDFs; residual rows resolve to article-abstract HTML/no durable PDF record with redirectedFrom=PDF
  oxjobs #461 Karger provider packet commit: ecae684b #461 taxicab-pdf: add karger recovery packet
  karger full gate: pdf-full10k-after-karger-ca8b132, 1,890/6,293 good_pdf (30.03%), +3 vs prior gate, +53 vs denominator baseline, 0 good-to-non-good regressions, 0 timeout, 0 taxicab_error
  oxjobs #461 Karger full gate commit: 5ccb3df5 #461 taxicab-pdf: publish karger full gate
  optica/opg bounded reharvest: pdf-optica-missing21-reharvest-25496ec, 21 DOI candidates, 0 good_pdf, 21 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  optica/opg finding: POST returned status 201 HTML/no durable PDF records for opg.optica.org/viewmedia.cfm routes
  oxjobs #461 Optica provider packet commit: 826bd689 #461 taxicab-pdf: add optica provider packet
  jstor bounded reharvest: pdf-jstor-missing60-reharvest-dc6cafc, 60 DOI candidates, 0 good_pdf, 60 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  jstor finding: POST returned status 201 HTML/no durable PDF records for www.jstor.org/stable/pdf routes
  oxjobs #461 JSTOR provider packet commit: 19ca1aff #461 taxicab-pdf: add jstor provider packet
  inlibra bounded reharvest: pdf-inlibra-missing32-reharvest-54d17e9, 32 DOI candidates, 0 good_pdf, 32 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  inlibra finding: POST returned status 201 HTML/no durable PDF records for www.inlibra.com/document/download/pdf/uuid routes
  oxjobs #461 Inlibra provider packet commit: 0df48262 #461 taxicab-pdf: add inlibra provider packet
  scientificnet bounded reharvest: pdf-scientificnet-missing20-reharvest-4e6130f, 20 DOI candidates, 0 good_pdf, 20 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  scientificnet finding: POST returned status 201 HTML/no durable PDF records for www.scientific.net PDF routes
  oxjobs #461 Scientific.net provider packet commit: 3b84fb4b #461 taxicab-pdf: add scientificnet provider packet
  persee bounded reharvest: pdf-persee-missing18-reharvest-af4baf7, 18 DOI candidates, 0 good_pdf, 18 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  persee finding: reharvest returned invalid PDF content for www.persee.fr/docAsPDF routes
  oxjobs #461 Persee provider packet commit: 1a7d1ddb #461 taxicab-pdf: add persee provider packet
  nature bounded reharvest: pdf-nature-missing17-reharvest-e7616c9, 17 DOI candidates, 2 good_pdf, 15 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  nature read-only confirmation: pdf-nature-missing17-readonly-e7616c9, 2 durable good_pdf, 15 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Nature provider packet commit: 33c8c71c #461 taxicab-pdf: add nature recovery packet
  jstage bounded reharvest: pdf-jstage-missing16-reharvest-43777d8, 16 DOI candidates, 2 good_pdf, 8 corrupt_or_truncated_pdf, 1 encrypted_or_unreadable_pdf, 4 missing_pdf_harvest, 1 timeout, 0 taxicab_error
  jstage read-only confirmation: pdf-jstage-missing16-readonly-43777d8, 2 durable good_pdf, 8 corrupt_or_truncated_pdf, 1 encrypted_or_unreadable_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 J-STAGE provider packet commit: 59789f72 #461 taxicab-pdf: add jstage recovery packet
  uchicago bounded reharvest: pdf-uchicago-missing16-reharvest-6b41e44, 16 DOI candidates, 0 good_pdf, 16 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  uchicago finding: POST accepted HTML/no durable PDF records for journals.uchicago.edu doi/pdf and doi/epdf routes, commonly resolving to doi/abs article pages
  oxjobs #461 UChicago provider packet commit: 95bde36b #461 taxicab-pdf: add uchicago provider packet
  asme bounded reharvest: pdf-asme-missing15-reharvest-c1c2b86, 15 DOI candidates, 0 good_pdf, 8 corrupt_or_truncated_pdf, 7 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  asme finding: POST returned invalid PDF-like content or HTML/no durable PDF records for asmedigitalcollection.asme.org article/proceedings PDF routes
  oxjobs #461 ASME provider packet commit: 10d80d80 #461 taxicab-pdf: add asme provider packet
  cairn bounded reharvest: pdf-cairn-missing20-reharvest-8742847, 20 DOI candidates, 0 good_pdf, 19 corrupt_or_truncated_pdf, 1 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  cairn finding: POST returned invalid PDF-like content or HTML/no durable PDF records for shs.cairn.info and www.cairn.info PDF routes
  oxjobs #461 Cairn provider packet commit: 97b61e38 #461 taxicab-pdf: add cairn provider packet
  physiology bounded reharvest: pdf-physiology-missing11-reharvest-6db1728, 11 DOI candidates, 0 good_pdf, 5 corrupt_or_truncated_pdf, 6 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  physiology finding: POST returned invalid PDF-like content or HTML/no durable PDF records for journals.physiology.org PDF routes
  oxjobs #461 Physiology provider packet commit: 33d5cb5b #461 taxicab-pdf: add physiology provider packet
  asce bounded reharvest: pdf-asce-missing10-reharvest-e708434, 10 DOI candidates, 0 good_pdf, 5 corrupt_or_truncated_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  asce finding: POST returned invalid PDF-like content or HTML/no durable PDF records for ascelibrary.org PDF routes
  oxjobs #461 ASCE provider packet commit: b57dba2f #461 taxicab-pdf: add asce provider packet
  pdcnet bounded reharvest: pdf-pdcnet-missing9-reharvest-9cd3b93, 9 DOI candidates, 0 good_pdf, 9 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  pdcnet finding: POST returned HTML purchase/form captures and no durable PDF records for pdcnet.org PDF routes
  oxjobs #461 PDCNet provider packet commit: a1663d3f #461 taxicab-pdf: add pdcnet provider packet
  eurekaselect bounded reharvest: pdf-eurekaselect-missing8-reharvest-d224066, 8 DOI candidates, 0 good_pdf, 6 corrupt_or_truncated_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  eurekaselect finding: POST returned invalid PDF-like content or HTML/no durable PDF records for eurekaselect.com article routes
  oxjobs #461 EurekaSelect provider packet commit: 357c4ee1 #461 taxicab-pdf: add eurekaselect provider packet
  actahort bounded reharvest: pdf-actahort-missing8-reharvest-8ce7ac3, 8 DOI candidates, 0 good_pdf, 8 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  actahort finding: POST returned status-201 HTML/no durable PDF records for www.actahort.org/members/showpdf routes
  oxjobs #461 ActaHort provider packet commit: be526662 #461 taxicab-pdf: add actahort provider packet
  vr-elibrary bounded reharvest: pdf-vr-elibrary-missing7-reharvest-fdfa16c, 7 DOI candidates, 0 good_pdf, 6 missing_pdf_harvest, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  vr-elibrary finding: reader routes resolved to abstract HTML/no durable PDF records and one explicit PDF route returned invalid PDF-like content
  oxjobs #461 V&R eLibrary provider packet commit: c3d3b00b #461 taxicab-pdf: add vr-elibrary provider packet
  iwaponline bounded reharvest: pdf-iwaponline-missing7-reharvest-bfa43c4, 7 DOI candidates, 0 good_pdf, 7 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  iwaponline finding: explicit article-pdf routes resolved to article-abstract HTML with redirectedFrom=PDF and no durable PDF records
  oxjobs #461 IWA Publishing provider packet commit: 98a037c1 #461 taxicab-pdf: add iwaponline provider packet
  ametsoc bounded reharvest: pdf-ametsoc-missing7-reharvest-29cf658, 7 DOI candidates, 0 good_pdf, 7 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  ametsoc finding: explicit downloadpdf/view routes returned status 200 but no durable readable PDF records
  oxjobs #461 AMS journals provider packet commit: 8fe1d510 #461 taxicab-pdf: add ametsoc provider packet
  jpet/aspet bounded reharvest: pdf-jpet-missing7-reharvest-0dd85b6, 7 DOI candidates, 0 good_pdf, 6 corrupt_or_truncated_pdf, 1 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  jpet/aspet finding: explicit article PDF routes returned invalid PDF-like content or no durable readable PDF records
  oxjobs #461 JPET/ASPET provider packet commit: ae72a1ff #461 taxicab-pdf: add jpet provider packet
  onepetro bounded reharvest: pdf-onepetro-missing7-reharvest-92f581e, 7 DOI candidates, 0 good_pdf, 7 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  onepetro finding: explicit article/proceedings PDF routes resolved to HTML/no durable PDF records
  oxjobs #461 OnePetro provider packet commit: 029f9ac9 #461 taxicab-pdf: add onepetro provider packet
  liebertpub bounded reharvest: pdf-liebertpub-missing7-reharvest-b5e1678, 7 DOI candidates, 0 good_pdf, 5 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  liebertpub finding: explicit Liebert PDF/reader routes resolved to Sage-hosted HTML/no durable PDF records or invalid PDF content
  oxjobs #461 Mary Ann Liebert provider packet commit: c9eafb75 #461 taxicab-pdf: add liebertpub provider packet
  aacr figshare bounded reharvest: pdf-aacr-figshare-missing6-reharvest-8f674aa, 6 DOI candidates, 0 good_pdf, 6 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  aacr figshare finding: Figshare downloader/PDF routes produced status-201 HTML/no durable PDF records
  oxjobs #461 AACR Figshare provider packet commit: dd7ab56d #461 taxicab-pdf: add aacr figshare provider packet
  ampp bounded reharvest: pdf-ampp-missing6-reharvest-851bd3f, 6 DOI candidates, 0 good_pdf, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  ampp finding: content.ampp.org article-pdf/proceedings-pdf routes returned invalid PDF-like content rather than complete PDF bytes
  oxjobs #461 AMPP provider packet commit: ef843caa #461 taxicab-pdf: add ampp provider packet
  healio bounded reharvest: pdf-healio-missing6-reharvest-51c7ad1, 6 DOI candidates, 0 good_pdf, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  healio finding: journals.healio.com epdf routes returned invalid PDF-like content rather than complete PDF bytes
  oxjobs #461 Healio provider packet commit: 64517b97 #461 taxicab-pdf: add healio provider packet
  sage knowledge bounded reharvest: pdf-sage-knowledge-missing10-reharvest-bef0376, 10 DOI candidates, 0 good_pdf, 10 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  sage knowledge finding: sk.sagepub.com download PDF routes returned invalid PDF-like content rather than complete PDF bytes
  oxjobs #461 Sage Knowledge provider packet commit: 79af39d8 #461 taxicab-pdf: add sage knowledge provider packet
  igi global bounded reharvest: pdf-igi-global-missing6-reharvest-14746e2, 6 DOI candidates, 1 good_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  igi global read-only confirmation: pdf-igi-global-missing6-readonly-14746e2, 1 durable good_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 IGI Global provider packet commit: 471f9ee3 #461 taxicab-pdf: add igi global recovery packet
  uc press bounded reharvest: pdf-ucpress-missing6-reharvest-dd1a528, 6 DOI candidates, 0 good_pdf, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 UC Press provider packet commit: e435bc5e #461 taxicab-pdf: add ucpress provider packet
  rupress bounded reharvest: pdf-rupress-missing6-reharvest-76fb88d, 6 DOI candidates, 1 good_pdf, 4 missing_pdf_harvest, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  rupress read-only confirmation: pdf-rupress-missing6-readonly-76fb88d, 1 durable good_pdf, 4 missing_pdf_harvest, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 RUPress provider packet commit: fa847b5a #461 taxicab-pdf: add rupress recovery packet
  emerald bounded reharvest: pdf-emerald-missing6-reharvest-e3fdbea, 6 DOI candidates, 0 good_pdf, 6 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 Emerald provider packet commit: f191f0eb #461 taxicab-pdf: add emerald provider packet
  jacc bounded reharvest: pdf-jacc-missing6-reharvest-9e16fb8, 6 DOI candidates, 0 good_pdf, 6 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 JACC provider packet commit: eea013bf #461 taxicab-pdf: add jacc provider packet
  ajo bounded reharvest: pdf-ajo-missing6-reharvest-a30f12a, 6 DOI candidates, 0 good_pdf, 5 corrupt_or_truncated_pdf, 1 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 AJO provider packet commit: a72d7c09 #461 taxicab-pdf: add ajo provider packet
  bioone bounded reharvest: pdf-bioone-missing5-reharvest-1d9e18f, 5 DOI candidates, 0 good_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 BioOne provider packet commit: b60d7147 #461 taxicab-pdf: add bioone provider packet
  canadian science publishing bounded reharvest: pdf-cdnsciencepub-missing5-reharvest-2a121b2, 5 DOI candidates, 0 good_pdf, 3 corrupt_or_truncated_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Canadian Science provider packet commit: 634173b9 #461 taxicab-pdf: add canadian science provider packet
  edward elgar bounded reharvest: pdf-elgaronline-missing5-reharvest-8244033, 5 DOI candidates, 1 good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  edward elgar read-only confirmation: pdf-elgaronline-missing5-readonly-8244033, 1 durable good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Edward Elgar provider packet commit: 9771940c #461 taxicab-pdf: add edward elgar recovery packet
  american concrete institute bounded reharvest: pdf-concrete-missing5-reharvest-d38b219, 5 DOI candidates, 0 good_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 American Concrete Institute provider packet commit: 9fbae749 #461 taxicab-pdf: add concrete provider packet
  american journal of surgery bounded reharvest: pdf-americanjournalofsurgery-missing5-reharvest-93479bd, 5 DOI candidates, 0 good_pdf, 3 corrupt_or_truncated_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 American Journal of Surgery provider packet commit: 1b4912ec #461 taxicab-pdf: add american journal of surgery packet
  ajog bounded reharvest: pdf-ajog-missing5-reharvest-831503a, 5 DOI candidates, 1 good_pdf, 4 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  ajog read-only confirmation: pdf-ajog-missing5-readonly-831503a, 1 durable good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 AJOG provider packet commit: 2e492500 #461 taxicab-pdf: add ajog recovery packet
  scholarly publishing collective bounded reharvest: pdf-scholarlypublishingcollective-missing5-reharvest-a9fdacb, 5 DOI candidates, 0 good_pdf, 4 corrupt_or_truncated_pdf, 1 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Scholarly Publishing Collective provider packet commit: 362d2b2f #461 taxicab-pdf: add scholarly publishing collective packet
  royal society publishing bounded reharvest: pdf-royalsocietypublishing-missing5-reharvest-1d0fac0, 5 DOI candidates, 0 good_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Royal Society Publishing provider packet commit: cfeb6d34 #461 taxicab-pdf: add royal society provider packet
  koreascience bounded reharvest: pdf-koreascience-missing5-reharvest-35d3541, 5 DOI candidates, 0 good_pdf, 5 timeout, 0 taxicab_error
  oxjobs #461 KoreaScience provider packet commit: 53c6d7fe #461 taxicab-pdf: add koreascience timeout packet
  journal of pharmaceutical sciences bounded reharvest: pdf-jpharmsci-missing5-reharvest-3b7bf15, 5 DOI candidates, 0 good_pdf, 5 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Journal of Pharmaceutical Sciences provider packet commit: c1f26ec8 #461 taxicab-pdf: add jpharmsci provider packet
  chest bounded reharvest: pdf-chestnet-missing5-reharvest-4c6cd17, 5 DOI candidates, 1 good_pdf, 4 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  chest read-only confirmation: pdf-chestnet-missing5-readonly-4c6cd17, 1 durable good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 CHEST provider packet commit: ee27cd5e #461 taxicab-pdf: add chestnet recovery packet
  green journal bounded reharvest: pdf-thegreenjournal-missing4-reharvest-a211471, 4 DOI candidates, 0 good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Green Journal provider packet commit: 0e0bb05f #461 taxicab-pdf: add green journal provider packet
  scielo bounded reharvest: pdf-scielo-missing4-reharvest-7d2c782, 4 DOI candidates, 2 good_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  scielo read-only confirmation: pdf-scielo-missing4-readonly-7d2c782, 2 durable good_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 SciELO provider packet commit: 41a903e6 #461 taxicab-pdf: add scielo recovery packet
  aip pubs.aip.org bounded reharvest: pdf-pubs-aip-missing25-reharvest-751ad63, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 AIP pubs.aip.org provider packet commit: b7940463 #461 taxicab-pdf: add pubs aip provider packet
  doi-router bounded reharvest: pdf-doi-org-missing19-reharvest-659e13e, 19 DOI candidates, 0 good_pdf, 17 missing_pdf_harvest, 2 timeout, 0 taxicab_error
  oxjobs #461 DOI-router provider packet commit: 4c711418 #461 taxicab-pdf: add doi router provider packet
  sciencedirectassets bounded reharvest: pdf-sciencedirectassets-missing6-reharvest-16bcb5a, 6 DOI candidates, 0 good_pdf, 6 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 ScienceDirect assets provider packet commit: 58ab0e73 #461 taxicab-pdf: add sciencedirect assets packet
  springer link bounded reharvest: pdf-springer-link-missing25-reharvest-d401917, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Springer link provider packet commit: 469a996b #461 taxicab-pdf: add springer link provider packet
  degruyterbrill bounded reharvest: pdf-degruyterbrill-missing25-reharvest-f2c5e99, 25 DOI candidates, 0 good_pdf, 25 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 De Gruyter Brill residual packet commit: ddb8a16f #461 taxicab-pdf: add degruyterbrill residual packet
  aiaa bounded reharvest: pdf-aiaa-missing4-reharvest-2faaaa2, 4 DOI candidates, 0 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 AIAA tail packet commit: 83c0b0fe #461 taxicab-pdf: add aiaa tail packet
  neurology bounded reharvest: pdf-neurology-missing4-reharvest-42dc6f4, 4 DOI candidates, 0 good_pdf, 3 missing_pdf_harvest, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 RSNA tail packet commit: 67a5b554 #461 taxicab-pdf: add rsna tail packet
  goldjournal bounded reharvest: pdf-goldjournal-missing4-reharvest-91c0c88, 4 DOI candidates, 0 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 Gold Journal tail packet commit: 8d1c57b4 #461 taxicab-pdf: add gold journal tail packet
  atsjournals bounded reharvest: pdf-atsjournals-missing4-reharvest-a618e5a, 4 DOI candidates, 0 good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 ATS Journals tail packet commit: 7e4dcc79 #461 taxicab-pdf: add ats journals tail packet
  transcript-verlag corrected read-only: pdf-transcript-verlag-missing4-readonly-previewfix-43ab357, 4 DOI candidates, 0 accepted good_pdf, 4 supplement_or_preview_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 Transcript Verlag correction commit: 433d621e #461 taxicab-pdf: add transcript preview correction
  PNAS bounded reharvest: pdf-pnas-missing4-reharvest-3d943cf, 4 DOI candidates, 0 accepted good_pdf, 4 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 PNAS packet commit: 8ff5fd14 #461 taxicab-pdf: add pnas tail packet
  Peter Lang bounded reharvest: pdf-peterlang-missing4-reharvest-eb523da, 4 DOI candidates, 0 accepted good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Peter Lang packet commit: a12417e1 #461 taxicab-pdf: add peter lang tail packet
  Nomos eLibrary bounded reharvest: pdf-nomos-elibrary-missing4-reharvest-b4bbab0, 4 DOI candidates, 0 accepted good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 Nomos packet commit: d7d1220d #461 taxicab-pdf: add nomos elibrary tail packet
  JPedsurg bounded reharvest: pdf-jpedsurg-missing4-reharvest-66bf4f1, 4 DOI candidates, 0 accepted good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 JPedsurg packet commit: d6c52a5b #461 taxicab-pdf: add jpedsurg tail packet
  JBC bounded reharvest: pdf-jbc-missing4-reharvest-83f5456, 4 DOI candidates, 0 accepted good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  oxjobs #461 JBC packet commit: c5a71e38 #461 taxicab-pdf: add jbc tail packet
  ADS bounded reharvest: pdf-adsabs-missing4-reharvest-1b03675, 4 DOI candidates, 4 accepted good_pdf, 0 timeout, 0 taxicab_error
  ADS read-only confirmation: pdf-adsabs-missing4-readonly-1b03675, 4 durable good_pdf, 0 timeout, 0 taxicab_error
  oxjobs #461 ADS recovery commit: 34c32f5f #461 taxicab-pdf: add adsabs recovery
  NCTM bounded reharvest: pdf-nctm-missing4-reharvest-97bcaa1, 4 DOI candidates, 1 accepted good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  NCTM read-only confirmation: pdf-nctm-missing4-readonly-97bcaa1, 1 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  NCTM finding: downloadpdf/view recovered one durable PDF; downloadpdf/journals routes stored XML article HTML with no durable PDF records
  oxjobs #461 NCTM recovery commit: 877d1107 #461 taxicab-pdf: add nctm recovery
  AAAHQ bounded reharvest: pdf-aaahq-missing4-reharvest-7f47ce9, 4 DOI candidates, 0 accepted good_pdf, 3 corrupt_or_truncated_pdf, 1 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  AAAHQ read-only confirmation: pdf-aaahq-missing4-readonly-7f47ce9, 0 durable good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  AAAHQ finding: three article-pdf routes returned invalid PDF content; one route stored article abstract HTML with redirectedFrom=PDF; no durable readable PDF records persisted
  oxjobs #461 AAAHQ packet commit: 63789cfc #461 taxicab-pdf: add aaahq tail packet
  EJSO bounded reharvest: pdf-ejso-missing4-reharvest-30ce1b5, 4 DOI candidates, 0 accepted good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  EJSO read-only confirmation: pdf-ejso-missing4-readonly-30ce1b5, 0 durable good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  EJSO finding: every candidate /pdf route resolved to article /abstract HTML with status-201 HTML and no durable PDF record
  oxjobs #461 EJSO packet commit: fc590d0f #461 taxicab-pdf: add ejso tail packet
  AUA Journals bounded reharvest: pdf-auajournals-missing4-reharvest-465c495, 4 DOI candidates, 0 accepted good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  AUA Journals read-only confirmation: pdf-auajournals-missing4-readonly-465c495, 0 durable good_pdf, 4 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  AUA Journals finding: every candidate PDF/EPDF route resolved to article DOI HTML with status-201 HTML and no durable PDF record
  oxjobs #461 AUA Journals packet commit: 16f51e88 #461 taxicab-pdf: add auajournals tail packet
  Springer Publishing bounded reharvest: pdf-springerpub-missing3-reharvest-3720861, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Springer Publishing read-only confirmation: pdf-springerpub-missing3-readonly-3720861, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Springer Publishing finding: every candidate PDF route resolved to article/book/chapter HTML with status-201 HTML and no durable PDF record
  oxjobs #461 Springer Publishing packet commit: d56b9fac #461 taxicab-pdf: add springerpub tail packet
  Vestnik/KRSU bounded reharvest: pdf-vestnik-krsu-missing3-reharvest-d39e366, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Vestnik/KRSU read-only confirmation: pdf-vestnik-krsu-missing3-readonly-d39e366, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Vestnik/KRSU finding: every candidate article/download route resolved to archive HTML with status-201 HTML and no durable PDF record
  oxjobs #461 Vestnik/KRSU packet commit: 5a217501 #461 taxicab-pdf: add vestnik krsu tail packet
  Duke University Press bounded reharvest: pdf-dukeupress-missing3-reharvest-c04d081, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Duke University Press read-only confirmation: pdf-dukeupress-missing3-readonly-c04d081, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Duke University Press finding: every candidate article-pdf route resolved to article abstract HTML with redirectedFrom=fulltext and no durable PDF record
  oxjobs #461 Duke University Press packet commit: 1e18ffdd #461 taxicab-pdf: add dukeupress tail packet
  GeoScienceWorld bounded reharvest: pdf-geoscienceworld-missing3-reharvest-98bb851, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  GeoScienceWorld read-only confirmation: pdf-geoscienceworld-missing3-readonly-98bb851, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  GeoScienceWorld finding: every candidate article-pdf route resolved to article abstract HTML with redirectedFrom=fulltext and no durable PDF record
  oxjobs #461 GeoScienceWorld packet commit: b3ba464e #461 taxicab-pdf: add geoscienceworld tail packet
  Indian Journals bounded reharvest: pdf-indianjournals-missing6-reharvest-dcadb4a, 6 DOI candidates, 0 accepted good_pdf, 6 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Indian Journals read-only confirmation: pdf-indianjournals-missing6-readonly-dcadb4a, 0 durable good_pdf, 6 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Indian Journals finding: every candidate PDF/API route resolved to HTML article pages with status-201 HTML and no durable PDF record
  oxjobs #461 Indian Journals packet commit: f4e4fe37 #461 taxicab-pdf: add indianjournals tail packet
  AJConline bounded reharvest: pdf-ajconline-missing3-reharvest-261a3ca, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  AJConline read-only confirmation: pdf-ajconline-missing3-readonly-261a3ca, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  AJConline finding: every candidate article PDF route resolved to article abstract HTML with status-201 HTML and no durable PDF record
  oxjobs #461 AJConline packet commit: b4b2a251 #461 taxicab-pdf: add ajconline tail packet
  IATED bounded reharvest: pdf-iated-missing3-reharvest-4a1e0d9, 3 DOI candidates, 0 accepted good_pdf, 3 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  IATED read-only confirmation: pdf-iated-missing3-readonly-4a1e0d9, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  IATED finding: every download route returned status-400 invalid PDF content and no durable PDF record
  oxjobs #461 IATED packet commit: 2fb1349a #461 taxicab-pdf: add iated tail packet
  Brepols bounded reharvest: pdf-brepolsonline-missing3-reharvest-d690cd3, 3 DOI candidates, 0 accepted good_pdf, 3 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  Brepols read-only confirmation: pdf-brepolsonline-missing3-readonly-d690cd3, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Brepols finding: every doi/epdf route returned status-400 invalid PDF content and no durable PDF record
  oxjobs #461 Brepols packet commit: 9918c055 #461 taxicab-pdf: add brepols tail packet
  oxjobs #461 report allowlist fix: 6a85359b #461 taxicab-pdf: expose recent tail artifacts
  Copernicus bounded reharvest: pdf-copernicus-meetingorganizer-missing3-reharvest-638dd13, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest after POST accepted HTML captures, 0 timeout, 0 taxicab_error
  Copernicus read-only confirmation: pdf-copernicus-meetingorganizer-missing3-readonly-638dd13, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Copernicus finding: every `*.html?pdf` route stored article HTML and no durable PDF record
  oxjobs #461 Copernicus packet commit: 4bc7763f #461 taxicab-pdf: add copernicus tail packet
  Google Drive bounded reharvest: pdf-google-drive-missing3-reharvest-47e462f, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest after POST accepted HTML captures, 0 timeout, 0 taxicab_error
  Google Drive read-only confirmation: pdf-google-drive-missing3-readonly-47e462f, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Google Drive finding: every `drive.google.com/file/d/.../view` route stored viewer HTML and no durable PDF record
  oxjobs #461 Google Drive packet commit: 3bd2e947 #461 taxicab-pdf: add google drive tail packet
  protocols.io bounded reharvest: pdf-protocols-io-missing3-reharvest-bc519d2, 3 DOI candidates, 2 accepted good_pdf, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  protocols.io read-only confirmation: pdf-protocols-io-missing3-readonly-bc519d2, 2 durable good_pdf, 1 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error
  protocols.io finding: direct PDF routes are recoverable for 2/3 rows; the residual row returns PDF bytes but fails validation with no page objects
  oxjobs #461 protocols.io recovery commit: 95fd1945 #461 taxicab-pdf: add protocols io recovery
  ASA/Scitation bounded reharvest: pdf-asa-scitation-missing3-reharvest-724b48e, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest after POST accepted HTML captures, 0 timeout, 0 taxicab_error
  ASA/Scitation read-only confirmation: pdf-asa-scitation-missing3-readonly-724b48e, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  ASA/Scitation finding: direct `asa.scitation.org/doi/pdf/...` routes stored article HTML and no durable PDF record
  oxjobs #461 ASA/Scitation packet commit: d457927c #461 taxicab-pdf: add asa scitation tail packet
  IOS Press bounded reharvest: pdf-iospress-missing3-reharvest-c08a1e4, 3 DOI candidates, 0 accepted good_pdf, 2 corrupt_or_truncated_pdf invalid responses, 1 missing_pdf_harvest after POST accepted HTML capture, 0 timeout, 0 taxicab_error
  IOS Press read-only confirmation: pdf-iospress-missing3-readonly-c08a1e4, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  IOS Press finding: explicit `content.iospress.com/download/...` routes returned invalid PDF content; one DOI redirected to Sage-hosted `/doi/pdf/...` HTML/no-record capture
  oxjobs #461 IOS Press packet commit: 930c773c #461 taxicab-pdf: add iospress tail packet
  AAI Journals bounded reharvest: pdf-aai-journals-missing3-reharvest-24795ac, 3 DOI candidates, 0 accepted good_pdf, 3 missing_pdf_harvest after POST accepted HTML captures, 0 timeout, 0 taxicab_error
  AAI Journals read-only confirmation: pdf-aai-journals-missing3-readonly-24795ac, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  AAI Journals finding: explicit `journals.aai.org/article-pdf/...` routes stored HTML/no durable PDF records
  oxjobs #461 AAI Journals packet commit: ebff6475 #461 taxicab-pdf: add aai journals tail packet
  JCVA Online bounded reharvest: pdf-jcvaonline-missing3-reharvest-dc3bba1, 3 DOI candidates, 0 accepted good_pdf, 2 missing_pdf_harvest after abstract-HTML captures, 1 corrupt_or_truncated_pdf invalid response, 0 timeout, 0 taxicab_error
  JCVA Online read-only confirmation: pdf-jcvaonline-missing3-readonly-dc3bba1, 0 durable good_pdf, 3 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  JCVA Online finding: two article PDF routes resolved to abstract HTML/no durable PDF records; one candidate returned invalid PDF content
  oxjobs #461 JCVA Online packet commit: e48d73e8 #461 taxicab-pdf: add jcvaonline tail packet
  Human Kinetics bounded reharvest: pdf-humankinetics-missing3-reharvest-bbd2225, 3 DOI candidates, 1 accepted good_pdf, 2 missing_pdf_harvest after XML article HTML captures, 0 timeout, 0 taxicab_error
  Human Kinetics read-only confirmation: pdf-humankinetics-missing3-readonly-bbd2225, 1 durable good_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  Human Kinetics finding: one `downloadpdf/view` route persisted as a durable PDF; two residual rows resolved to XML article HTML/no durable PDF records
  oxjobs #461 Human Kinetics packet commit: 93b383f6 #461 taxicab-pdf: add humankinetics recovery packet
  Human Kinetics full gate: pdf-full10k-after-humankinetics-bbd2225, 1,910/6,293 good_pdf (30.35%), +20 vs Karger, +73 vs denominator baseline, 0 good-to-non-good regressions, 0 timeout, 0 taxicab_error
  oxjobs #461 Human Kinetics full-gate commit: 43ca3830 #461 taxicab-pdf: publish humankinetics full gate
  structured parser full gate: pdf-full10k-after-structured-parser-a61d34b, 2,193/6,293 good_pdf (34.85%), +283 net vs Human Kinetics, +356 vs denominator baseline, 363 recovered, 80 stricter supplement/preview reclassifications, 0 timeout, 0 taxicab_error
  oxjobs #461 structured parser full-gate commit: dcb7bb14 #461 taxicab-pdf: publish structured parser gate
  Wiley residual 5-row provider probe: wiley-residual-corrupt-provider-probe-5-a61d34b, 3/5 good_pdf, one empty_response, one supplement_or_preview_pdf, no Taxicab POST/R2/DynamoDB writes; oxjobs #461 commit 9569e1f6
  Wiley residual all-row provider probe: wiley-residual-corrupt-provider-probe-19-a61d34b, 15/19 good_pdf, with two empty_response, one bot_block_403, and one supplement_or_preview_pdf residual; no Taxicab POST/R2/DynamoDB writes; oxjobs #461 commit 6ba84787
  Wiley PDF-direct implementation candidate: Taxicab commit 3b2d218, local no-storage http_get validation 13/19 good_pdf on the same residual rows, no production deploy yet
  oxjobs candidate publication: d4f99eee #461 taxicab-pdf: publish Wiley pdfdirect candidate
  next lane: decide a bounded confirmation path that does not push Taxicab main before the full PDF 95% proof
  offline fixture smoke: 15 categories represented
  live smoke: 1/5 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf
  live smoke after EOF/concurrent runner: 3/5 good_pdf, 2 missing_pdf_harvest, 0 timeout, 0 taxicab_error
  limit-100 initial: 1/100 good_pdf, 77 missing_pdf_harvest, 19 corrupt_or_truncated_pdf, 2 encrypted_or_unreadable_pdf, 1 bot_block_403
  limit-100 corrected after EOF validator fix: 15/100 good_pdf, 77 missing_pdf_harvest, 5 corrupt_or_truncated_pdf, 2 encrypted_or_unreadable_pdf, 1 bot_block_403
  note: the 1/100 -> 15/100 lift is measurement/validator correctness, not production scraping behavior.
  target denominator: pdf_expected_total
```

## Required Commit Loop

Every meaningful slice must use this loop:

```bash
git status --short
# make scoped changes
# run focused tests/checks
git add <owned files>
git commit -m "<specific message>"
git pull --rebase
git push
```

Taxicab production behavior changes require targeted eval plus full no-regression
proof before pushing to `main`.

Oxjobs uses `main` as the reporting source of truth. Push report/docs changes
to oxjobs `main` frequently after checks.

## Last Verification

```text
Taxicab main-sync commit: 07c974e
python3 -m unittest discover -s tests: 54 tests passed
python3 scripts/taxicab_eval.py --fixture-smoke --out /tmp/taxicab-fixture-smoke: passed, 20 fixtures, 11 categories
python3 scripts/taxicab_eval.py --smoke --out /tmp/taxicab-html-main-sync-smoke: passed, 8 rows, 0 timeout, 0 taxicab_error
git diff --cached --check: passed
secret pattern scan: no raw secret pattern findings

PDF harness setup:
python3 -m unittest discover -s tests: 62 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke --out /tmp/taxicab-pdf-fixture-smoke: passed, 15 fixtures, 15 categories
git diff --check: passed
secret pattern scan: no raw secret pattern findings

PDF read-only live smoke:
python3 -m unittest discover -s tests: 64 tests passed
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --run-id pdf-live-smoke --out /tmp/taxicab-pdf-live-smoke --timeout 30 --retries 1 --progress-every 1: passed
result: 5 rows; 1 good_pdf, 2 missing_pdf_harvest, 2 corrupt_or_truncated_pdf, 0 timeout, 0 taxicab_error

PDF limit-100 read-only baseline:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out pdf_eval_runs/ --run-id pdf-limit100-readonly-6661cde --timeout 45 --retries 1 --progress-every 10: passed
result: 1/100 good_pdf; 77 missing_pdf_harvest; 19 corrupt_or_truncated_pdf; 2 encrypted_or_unreadable_pdf; 1 bot_block_403; 0 timeout; 0 taxicab_error

PDF EOF validator correction:
python3 -m unittest tests.test_pdf_eval_harness: 11 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-eof --out /tmp/taxicab-pdf-fixture-smoke-eof: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out pdf_eval_runs/ --run-id pdf-limit100-readonly-eof-fix --timeout 45 --retries 1 --progress-every 10: passed
result: 15/100 good_pdf; 77 missing_pdf_harvest; 5 corrupt_or_truncated_pdf; 2 encrypted_or_unreadable_pdf; 1 bot_block_403; 0 timeout; 0 taxicab_error

PDF concurrent read-only runner:
python3 -m unittest discover -s tests: 66 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-workers --out /tmp/taxicab-pdf-fixture-smoke-workers: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --smoke --run-id pdf-live-smoke-workers-358111f --out /tmp/taxicab-pdf-live-smoke-workers --timeout 30 --retries 1 --workers 4 --progress-every 1: passed
result: 5 rows; 3 good_pdf; 2 missing_pdf_harvest; 0 timeout; 0 taxicab_error

PDF full 10K read-only baseline:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --out pdf_eval_runs/ --run-id pdf-full10k-readonly-22b78b7 --workers 8 --timeout 45 --retries 1 --progress-every 100: passed
result: 2,148/10,000 good_pdf (21.48%); 7,230 missing_pdf_harvest; 453 corrupt_or_truncated_pdf; 121 encrypted_or_unreadable_pdf; 13 html_instead_of_pdf; 13 js_redirect_unresolved; 11 supplement_or_preview_pdf; 9 interstitial_or_paywall; 2 bot_block_403; 0 timeout; 0 taxicab_error

PDF denominator enrichment:
python3 -m unittest discover -s tests: 68 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-denominator --out /tmp/taxicab-pdf-fixture-smoke-denominator: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 100 --out pdf_eval_runs/ --run-id pdf-limit100-denominator --workers 8 --timeout 45 --retries 1 --progress-every 10: passed
result: pdf_expected_total 65; 13 good_pdf; 35 no_pdf_expected; 45 missing_pdf_harvest; 5 corrupt_or_truncated_pdf; 1 encrypted_or_unreadable_pdf; 1 bot_block_403; 0 timeout; 0 taxicab_error

PDF denominator-enriched full 10K baseline:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --out pdf_eval_runs/ --run-id pdf-full10k-denominator-3f7cd47 --workers 8 --timeout 45 --retries 1 --progress-every 100: passed
result: 1,837/6,293 good_pdf (29.19%); 3,707 no_pdf_expected; 3,939 missing_pdf_harvest; 373 corrupt_or_truncated_pdf; 102 encrypted_or_unreadable_pdf; 11 html_instead_of_pdf; 11 js_redirect_unresolved; 10 supplement_or_preview_pdf; 8 interstitial_or_paywall; 2 bot_block_403; 0 timeout; 0 taxicab_error

PDF reharvest mode:
python3 -m unittest discover -s tests: 69 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-reharvest --out /tmp/taxicab-pdf-fixture-smoke-reharvest: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --limit 5 --reharvest --workers 2 --out /tmp/taxicab-pdf-reharvest-smoke --run-id pdf-reharvest-smoke-5 --timeout 45 --retries 1 --progress-every 1: passed
result: 0/5 good_pdf; 3 corrupt_or_truncated_pdf from Taxicab invalid-PDF POST responses; 2 missing_pdf_harvest after read-back; 0 timeout; 0 taxicab_error

PDF Springer seed queue:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv --reharvest --workers 2 --out pdf_eval_runs/ --run-id pdf-springer-missing-reharvest-12 --timeout 60 --retries 1 --progress-every 1: passed
result: 1/12 good_pdf; 11 missing_pdf_harvest; recovered DOI 10.1007/bf03544238; 0 timeout; 0 taxicab_error

PDF reharvest POST-context instrumentation:
python3 -m unittest tests.test_pdf_eval_harness: 16 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-post-context --out /tmp/taxicab-pdf-fixture-smoke-post-context: passed, 15 fixtures, 15 categories
python3 -m unittest discover -s tests: 70 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-post-context-final --out /tmp/taxicab-pdf-fixture-smoke-post-context-final: passed, 15 fixtures, 15 categories
git diff --check: passed
secret pattern scan: no raw secret pattern findings

PDF Springer post-context seed rerun:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv --reharvest --workers 2 --out pdf_eval_runs/ --run-id pdf-springer-missing-reharvest-12-post-context-b9d5918 --timeout 60 --retries 1 --progress-every 1: passed
result: 1/12 good_pdf; 11 missing_pdf_harvest; 11/11 misses had POST status 201 and post content_type html

PDF Browserbase evidence mode:
python3 -m unittest tests.test_pdf_eval_harness: 17 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-browserbase-mode --out /tmp/taxicab-pdf-fixture-smoke-browserbase-mode: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/springer-missing-12.csv --limit 1 --with-browserbase --browserbase-mode session --browserbase-timeout 60 --out pdf_eval_runs/ --run-id pdf-browserbase-springer-1-f424129 --timeout 30 --retries 1 --progress-every 1: passed with ignored Parseland env Browserbase key
result: Browserbase verdict html_not_pdf; browserbase_available false; final URL was Springer RWE HTML page, not PDF

PDF row-timeout watchdog:
python3 -m unittest tests.test_pdf_eval_harness: 18 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-row-timeout --out /tmp/taxicab-pdf-fixture-smoke-row-timeout: passed, 15 fixtures, 15 categories
python3 -m unittest discover -s tests: 72 tests passed
git diff --check: passed
secret pattern scan: no raw secret pattern findings

PDF Elsevier bounded missing sample:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-25.csv --reharvest --workers 2 --row-timeout 120 --resume --out pdf_eval_runs/ --run-id pdf-elsevier-missing-reharvest-25-84b2c05 --timeout 60 --retries 1 --progress-every 1: passed
result: 4/25 good_pdf; 15 missing_pdf_harvest; 6 corrupt_or_truncated_pdf; 0 timeout; 0 taxicab_error

PDF Elsevier read-only confirmation:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-25.csv --out pdf_eval_runs/ --run-id pdf-elsevier-missing-readonly-after-reharvest-be2f5c7 --workers 4 --row-timeout 120 --timeout 60 --retries 1 --progress-every 1: passed
result: 4/25 good_pdf; 21 missing_pdf_harvest; 0 timeout; 0 taxicab_error

PDF preview URL classifier:
python3 -m unittest tests.test_pdf_eval_harness: 19 tests passed
python3 scripts/taxicab_pdf_eval.py --fixture-smoke --run-id pdf-fixture-smoke-preview-url --out /tmp/taxicab-pdf-fixture-smoke-preview-url: passed, 15 fixtures, 15 categories
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/elsevier-missing-100.csv --out pdf_eval_runs/ --run-id pdf-elsevier-missing-readonly-previewfix-9b7d84b --workers 4 --row-timeout 120 --timeout 60 --retries 1 --progress-every 10: passed
result: 7/100 good_pdf; 92 missing_pdf_harvest; 1 supplement_or_preview_pdf; 0 timeout; 0 taxicab_error

PDF Cell Browserbase evidence reporting:
oxjobs python3 scripts/publish-report.py 461: passed
oxjobs git diff --check -- working/taxicab-pdf: passed
oxjobs strict secret/token scan including signed-URL and Cloudflare challenge-token patterns: no findings
result: public scrubbed summary published at oxjobs commit d0344d1d; raw Browserbase evidence remains local

PDF Wiley bounded sample reporting:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/wiley-missing-25.csv --reharvest --workers 2 --row-timeout 120 --out pdf_eval_runs/ --run-id pdf-wiley-missing-reharvest-25-4267740 --timeout 60 --retries 1 --progress-every 1: passed
result: 0/25 good_pdf; 25 missing_pdf_harvest; 0 timeout; 0 taxicab_error
oxjobs python3 scripts/publish-report.py 461: passed
oxjobs git diff --check -- working/taxicab-pdf: passed
oxjobs strict secret/token scan including signed-URL, Browserbase session/path, and Cloudflare challenge-token patterns: no findings
result: public scrubbed summary/report and provider request published at oxjobs commit 3d7356bc

PDF De Gruyter bounded sample reporting:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/degruyter-missing-25.csv --reharvest --workers 2 --row-timeout 120 --out pdf_eval_runs/ --run-id pdf-degruyter-missing-reharvest-25-95308b7 --timeout 60 --retries 1 --progress-every 1: passed
result: 0/25 good_pdf; 25 missing_pdf_harvest; 0 timeout; 0 taxicab_error
De Gruyter no-storage direct PDF probe: 3/3 returned js_redirect_unresolved, status 202, text/html, JS/robot-verification evidence
oxjobs python3 scripts/publish-report.py 461: passed
oxjobs git diff --check -- working/taxicab-pdf: passed
oxjobs strict secret/token scan including signed-URL, Browserbase session/path, and Cloudflare challenge-token patterns: no findings
result: public scrubbed summary/report and provider request published at oxjobs commit de7d0f2d

PDF Lippincott bounded sample reporting:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/lippincott-missing-25.csv --reharvest --workers 2 --row-timeout 120 --out pdf_eval_runs/ --run-id pdf-lippincott-missing-reharvest-25-0405edf --timeout 60 --retries 1 --progress-every 1: passed
result: 0/25 good_pdf; 25 missing_pdf_harvest; 0 timeout; 0 taxicab_error
Lippincott no-storage direct PDF probe: 3/3 returned bot_block_403, status 200, text/html, secured-browser evidence
oxjobs python3 scripts/publish-report.py 461: passed
oxjobs git diff --check -- working/taxicab-pdf: passed
oxjobs strict secret/token scan including signed-URL, Browserbase session/path, and Cloudflare challenge-token patterns: no findings
result: public scrubbed summary/report and provider request published at oxjobs commit b88a5a79

PDF Oxford bounded sample reporting:
python3 scripts/taxicab_pdf_eval.py --base-url http://harvester-load-balancer-366186003.us-east-1.elb.amazonaws.com --doi-file /Users/shubh-trips/Documents/OpenAlex/oxjobs/working/taxicab-pdf/evidence/oxford-missing-25.csv --reharvest --workers 2 --row-timeout 120 --out pdf_eval_runs/ --run-id pdf-oxford-missing-reharvest-25-b259f2e --timeout 60 --retries 1 --progress-every 1: passed
result: 0/25 good_pdf; 25 missing_pdf_harvest; 0 timeout; 0 taxicab_error
Oxford no-storage direct PDF probe: 3/3 returned empty_response, status 520, no body
oxjobs python3 scripts/publish-report.py 461: passed
oxjobs git diff --check -- working/taxicab-pdf: passed
oxjobs strict secret/token scan including signed-URL, Browserbase session/path, and Cloudflare challenge-token patterns: no findings
result: public scrubbed summary/report and provider request published at oxjobs commit e1fe9deb
```

## Provider Policy

```text
Zyte:
  production retrieval core.

Browserbase:
  evidence, recoverability checks, and gold-sample collection only.
  not a production fallback unless explicitly approved later.

Secrets:
  never print or commit key/token/cookie values.
  local ignored .env and .env.aws can be loaded without echoing values.
```

## Do Not

```text
Do not use /Users/shubh-trips/Documents/openalex-taxicab.
Do not mix HTML and PDF KPIs.
Do not put PDF Phase 2 results into #133 as the primary report.
Do not use Browserbase as production fallback.
Do not print secrets, signed URLs, cookies, or decrypted AWS secret values.
Do not push broad production scraping changes without full regression proof.
```
