# Rightmove daily sync

A daily job that searches Rightmove's for-sale listings across Greater
London and the Home Counties, filters out retirement and shared-ownership
properties, and tracks what's new, what's changed price, and what's come
off the market — published as a small dashboard at `site/index.html`.

## Read this first: legal/ToS status

Rightmove has no public API for bulk access to their listings. This project
works by parsing the same search-results pages you'd see in a browser at
rightmove.co.uk. **Rightmove's Terms of Use prohibit automated scraping**,
and they have taken legal action against scrapers before. This is built for
low-volume, personal/internal use (one crawl per day, with deliberate
throttling — see `RATE_LIMIT_SECONDS` in `scraper/config.py`), not for
redistribution or commercial resale of the data. Review Rightmove's current
Terms of Use yourself and use your own judgement about whether to run this;
it may get rate-limited or blocked at any time, with no warning, and that's
expected risk, not a bug.

## Important: this has not been run against live Rightmove yet

This was built in a sandboxed environment with **no outbound internet
access at all** (confirmed against unrelated sites too, not just
Rightmove), so none of the actual HTTP-calling code has been exercised
against a real response. What *has* been verified (see `tests/`):

- The JSON-extraction and result-count logic, against a hand-written
  fixture that mimics Rightmove's historically-known `window.jsonModel`
  embed.
- The retirement/shared-ownership filtering logic.
- The SQLite dedupe / price-history / removed-listing detection logic.
- The dashboard HTML generation.

What has **not** been verified: that Rightmove's search pages still embed
data the way the fixture assumes, and that the typeahead endpoint
(`scraper/locations.py`) and "don't show" filter parameter names
(`scraper/rightmove.py`, `DONT_SHOW_VALUES`) still work as written. These
are unofficial, undocumented parts of Rightmove's site and can change
without notice. Treat the first real run (e.g. via `workflow_dispatch` in
GitHub Actions, which has real internet access) as a test run, and expect to
need to tweak `scraper/rightmove.py` / `scraper/locations.py` if Rightmove's
page structure has moved on. The code is written to fail with a clear error
message pointing at the problem rather than silently returning wrong data.

## How it works

1. `scraper/locations.py` resolves the place names in `scraper/config.py`
   (`AREAS`) to Rightmove's internal `locationIdentifier` values via
   Rightmove's own search-box autocomplete endpoint, caching results in
   `data/location_cache.json` so this only happens once per area.
2. `scraper/rightmove.py` fetches search-results pages for each area, for
   sale only by default (`CHANNELS = ["buy"]`), and paginates through them.
   Rightmove appears to cap how many results you can page through per
   search (~1,000); if an area reports more than that, the search is
   automatically split into two price bands and each is crawled separately,
   recursively, so large areas like all of Greater London still get full
   coverage.
3. `scraper/filters.py` normalizes each raw listing and excludes retirement
   / shared-ownership properties (both via Rightmove's own "don't show"
   filter and a keyword backstop, in case that parameter doesn't catch
   everything).
4. `scraper/store.py` keeps everything in a SQLite database
   (`data/listings.db`, committed to the repo so state persists between
   runs) — tracking first-seen date, price history, and marking a listing
   "removed" once it's been missing from two consecutive runs (rather than
   assuming a single missed crawl means it's gone).
5. `scraper/dashboard.py` renders `site/index.html`: summary counts plus a
   searchable/sortable table of listings first seen in the last 14 days
   (`DASHBOARD_WINDOW_DAYS` in config). Full history always stays queryable
   in the SQLite file itself.

## Running it

The daily run happens via `.github/workflows/rightmove-daily-sync.yml` on
GitHub Actions (06:00 UTC daily), because GitHub's hosted runners have real
internet access — this repo's own Claude Code sandbox does not, so it
can't run this job itself.

**GitHub only fires `schedule` triggers from the default branch.** Until
this workflow file is merged into your default branch, it won't run on its
own — use the "Run workflow" button (`workflow_dispatch`) on this branch to
test it manually in the meantime.

To run locally:

```
pip install -r requirements.txt
python -m scraper.main
```

To run the tests (no network required):

```
python -m unittest discover -s tests
```

## Configuration

Edit `scraper/config.py`:

- `AREAS` — place names to cover. Defaults to Greater London plus the nine
  traditional Home Counties (Berkshire, Buckinghamshire, East Sussex, Essex,
  Hertfordshire, Kent, Oxfordshire, Surrey, West Sussex). Trim this if you
  only care about part of that.
- `CHANNELS` — `["buy"]` by default; add `"rent"` for lettings too.
- `EXCLUDE_RETIREMENT`, `EXCLUDE_SHARED_OWNERSHIP`, `EXCLUDE_KEYWORDS` —
  filtering.
- `RATE_LIMIT_SECONDS` — minimum delay between requests to rightmove.co.uk.
  Don't set this low; the whole point is to be a light, once-a-day crawl.
- `DASHBOARD_WINDOW_DAYS` — how many days of "new" listings the dashboard
  table shows.

If a place name in `AREAS` doesn't resolve, or resolves to the wrong area,
you can hand-edit `data/location_cache.json` — it's just
`{"place name": "REGION^12345"}`. To find a `locationIdentifier` by hand,
search for the area on rightmove.co.uk and copy the `locationIdentifier`
value out of the resulting URL.

## Troubleshooting

- **"Could not find embedded search-results JSON"** — Rightmove has changed
  how search pages embed data. Save a real response's HTML and look for
  where the listing data now lives, then add/update an extractor function
  in `scraper/rightmove.py` (see `_extract_json_model` / `_extract_next_data`
  for the pattern).
- **"Could not resolve location"** — the typeahead endpoint's response shape
  has changed, or the place name is ambiguous. Check the raw response in the
  error message, or set the identifier manually in
  `data/location_cache.json`.
- **Result counts look truncated** — check the logs for "Cannot bisect price
  band any further" warnings; an area may be dense enough at a single price
  point to still exceed the pagination cap. Narrow `AREAS` further (e.g. by
  borough instead of all of Greater London) if this happens.
