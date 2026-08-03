"""Client for Rightmove's public search-results pages.

There is no official Rightmove API for this. Search results pages embed a
JSON blob describing the properties on that page; the exact wrapper around
that JSON has changed over the years (window.jsonModel -> __NEXT_DATA__ ->
whatever it is when you're reading this). To be resilient to that, we try a
couple of known wrappers and then fall back to a generic scan for "a list of
dicts that look like property listings" anywhere in the parsed JSON.

This has NOT been verified against a live response (this was written in an
environment with no outbound internet access -- see README.md). Treat the
extraction logic as a best-effort first draft to be confirmed/fixed against
a real response on first run.
"""
from __future__ import annotations

import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Iterator, Optional

import requests

from . import config

logger = logging.getLogger(__name__)

CHANNEL_PATHS = {
    "buy": "property-for-sale/find.html",
    "rent": "property-to-rent/find.html",
}

# Best-effort mapping of our exclusion flags to Rightmove's "Don't show"
# search filter values. Confirm these still match Rightmove's current search
# form (view page source / network tab on rightmove.co.uk) if filtering
# stops working -- these are unofficial and may drift.
DONT_SHOW_VALUES = {
    "retirement": "retirement",
    "shared_ownership": "sharedOwnership",
}

_LISTING_KEY_HINTS = ("bedrooms", "displayAddress", "propertySubType")
_ID_KEYS = ("id", "propertyId", "identifier")
_PRICE_KEYS = ("price", "prices")
_COUNT_KEYS = ("resultCount", "totalResults", "total", "matchCount")


@dataclass
class SearchParams:
    location_identifier: str
    channel: str = "buy"
    min_price: Optional[int] = None
    max_price: Optional[int] = None


@dataclass
class RawListing:
    raw: dict
    area: str
    channel: str


class RightmoveClient:
    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self._last_request_ts = 0.0

    def _throttled_get(self, url: str) -> requests.Response:
        elapsed = time.monotonic() - self._last_request_ts
        wait = config.RATE_LIMIT_SECONDS - elapsed
        if wait > 0:
            time.sleep(wait)
        resp = self.session.get(
            url,
            headers={
                "User-Agent": config.USER_AGENT,
                "Accept-Language": "en-GB,en;q=0.9",
            },
            timeout=config.REQUEST_TIMEOUT,
        )
        self._last_request_ts = time.monotonic()
        resp.raise_for_status()
        return resp

    def _build_url(self, params: SearchParams, index: int) -> str:
        path = CHANNEL_PATHS[params.channel]
        query = {"locationIdentifier": params.location_identifier, "index": index}
        if params.min_price is not None:
            query["minPrice"] = params.min_price
        if params.max_price is not None:
            query["maxPrice"] = params.max_price

        dont_show = []
        if config.EXCLUDE_RETIREMENT:
            dont_show.append(DONT_SHOW_VALUES["retirement"])
        if config.EXCLUDE_SHARED_OWNERSHIP:
            dont_show.append(DONT_SHOW_VALUES["shared_ownership"])
        if dont_show:
            query["dontShow"] = ",".join(dont_show)

        qs = "&".join(f"{k}={requests.utils.quote(str(v))}" for k, v in query.items())
        return f"https://www.rightmove.co.uk/{path}?{qs}"

    def fetch_page(self, params: SearchParams, index: int) -> tuple[list[dict], int]:
        """Return (listings on this page, total result count reported)."""
        url = self._build_url(params, index)
        resp = self._throttled_get(url)
        data = extract_json_payload(resp.text)
        listings = find_listing_records(data)
        total = find_result_count(data)
        return listings, total

    def iterate_search(self, params: SearchParams) -> Iterator[RawListing]:
        """Yield every listing for a search, automatically bisecting by price
        band if the result count exceeds Rightmove's apparent pagination cap.
        """
        listings, total = self.fetch_page(params, index=0)
        logger.info(
            "%s | %s [%s-%s]: reported %s results",
            params.channel,
            params.location_identifier,
            params.min_price,
            params.max_price,
            total,
        )

        if total > config.RESULT_CAP:
            for sub_params in _bisect_price(params, total):
                yield from self.iterate_search(sub_params)
            return

        seen_ids = set()
        for listing in listings:
            seen_ids.add(_listing_id(listing))
            yield RawListing(raw=listing, area=params.location_identifier, channel=params.channel)

        index = config.PAGE_SIZE
        while index < min(total, config.RESULT_CAP):
            listings, _ = self.fetch_page(params, index=index)
            if not listings:
                break
            for listing in listings:
                lid = _listing_id(listing)
                if lid in seen_ids:
                    continue
                seen_ids.add(lid)
                yield RawListing(raw=listing, area=params.location_identifier, channel=params.channel)
            index += config.PAGE_SIZE


