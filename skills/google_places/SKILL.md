---
name: google_places
description: "Find places via Google Places API (New): top-rated & open-now restaurants, cafés, attractions, with live ratings, hours, reviews, and Google Maps links."
version: 3.0.0
author: shlomsh
tags: [travel, places, maps, local-search]
platforms: [linux, macos, windows]
---

# Google Places

Live place recommendations with real ratings, open-now status, and tappable Maps links. Reach for this whenever the user asks about a place to eat, drink, or visit — the API beats memory because results are current.

## Primary command: `search`
Pass the user's request as a natural-language query — it already understands location and intent. This is the command you'll use ~90% of the time.

```bash
python google_places.py search "<query>" [--open] [--min-rating X] [--top N]
```

| Flag | Effect |
|---|---|
| `--open` | only places open right now |
| `--min-rating X` | only places rated ≥ X (e.g. 4.5) |
| `--top N` | cap to N results (default ~10) |

**Examples — map the user's ask straight to a query:**
```bash
# "recommended coffee around times square, open now"
python google_places.py search "top rated coffee around Times Square" --open

# "popular steak house in new york"
python google_places.py search "popular steak house in New York" --min-rating 4.5

# "trendy donut shops in miami"
python google_places.py search "trendy donut shops in Miami" --top 5
```
Put quality words ("top rated", "popular", "best", "trendy") right in the query — Google ranks on them.

## `details` — deep dive on one place
Every `search`/`nearby` result prints a `place_id`. Feed it here for full weekly hours, coordinates, and top user reviews.
```bash
python google_places.py details <place_id>
```

## `nearby` — strict radius around an anchor
Ranked by **popularity** (top-rated/popular first), bounded to a hard radius — use it for "within X meters of here." Accepts a **place/area name** (auto-resolved to coordinates) *or* raw lat/lng.
```bash
python google_places.py nearby <"location name" | lat lng> <radius_m> [type1,type2] [--open] [--top N]
# by name:        python google_places.py nearby "Williamsburg Brooklyn" 800 cafe --open
# by coordinates: python google_places.py nearby 40.758 -73.985 600 restaurant,cafe --open
```
Prefer `search` for general "in Miami / around Times Square" asks; reach for `nearby` only when a tight distance bound matters (e.g. walking distance from the hotel).

## Reading the output
Each result gives: name + type, 🟢 OPEN NOW / 🔴 CLOSED, editorial summary, address, rating + review count, price level, today's hours, website, **Google Maps link**, and a `place_id`.

When replying in WhatsApp: lead with the top 2–3, mention the rating + review count and whether it's open now, and **always include the Google Maps link** so the user can tap to navigate or save.
