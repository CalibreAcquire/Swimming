"""Entry point: resolve areas -> crawl Rightmove search results -> filter ->
store -> render dashboard. Run daily via .github/workflows/rightmove-daily-sync.yml.

    python -m scraper.main
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone

from . import config, dashboard, filters, locations
from .rightmove import RightmoveClient, SearchParams
from .store import Store, today_str

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("scraper.main")


def run() -> int:
    started_at = datetime.now(timezone.utc).isoformat()
    run_date = today_str()

    logger.info("Resolving %d areas to Rightmove location identifiers...", len(config.AREAS))
    resolved = locations.resolve_all(config.AREAS)

    store = Store()
    client = RightmoveClient()

    seen_ids: set[str] = set()
    new_count = 0
    price_change_count = 0
    excluded_count = 0
    errors: list[str] = []

    for area_name, location_identifier in resolved.items():
        for channel in config.CHANNELS:
            params = SearchParams(location_identifier=location_identifier, channel=channel)
            logger.info("Crawling %s (%s)...", area_name, channel)
            try:
                for raw_listing in client.iterate_search(params):
                    normalized = filters.normalize(raw_listing.raw, area=area_name, channel=channel)
                    if not normalized["id"]:
                        continue
                    if filters.is_excluded(normalized):
                        excluded_count += 1
                        continue
                    seen_ids.add(normalized["id"])
                    result = store.upsert_listing(normalized, run_date)
                    if result.is_new:
                        new_count += 1
                    elif result.price_changed:
                        price_change_count += 1
            except Exception as exc:  # noqa: BLE001 - keep crawling other areas
                logger.exception("Failed crawling %s (%s)", area_name, channel)
                errors.append(f"{area_name} ({channel}): {exc}")

    removed_count = store.finalize_missing(seen_ids, run_date)

    finished_at = datetime.now(timezone.utc).isoformat()
    stats = {
        "total_seen": len(seen_ids),
        "new_count": new_count,
        "price_change_count": price_change_count,
        "removed_count": removed_count,
    }
    store.record_run(run_date, started_at, finished_at, stats)

    dashboard.write_dashboard(
        store,
        {**stats, "run_date": run_date},
        generated_at=finished_at,
    )

    summary_lines = [
        f"Rightmove sync {run_date}",
        f"  Areas crawled: {len(resolved)} x {len(config.CHANNELS)} channel(s)",
        f"  Listings seen: {len(seen_ids)}",
        f"  New: {new_count}  Price changes: {price_change_count}  Removed: {removed_count}",
        f"  Excluded (retirement/shared ownership): {excluded_count}",
    ]
    if errors:
        summary_lines.append(f"  Errors ({len(errors)}):")
        summary_lines.extend(f"    - {e}" for e in errors)

    summary = "\n".join(summary_lines)
    print(summary)

    step_summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary_path:
        with open(step_summary_path, "a", encoding="utf-8") as f:
            f.write("```\n" + summary + "\n```\n")

    store.close()
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(run())
