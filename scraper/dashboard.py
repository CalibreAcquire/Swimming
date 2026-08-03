"""Generate a self-contained static HTML dashboard from the SQLite store.

No CDN dependencies -- everything (CSS/JS) is inline, and the page works by
embedding a JSON array of recent listings that a small vanilla-JS table
renders with client-side search/sort/filter.
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta

from . import config
from .store import Store

PAGE_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Rightmove Daily Sync</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{ color-scheme: light dark; }}
body {{ font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; padding: 1.5rem; }}
h1 {{ font-size: 1.4rem; margin-bottom: 0.25rem; }}
.meta {{ color: #777; font-size: 0.85rem; margin-bottom: 1.25rem; }}
.cards {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }}
.card {{ border: 1px solid #8884; border-radius: 8px; padding: 0.75rem 1rem; min-width: 130px; }}
.card .n {{ font-size: 1.6rem; font-weight: 600; display: block; }}
.card .l {{ font-size: 0.8rem; color: #777; }}
.controls {{ display: flex; gap: 0.5rem; margin-bottom: 0.75rem; flex-wrap: wrap; }}
input, select {{ padding: 0.4rem 0.6rem; border-radius: 6px; border: 1px solid #8884; background: transparent; color: inherit; }}
table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
th, td {{ text-align: left; padding: 0.4rem 0.6rem; border-bottom: 1px solid #8882; }}
th {{ cursor: pointer; white-space: nowrap; }}
tr:hover {{ background: #8881; }}
a {{ color: inherit; }}
.small {{ color: #777; font-size: 0.8rem; }}
</style>
</head>
<body>
<h1>Rightmove Daily Sync</h1>
<div class="meta">Last run: {last_run} &middot; Generated: {generated_at} &middot; Covers: London &amp; Home Counties, for-sale, retirement/shared-ownership excluded</div>

<div class="cards">
  <div class="card"><span class="n">{active_total}</span><span class="l">active listings tracked</span></div>
  <div class="card"><span class="n">{new_today}</span><span class="l">new today</span></div>
  <div class="card"><span class="n">{price_changes_today}</span><span class="l">price changes today</span></div>
  <div class="card"><span class="n">{removed_today}</span><span class="l">removed today</span></div>
</div>

<p class="small">Showing listings first seen in the last {window_days} days ({shown_count} of {active_total} active). Full history lives in data/listings.db.</p>

<div class="controls">
  <input id="q" type="search" placeholder="Search address / agent / type&hellip;" style="flex:1; min-width:200px;">
  <select id="areaFilter"><option value="">All areas</option>{area_options}</select>
</div>

<table id="tbl">
  <thead>
    <tr>
      <th data-k="first_seen">First seen</th>
      <th data-k="area">Area</th>
      <th data-k="display_address">Address</th>
      <th data-k="price">Price</th>
      <th data-k="bedrooms">Beds</th>
      <th data-k="property_sub_type">Type</th>
      <th data-k="agent">Agent</th>
    </tr>
  </thead>
  <tbody></tbody>
</table>

<script id="data" type="application/json">{data_json}</script>
<script>
const rows = JSON.parse(document.getElementById('data').textContent);
const tbody = document.querySelector('#tbl tbody');
const q = document.getElementById('q');
const areaFilter = document.getElementById('areaFilter');
let sortKey = 'first_seen', sortDir = -1;

function render() {{
  const term = q.value.trim().toLowerCase();
  const area = areaFilter.value;
  let filtered = rows.filter(r => {{
    if (area && r.area !== area) return false;
    if (!term) return true;
    return [r.display_address, r.agent, r.property_sub_type].join(' ').toLowerCase().includes(term);
  }});
  filtered.sort((a, b) => {{
    const av = a[sortKey], bv = b[sortKey];
    if (av === bv) return 0;
    return (av > bv ? 1 : -1) * sortDir;
  }});
  tbody.innerHTML = filtered.map(r => `
    <tr>
      <td>${{r.first_seen}}</td>
      <td>${{r.area}}</td>
      <td><a href="${{r.url}}" target="_blank" rel="noopener">${{r.display_address || ''}}</a></td>
      <td>${{r.price_display || ''}}</td>
      <td>${{r.bedrooms ?? ''}}</td>
      <td>${{r.property_sub_type || ''}}</td>
      <td>${{r.agent || ''}}</td>
    </tr>`).join('');
}}

document.querySelectorAll('th[data-k]').forEach(th => {{
  th.addEventListener('click', () => {{
    const k = th.dataset.k;
    sortDir = (sortKey === k) ? -sortDir : -1;
    sortKey = k;
    render();
  }});
}});
q.addEventListener('input', render);
areaFilter.addEventListener('change', render);
render();
</script>
</body>
</html>
"""


def build_dashboard(store: Store, run_summary: dict, generated_at: str) -> str:
    active = store.all_active_listings()
    cutoff = (date.today() - timedelta(days=config.DASHBOARD_WINDOW_DAYS)).isoformat()
    recent = [dict(row) for row in active if row["first_seen"] >= cutoff]

    areas = sorted({row["area"] for row in active})
    area_options = "".join(f'<option value="{a}">{a}</option>' for a in areas)

    slim = [
        {
            "first_seen": r["first_seen"],
            "area": r["area"],
            "display_address": r["display_address"],
            "price": r["price"],
            "price_display": r["price_display"],
            "bedrooms": r["bedrooms"],
            "property_sub_type": r["property_sub_type"],
            "agent": r["agent"],
            "url": r["url"],
        }
        for r in recent
    ]

    return PAGE_TEMPLATE.format(
        last_run=run_summary.get("run_date", "n/a"),
        generated_at=generated_at,
        active_total=len(active),
        new_today=run_summary.get("new_count", 0),
        price_changes_today=run_summary.get("price_change_count", 0),
        removed_today=run_summary.get("removed_count", 0),
        window_days=config.DASHBOARD_WINDOW_DAYS,
        shown_count=len(slim),
        area_options=area_options,
        data_json=json.dumps(slim),
    )


def write_dashboard(store: Store, run_summary: dict, generated_at: str, path: str = config.DASHBOARD_PATH):
    html = build_dashboard(store, run_summary, generated_at)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
