"""Normalize raw Rightmove listing JSON and apply the retirement / shared
ownership backstop filter (server-side filtering already happens via the
dontShow query param in rightmove.py -- this is belt-and-braces in case that
doesn't catch everything).
"""
from __future__ import annotations

from typing import Optional

from . import config


def _get(d: dict, *keys, default=None):
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return default


def normalize(raw: dict, area: str, channel: str) -> dict:
    listing_id = str(_get(raw, "id", "propertyId", "identifier", default=""))

    price_field = raw.get("price")
    price_amount: Optional[int] = None
    price_display: Optional[str] = None
    if isinstance(price_field, dict):
        price_amount = price_field.get("amount")
        display = price_field.get("displayPrices") or price_field.get("displayPrice")
        if isinstance(display, list) and display:
            first = display[0]
            price_display = first.get("displayPrice") if isinstance(first, dict) else str(first)
        elif isinstance(display, str):
            price_display = display
    elif isinstance(price_field, (int, float)):
        price_amount = int(price_field)
    elif isinstance(price_field, str):
        price_display = price_field

    if price_display is None and price_amount:
        price_display = f"£{price_amount:,}"

    url_path = raw.get("propertyUrl")
    if not url_path and listing_id:
        url_path = f"/properties/{listing_id}"
    url = f"https://www.rightmove.co.uk{url_path}" if url_path and url_path.startswith("/") else url_path

    customer = raw.get("customer")
    agent_name = None
    if isinstance(customer, dict):
        agent_name = customer.get("brandTradingName") or customer.get("branchDisplayName")

    location = raw.get("location")
    latitude = longitude = None
    if isinstance(location, dict):
        latitude = location.get("latitude")
        longitude = location.get("longitude")

    tags = raw.get("tags") or raw.get("keywords") or []
    if not isinstance(tags, list):
        tags = [str(tags)]

    return {
        "id": listing_id,
        "area": area,
        "channel": channel,
        "price": price_amount,
        "price_display": price_display,
        "bedrooms": raw.get("bedrooms"),
        "bathrooms": raw.get("bathrooms"),
        "property_sub_type": raw.get("propertySubType"),
        "display_address": raw.get("displayAddress"),
        "summary": raw.get("summary") or raw.get("description") or "",
        "url": url,
        "agent": agent_name,
        "latitude": latitude,
        "longitude": longitude,
        "raw_tags": tags,
    }


def is_excluded(normalized: dict) -> bool:
    haystack = " ".join(
        [
            normalized.get("property_sub_type") or "",
            normalized.get("summary") or "",
            " ".join(str(t) for t in normalized.get("raw_tags") or []),
        ]
    ).lower()
    return any(keyword in haystack for keyword in config.EXCLUDE_KEYWORDS)