def _bisect_price(params: SearchParams, total: int) -> list[SearchParams]:
    lo = params.min_price or 0
    # Rightmove search has no listings above ~ tens of millions; use a high
    # ceiling for the initial unbounded band rather than assuming one.
    hi = params.max_price or 20_000_000
    mid = (lo + hi) // 2
    if mid <= lo or mid >= hi:
        logger.warning(
            "Cannot bisect price band any further for %s (min=%s max=%s, total=%s) "
            "-- results in this band will be truncated at the pagination cap.",
            params.location_identifier,
            lo,
            hi,
            total,
        )
        return [params]
    return [
        SearchParams(params.location_identifier, params.channel, lo or None, mid),
        SearchParams(params.location_identifier, params.channel, mid + 1, params.max_price),
    ]


def _listing_id(listing: dict) -> str:
    for key in _ID_KEYS:
        if key in listing:
            return str(listing[key])
    return json.dumps(listing, sort_keys=True)[:200]


def extract_json_payload(html: str) -> dict:
    """Try known wrappers for the embedded search-results JSON, in order."""
    for extractor in (_extract_json_model, _extract_next_data):
        try:
            payload = extractor(html)
        except Exception:
            payload = None
        if payload:
            return payload
    raise RuntimeError(
        "Could not find embedded search-results JSON in the Rightmove response. "
        "The page structure has likely changed since this scraper was written -- "
        "save the HTML and inspect it for the new embed format. "
        f"Response length: {len(html)} chars."
    )


def _extract_json_model(html: str) -> Optional[dict]:
    marker = "window.jsonModel"
    idx = html.find(marker)
    if idx == -1:
        return None
    eq_idx = html.find("=", idx)
    brace_idx = html.find("{", eq_idx)
    if brace_idx == -1:
        return None
    obj_str = _extract_balanced_braces(html, brace_idx)
    return json.loads(obj_str)


def _extract_next_data(html: str) -> Optional[dict]:
    match = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL
    )
    if not match:
        return None
    return json.loads(match.group(1))


def _extract_balanced_braces(text: str, start: int) -> str:
    """Given the index of an opening '{', return the substring up to its
    matching closing brace, respecting string literals so braces inside
    quoted strings don't confuse the count.
    """
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    raise ValueError("Unbalanced braces while extracting embedded JSON")


def find_listing_records(payload) -> list[dict]:
    """Generic walk of the parsed JSON looking for a list of dicts that look
    like property listings (heuristic: has an id-like key plus at least one
    listing-shaped key such as bedrooms/displayAddress/propertySubType).
    """

    def looks_like_listing(item) -> bool:
        if not isinstance(item, dict):
            return False
        has_id = any(k in item for k in _ID_KEYS)
        has_hint = any(k in item for k in _LISTING_KEY_HINTS)
        return has_id and has_hint

    best: list[dict] = []

    def walk(node):
        nonlocal best
        if isinstance(node, list):
            if node and all(looks_like_listing(x) for x in node):
                if len(node) > len(best):
                    best = node
                return
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)

    walk(payload)
    return best


def find_result_count(payload) -> int:
    found = []

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k in _COUNT_KEYS and isinstance(v, (int, str)):
                    try:
                        found.append(int(str(v).replace(",", "")))
                    except ValueError:
                        pass
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(payload)
    return max(found) if found else 0
