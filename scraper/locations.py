"""Resolve human-readable place names to Rightmove locationIdentifiers.

Rightmove's search pages take a `locationIdentifier` query parameter such as
`REGION^87490`. These IDs are internal and undocumented, so rather than
hardcoding them (which would silently rot if wrong or if Rightmove renumbers
anything) we resolve place names at run time via Rightmove's own "typeahead"
autocomplete endpoint -- the same one that powers the search box on their
site -- and cache the result locally.

If the typeahead endpoint's response shape has changed since this was
written, `resolve()` will raise a clear error rather than silently returning
wrong data; see README.md's troubleshooting section.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional

import requests

from . import config

logger = logging.getLogger(__name__)

TYPEAHEAD_URL = "https://los.rightmove.co.uk/typeahead/uknostreet/{query}"


def _load_cache() -> dict:
    if os.path.exists(config.LOCATION_CACHE_PATH):
        with open(config.LOCATION_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    os.makedirs(os.path.dirname(config.LOCATION_CACHE_PATH), exist_ok=True)
    with open(config.LOCATION_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, sort_keys=True)


def _extract_best_match(payload: dict, place_name: str) -> Optional[dict]:
    """Rightmove's typeahead response has historically nested matches under a
    few different keys depending on version. Try the known shapes, and fall
    back to a generic scan for the first dict that has both an id-like and a
    display-name-like field.
    """
    candidates = None
    if isinstance(payload, dict):
        for key in ("matches", "results", "typeAheadResultRegions"):
            if isinstance(payload.get(key), list) and payload[key]:
                candidates = payload[key]
                break

    if candidates is None:
        # Generic fallback: walk the JSON looking for a list of dicts that
        # look like location matches.
        def walk(node):
            if isinstance(node, list):
                for item in node:
                    if (
                        isinstance(item, dict)
                        and any(k in item for k in ("id", "locationIdentifier"))
                        and any(k in item for k in ("displayName", "name", "value"))
                    ):
                        yield item
                    else:
                        yield from walk(item)
            elif isinstance(node, dict):
                for v in node.values():
                    yield from walk(v)

        candidates = list(walk(payload))

    if not candidates:
        return None

    # Prefer an exact (case-insensitive) display-name match; else take the
    # first candidate, which the typeahead API ranks by relevance already.
    for item in candidates:
        name = item.get("displayName") or item.get("name") or item.get("value") or ""
        if name.strip().lower() == place_name.strip().lower():
            return item
    return candidates[0]


def resolve(place_name: str, session: Optional[requests.Session] = None) -> str:
    """Return a Rightmove locationIdentifier for a place name, using and
    updating the on-disk cache.
    """
    cache = _load_cache()
    if place_name in cache:
        return cache[place_name]

    session = session or requests.Session()
    url = TYPEAHEAD_URL.format(query=requests.utils.quote(place_name))
    resp = session.get(
        url,
        headers={"User-Agent": config.USER_AGENT},
        timeout=config.REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    payload = resp.json()

    match = _extract_best_match(payload, place_name)
    if not match:
        raise RuntimeError(
            f"Could not resolve location '{place_name}' from Rightmove typeahead "
            f"response. Raw response (truncated): {json.dumps(payload)[:500]}\n"
            "Rightmove's typeahead response shape may have changed -- see "
            "README.md troubleshooting, or add the locationIdentifier manually "
            "to data/location_cache.json."
        )

    identifier = match.get("id") or match.get("locationIdentifier")
    if not identifier:
        raise RuntimeError(
            f"Matched a location for '{place_name}' but found no id field: {match}"
        )

    cache[place_name] = identifier
    _save_cache(cache)
    time.sleep(config.RATE_LIMIT_SECONDS)
    return identifier


def resolve_all(place_names: list[str], session: Optional[requests.Session] = None) -> dict:
    session = session or requests.Session()
    resolved = {}
    for name in place_names:
        try:
            resolved[name] = resolve(name, session=session)
        except Exception:
            logger.exception("Failed to resolve location %r", name)
            raise
    return resolved
