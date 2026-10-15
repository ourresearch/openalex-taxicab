"""Per-request time budget for harvests (oxjob #1712).

The load balancer in front of the harvester hangs up after 60 s, but a worker thread keeps
running until its code returns, and the caller then asks again. One slow page could hold four
threads for minutes and call Zyte each time. Every outbound HTTP call made while a harvest is
in flight now takes its timeout from the time that request has left, and a request that runs
out raises DeadlineExceeded instead of starting another call.

Outside a harvest (scripts, /test-zyte) no budget is active and timeouts pass through unchanged.
"""
import os
import re
import threading
from time import time

# Counted from when the load balancer received the request, so the answer goes back before
# the load balancer's 60 s idle timeout.
REQUEST_BUDGET_SECONDS = float(os.environ.get("TAXICAB_REQUEST_BUDGET_SECONDS", "55"))

# Don't start a call with less than this left: it can't finish anyway.
MIN_CALL_SECONDS = 2.0

# Zyte calls that used to have no timeout at all get this one when no budget is active.
ZYTE_TIMEOUT = (10, 100)

_ALB_TRACE_ROOT = re.compile(r"Root=1-([0-9a-fA-F]{8})-")

_local = threading.local()


class DeadlineExceeded(Exception):
    pass


def start(started_at=None, budget=REQUEST_BUDGET_SECONDS):
    _local.deadline = (started_at or time()) + budget


def clear():
    _local.deadline = None


def time_left():
    deadline = getattr(_local, "deadline", None)
    return None if deadline is None else deadline - time()


def bounded_timeout(timeout):
    """A requests `timeout` (seconds, (connect, read) or None) shrunk to fit the time left."""
    left = time_left()
    if left is None:
        return timeout
    if left < MIN_CALL_SECONDS:
        raise DeadlineExceeded(f"request budget spent ({left:.1f} s left)")
    if timeout is None:
        return left
    if isinstance(timeout, tuple):
        return tuple(left if t is None else min(t, left) for t in timeout)
    return min(timeout, left)


def alb_received_at(trace_header, now=None):
    """When the ALB received this request, from X-Amzn-Trace-Id (Root=1-<epoch hex>-...).

    None when the header is missing or its time is implausible (clock skew, replays)."""
    match = _ALB_TRACE_ROOT.search(trace_header or "")
    if not match:
        return None
    received = int(match.group(1), 16)
    now = time() if now is None else now
    if not now - 120 <= received <= now + 5:
        return None
    return float(received)
