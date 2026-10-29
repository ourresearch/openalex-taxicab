"""What a fetched page is (oxjob #1790, landing-pages charter).

Taxicab used to store any HTTP 200 as a success, so bot walls, login pages and empty app shells were stored,
sent to Parseland and never fetched again. `classify` names the page; walls, logins and shells are not stored
(the harvester reports them with is_soft_block, as it always has for bot walls).

Classes: pdf, html (anything that may be an article or abstract page), pdf_viewer (a browser's PDF-viewer wrapper:
the URL served a PDF; stored), bot_wall, login, shell, error (not a 200).
Markers are body substrings seen on real stored pages (#1790 EXPLORE § 3a) or vendor block pages, chosen to
appear only on the block page itself, never on the normal pages those vendors protect.
"""
import re

BOT_WALL_MARKERS = [
    'ShieldSquare Captcha',
    '429 - Too many requests',
    'We apologize for the inconvenience',
    '<title>APA PsycNet</title>',
    'Your request cannot be processed at this time',
    '/cookieAbsent',
    'Project MUSE -- Verification required!',
    '<div class="frc-captcha"',
    # Anubis proof-of-work challenge (HAL since spring 2026; oxjob #1402)
    'id="anubis_challenge"',
    'Making sure you&#39;re not a bot!',
    # PMC bot checks, both HTTP 200: Google reCAPTCHA challenge page (served in place of ~319K PMC landing
    # pages Apr-Aug 2026) and PMC's "Preparing to download" PDF proof-of-work page
    'RecaptchaChallengePageUi',
    '<title>Checking your browser - reCAPTCHA</title>',
    'cloudpmc-viewer-pow',
    # oxjob #1790:
    # Akamai Bot Manager: meta refresh to ?bm-verify=... (MDPI, 48% of its stored HTML in Oct 2026)
    'bm-verify=',
    # Cloudflare managed challenge
    'window._cf_chl_opt',
    '<title>Just a moment...</title>',
    # DataDome block page (its normal-page tag is js.datadome.co, not this host)
    'captcha-delivery.com',
    # PerimeterX / HUMAN block page
    'id="px-captcha"',
    # Imperva / Distil
    '<title>Pardon Our Interruption</title>',
    # ucc.edu.co and others: "Bot Detection" challenge
    'Please prove that you are Human before accessing this website',
    # F5 BIG-IP access gateway's session-ended page (Leiden's repository, 19.6K stored 22-23 Oct 2026)
    '<title>BIG-IP logout page</title>',
    # Imperva / Incapsula block page: an iframe to the incident resource (spiedigitallibrary.org, 16 of 100
    # stored pages 24-25 Oct 2026); normal Imperva pages load /_Incapsula_Resource?SWJIYLWA= scripts, not this
    '_Incapsula_Resource?SWUDNSAI=',
    # F5 Advanced WAF ("TSPD") JavaScript challenge (ekb.eg, every stored page 24-25 Oct 2026)
    'window["bobcmn"]',
    # Silverchair JS challenge ("Loading...", ~1.5 KB): stored on ~11% of older OUP article pages (#1809)
    'function leastFactor(n)',
    # Silverchair captcha page (ashpublications.org, 1 of 100 stored pages 25-26 Oct 2026)
    '<title>Validate User</title>',
]
# Fastly bot-management "Client Challenge" (3,038 bytes, assets under /_fs-ch-<token>/): Springer Nature
# (nature.com, link.springer.com PDF links, springermedizin.de), JSTOR, eLife, PyPI, Scribd; ~19.8K stored as
# articles Mar-Oct 2026, nature.com almost every fetch from 28 Oct (#1789's alarm, #1790 EXPLORE § 14). Both strings:
# every normal consultant360.com page loads /_fs-ch-<token>/ scripts too.
FASTLY_CHALLENGE = ('<title>Client Challenge</title>', '/_fs-ch-')
# Walls that need every string of a group, for vendors whose single strings could appear on a normal page.
BOT_WALL_MARKER_GROUPS = [FASTLY_CHALLENGE]
# Chrome's PDF-viewer wrapper (271 bytes, no text): what a browser render returns when the URL serves a PDF
# (Elsevier society journals' /article/<PII>/pdf). It is evidence that a PDF was served (#1290 scores it so), so
# it is stored like any page. 125e840 classed it as a wall by mistake (25 Oct 2026, #1790 EXPLORE § 6).
PDF_VIEWER_MARKER = '<!-- the placeholder in the body style is for an optional background-color -->'
# Login pages whose title the login-title rule can't safely catch
LOGIN_MARKERS = [
    '<title>Sign in with subscription number</title>',   # J-STAGE
    'Log in to Bloomsbury Collections</h1>',              # bloomsburycollections.com (title "collections-NN")
    "value='login_required'",                             # RSC's auto-posting OIDC sign-in form (994 bytes)
]
# Redirect targets that are never the page we asked for
WALL_REDIRECTS = ('muse.jhu.edu/verify', 'fbi.gov', '/vdesk/hangup.php3')

