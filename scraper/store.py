"""SQLite-backed persistence: dedupe listings across daily runs, track price
history, and detect removed (sold/let-agreed/withdrawn) listings.

The DB file (data/listings.db) is committed to the repo by the GitHub Actions
workflow so state carries over between runs without needing external
infrastructure.
"""
from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from typing import Iterable, Optional

from . import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS listings (
    id TEXT PRIMARY KEY,
    area TEXT,
    channel TEXT,
    price INTEGER,
    price_display TEXT,
    bedrooms INTEGER,
    bathrooms INTEGER,
    property_sub_type TEXT,
    display_address TEXT,
    summary TEXT,
    url TEXT,
    agent TEXT,
    latitude REAL,
    longitude REAL,
    first_seen TEXT NOT NULL,
    last_seen TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    missed_runs INTEGER NOT NULL DEFAULT 0,
    removed_at TEXT
);

CREATE TABLE IF NOT EXISTS price_history (
    listing_id TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    price INTEGER,
    PRIMARY KEY (listing_id, observed_at)
);

CREATE TABLE IF NOT EXISTS runs (
    run_date TEXT PRIMARY KEY,
    started_at TEXT,
    finished_at TEXT,
    total_seen INTEGER,
    new_count INTEGER,
    price_change_count INTEGER,
    removed_count INTEGER
);
"""


@dataclass
class UpsertResult:
    listing_id: str
    is_new: bool
    price_changed: bool
    old_price: Optional[int] = None


class Store:
    def __init__(self, path: str = config.DB_PATH):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self):
        self.conn.close()

    @contextmanager
    def transaction(self):
        try:
            yield
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def upsert_listing(self, listing: dict, run_date: str) -> UpsertResult:
        cur = self.conn.execute(
            "SELECT price FROM listings WHERE id = ?", (listing["id"],)
        )
        row = cur.fetchone()

        if row is None:
            self.conn.execute(
                """
                INSERT INTO listings (
                    id, area, channel, price, price_display, bedrooms, bathrooms,
                    property_sub_type, display_address, summary, url, agent,
                    latitude, longitude, first_seen, last_seen, status, missed_runs
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'active', 0)
                """,
                (
                    listing["id"],
                    listing["area"],
                    listing["channel"],
                    listing["price"],
                    listing["price_display"],
                    listing["bedrooms"],
                    listing["bathrooms"],
                    listing["property_sub_type"],
                    listing["display_address"],
                    listing["summary"],
                    listing["url"],
                    listing["agent"],
                    listing["latitude"],
                    listing["longitude"],
                    run_date,
                    run_date,
                ),
            )
            self._record_price(listing["id"], run_date, listing["price"])
            return UpsertResult(listing["id"], is_new=True, price_changed=False)

        old_price = row[0]
        price_changed = listing["price"] is not None and listing["price"] != old_price

        self.conn.execute(
            """
            UPDATE listings SET
                area = ?, channel = ?, price = ?, price_display = ?, bedrooms = ?,
                bathrooms = ?, property_sub_type = ?, display_address = ?,
                summary = ?, url = ?, agent = ?, latitude = ?, longitude = ?,
                last_seen = ?, status = 'active', missed_runs = 0
            WHERE id = ?
            """,
            (
                listing["area"],
                listing["channel"],
                listing["price"],
                listing["price_display"],
                listing["bedrooms"],
                listing["bathrooms"],
                listing["property_sub_type"],
                listing["display_address"],
                listing["summary"],
                listing["url"],
                listing["agent"],
                listing["latitude"],
                listing["longitude"],
                run_date,
                listing["id"],
            ),
        )
        if price_changed:
            self._record_price(listing["id"], run_date, listing["price"])

        return UpsertResult(listing["id"], is_new=False, price_changed=price_changed, old_price=old_price)

    def _record_price(self, listing_id: str, observed_at: str, price: Optional[int]):
        self.conn.execute(
            "INSERT OR REPLACE INTO price_history (listing_id, observed_at, price) VALUES (?, ?, ?)",
            (listing_id, observed_at, price),
        )

    def finalize_missing(self, seen_ids: Iterable[str], run_date: str) -> int:
        """Mark previously-active listings not seen in this run as missed;
        once a listing has been missed REMOVED_AFTER_MISSING_RUNS times in a
        row, flip it to status='removed'.
        """
        seen_ids = set(seen_ids)
        cur = self.conn.execute(
            "SELECT id, missed_runs FROM listings WHERE status = 'active'"
        )
        active = cur.fetchall()

        removed_count = 0
        for listing_id, missed_runs in active:
            if listing_id in seen_ids:
                continue
            missed_runs += 1
            if missed_runs >= config.REMOVED_AFTER_MISSING_RUNS:
                self.conn.execute(
                    "UPDATE listings SET status = 'removed', missed_runs = ?, removed_at = ? WHERE id = ?",
                    (missed_runs, run_date, listing_id),
                )
                removed_count += 1
            else:
                self.conn.execute(
                    "UPDATE listings SET missed_runs = ? WHERE id = ?",
                    (missed_runs, listing_id),
                )
        return removed_count

    def record_run(self, run_date: str, started_at: str, finished_at: str, stats: dict):
        self.conn.execute(
            """
            INSERT OR REPLACE INTO runs (
                run_date, started_at, finished_at, total_seen, new_count,
                price_change_count, removed_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_date,
                started_at,
                finished_at,
                stats.get("total_seen", 0),
                stats.get("new_count", 0),
                stats.get("price_change_count", 0),
                stats.get("removed_count", 0),
            ),
        )

    def all_active_listings(self) -> list[sqlite3.Row]:
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.execute(
            "SELECT * FROM listings WHERE status = 'active' ORDER BY first_seen DESC"
        )
        rows = cur.fetchall()
        self.conn.row_factory = None
        return rows

    def recent_runs(self, limit: int = 30) -> list[sqlite3.Row]:
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.execute(
            "SELECT * FROM runs ORDER BY run_date DESC LIMIT ?", (limit,)
        )
        rows = cur.fetchall()
        self.conn.row_factory = None
        return rows


def today_str() -> str:
    return date.today().isoformat()
