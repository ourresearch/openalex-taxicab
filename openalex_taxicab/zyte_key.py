"""Which Zyte API key a harvest bills to (oxjob #1790).

Campaigns (re-scrapes such as the bronze re-check) send `zyte_key: "<name>"` with each request so
their Zyte calls go to their own API key. That key has its own spending limit in the Zyte dashboard
(billing cycle, "pause processing requests when this limit is reached") and its own line in Zyte's
stats, so a campaign can never spend the main key's budget and stop new-content scraping.

Campaign keys come from the env var ZYTE_CAMPAIGN_KEYS, a JSON object {"campaign-bronze": "<key>"}.
A name that isn't there is refused (UnknownZyteKey), never billed to the main key. Without a name,
every call uses ZYTE_API_KEY as before.

The choice is per thread, like deadline.py: harvest() sets it before fetching and clears it after.
"""
import json
import os
import threading

_local = threading.local()


class UnknownZyteKey(ValueError):
    pass


def _campaign_keys():
    raw = os.environ.get("ZYTE_CAMPAIGN_KEYS", "").strip()
    if not raw:
        return {}
    try:
        keys = json.loads(raw)
    except ValueError:
        # Never echo the value: it holds API keys.
        raise UnknownZyteKey("ZYTE_CAMPAIGN_KEYS is not valid JSON")
    return keys if isinstance(keys, dict) else {}


def use(name=None):
    """Bill this thread's Zyte calls to campaign key `name` (None or "" = the main key)."""
    if not name:
        _local.key = None
        return
    key = _campaign_keys().get(name)
    if not key:
        raise UnknownZyteKey(f"unknown zyte_key {name!r}")
    _local.key = key


def clear():
    _local.key = None


def current():
    """The Zyte API key for a call made now on this thread."""
    return getattr(_local, "key", None) or os.getenv("ZYTE_API_KEY")