# Pages whose title starts with a login phrase followed by the end of the title or a separator.
# ("Login-free authentication: ..." is an article; "Login | Journal" and "Connectez-vous ou créez un
# compte. | Cairn.info" are not.)
_LOGIN_TITLE = re.compile(
    r'<title[^>]*>\s*(?:log ?in|sign ?in|se connecter|connectez-vous[^<]*|iniciar sesi[oó]n|anmelden)'
    r'(?:\s*</title>|\s+[|\-–:]\s|\s*\|)',
    re.IGNORECASE,
)
# An empty custom element used as an app root: <ds-app></ds-app>, <app-root></app-root>, <nde-app-root>, <app-wos>.
# Angular's <router-outlet> is always empty, even on a fully rendered page (its content renders after it), so it
# never counts (taylorfrancis.com chapter pages, 25 Oct 2026).
_EMPTY_APP_ROOT = re.compile(r'<(?!router-outlet\b)([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\b[^>]*>\s*</\1>', re.IGNORECASE)
_CITATION_META = re.compile(r'name=["\']?(?:citation_title|dc\.title|eprints\.title|dcterms\.title)["\']?', re.IGNORECASE)
# Pages that name their item in Open Graph or JSON-LD carry metadata Parseland can read, so they are never
# shells (T&F keeps title, authors and abstract there; the Primo shell's JSON-LD block is empty).
_OG_TITLE = re.compile(r'property=["\']?og:title["\']?', re.IGNORECASE)
_JSON_LD = re.compile(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', re.IGNORECASE | re.DOTALL)
JSON_LD_MIN = 100
_NON_TEXT = re.compile(r'<(script|style|noscript)\b[^>]*>.*?</\1>|<[^>]+>', re.IGNORECASE | re.DOTALL)
SHELL_MAX_TEXT = 200

NOT_STORED = {'bot_wall', 'login', 'shell'}


def _text(content):
    return content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else str(content or '')


def is_bot_wall(content):
    text = _text(content)
    return (any(marker in text for marker in BOT_WALL_MARKERS)
            or any(all(marker in text for marker in group) for group in BOT_WALL_MARKER_GROUPS))


def is_fastly_challenge(content):
    text = _text(content)
    return all(marker in text for marker in FASTLY_CHALLENGE)


def is_shell(text):
    """A client-rendered app with nothing in it yet: an empty app root, no citation, Open Graph or JSON-LD
    metadata, almost no text."""
    if not _EMPTY_APP_ROOT.search(text) or _CITATION_META.search(text) or _OG_TITLE.search(text):
        return False
    if any(len(block.strip()) >= JSON_LD_MIN for block in _JSON_LD.findall(text)):
        return False
    return len(' '.join(_NON_TEXT.sub(' ', text).split())) < SHELL_MAX_TEXT


def classify(content, content_type, status_code, resolved_url=None):
    if content_type == 'pdf':
        return 'pdf'
    if resolved_url and any(target in resolved_url for target in WALL_REDIRECTS):
        return 'bot_wall'
    text = _text(content)
    # markers count on any status, as they always have (a 403 carrying a captcha is a bot wall)
    if is_bot_wall(text):
        return 'bot_wall'
    if status_code == 202:   # Akamai's challenge answer (IEEE): never a page
        return 'bot_wall'
    if status_code != 200:
        return 'error'
    if PDF_VIEWER_MARKER in text[:2000]:
        return 'pdf_viewer'
    if _LOGIN_TITLE.search(text[:20000]) or any(marker in text for marker in LOGIN_MARKERS):
        return 'login'
    if is_shell(text):
        return 'shell'
    return 'html'
