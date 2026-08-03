"""Configuration for the Rightmove daily sync.

IMPORTANT: This talks to Rightmove's public search pages, not an official API.
Rightmove has no public API for this kind of bulk access, and their Terms of
Use prohibit automated scraping. This is intended for personal/internal use
at a modest, polite request rate (see RATE_LIMIT_SECONDS below) -- not for
redistribution or commercial resale of the data. Review Rightmove's current
Terms of Use before relying on this, and be prepared for it to break or get
blocked, since it depends on an undocumented, unofficial page structure that
Rightmove can change at any time.
"""

# Top-level areas to cover. Each is resolved to a Rightmove locationIdentifier
# at run time via the typeahead lookup (see locations.py) and cached in
# data/location_cache.json. Add/remove place names here -- no need to know
# Rightmove's internal location IDs.
#
# "Home Counties" here uses the traditional nine counties. Trim this list if
# you only care about a subset.
AREAS = [
    "Greater London",
    "Berkshire",
    "Buckinghamshire",
    "East Sussex",
    "Essex",
    "Hertfordshire",
    "Kent",
    "Oxfordshire",
    "Surrey",
    "West Sussex",
]

# "buy" = property-for-sale, "rent" = property-to-rent.
CHANNELS = ["buy"]

# Rightmove's own "Don't show" search filters -- ask Rightmove's search to
# exclude these categories server-side. We also re-check with keyword
# matching below in filters.py as a backstop, in case the query-param names
# drift or don't cover every case.
EXCLUDE_RETIREMENT = True
EXCLUDE_SHARED_OWNERSHIP = True

# Backstop keyword filter applied to property sub-type / summary text.
EXCLUDE_KEYWORDS = [
    "retirement",
    "shared ownership",
    "shared-ownership",
]

# Rightmove appears to cap search pagination at roughly this many results per
# individual search query. If a search's reported result count exceeds this,
# we automatically split it into two price-banded sub-searches (recursively)
# so large areas (e.g. all of Greater London) still get full coverage.
RESULT_CAP = 950
PAGE_SIZE = 24

# Politeness: minimum delay between HTTP requests to rightmove.co.uk.
RATE_LIMIT_SECONDS = 1.5

# How many days a listing can go "unseen" in a fresh crawl before we mark it
# removed/sold-let-agreed rather than assuming it was a transient miss.
REMOVED_AFTER_MISSING_RUNS = 2

DB_PATH = "data/listings.db"
LOCATION_CACHE_PATH = "data/location_cache.json"
DASHBOARD_PATH = "site/index.html"
# Dashboard only embeds listings first seen within this many days, to keep
# the generated HTML file a sane size for a region this large. Full history
# always remains queryable in data/listings.db.
DASHBOARD_WINDOW_DAYS = 14
REQUEST_TIMEOUT = 20

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
