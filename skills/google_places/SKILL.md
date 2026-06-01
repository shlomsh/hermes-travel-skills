---
name: google_places
description: "Google Places API: discovery engine for restaurants/attractions. Live ratings, open status, maps links."
version: 3.2.1
author: shlomsh
tags: [travel, places, maps, local-search]
platforms: [linux, macos, windows]
---

# Google Places

Live discovery engine for places. 

## Work Efficiently (Orchestration)

You must adapt your usage of this skill based on your assigned Execution Flavor:

**Flavor: ONLINE (Low Latency / Minimum Steps)**
1. Plan your execution to meet the exact request in the **absolute minimum number of steps**.
2. Craft the perfect `search` query on the first try.
3. Use `--top N` (e.g. `--top 10`) to fetch a large enough buffer of results so you can filter and pick the best options locally.
4. **Do NOT run the `details` command.** The `search` command already provides the `editorialSummary` and ratings, so running `details` in an online context wastes API tokens and latency.

**Flavor: RESEARCH (Deep Dive / Thorough)**
1. You may execute multiple `search` queries to compare different areas or keywords.
2. You may use the `details` command if you need exhaustive information (like full reviews or extensive opening hours) not covered by the `search` summary.

Available flags for `search`:
   - `--open`: Use if the user asks for places open *right now*.
   - `--min-rating X`: E.g. `--min-rating 4.5`
   - `--top N`: E.g. `--top 5`

### Orchestration Example
To ensure you can present exactly 3 high-quality options, query a buffer of places (e.g. `--top 5`) so you still have 3 valid choices even if some are closed or poorly rated.

```bash
# 1-Shot Search: Fetch top 5 places and use their basic data and editorialSummary
python google_places.py search "trendy cafes in Brooklyn" --top 5
```

### Formatting the Best Search Query
Do not just search for a generic category (like "restaurant"). The Places API is a semantic engine. **Always inject qualitative modifiers and specific locations** directly into the `<query>` string to let Google do the heavy lifting on ranking.
* **Good Query:** `"top rated kid friendly Italian restaurants in Times Square"`
* **Bad Query:** `"Italian restaurant"` (too broad, leaves the ranking to chance)

## Examples / Use Cases
Map the user's ask straight to a query:
```bash
# "top rated coffee around times square, open now"
python google_places.py search "top rated coffee around Times Square" --open --top 3

# "popular steak house in new york"
python google_places.py search "popular steak house in New York" --min-rating 4.5 --top 5
```

## `nearby`
Strict radius bounded search. Prefer `search` generally, use `nearby` only when strict distance bounds matter.
```bash
python google_places.py nearby <"location name" | lat lng> <radius_m> [type1,type2] [--open] [--top N]
```

## Output Formatting for the User
**CRITICAL RULE:** Do NOT attempt to format the output into Hebrew or use complex templates. Simply return the text data exactly as it was outputted by the Google Places script.

When returning your findings to the parent agent, output the raw data for exactly 3 high-quality options. Each option must include the raw text from Google:
1. **Name**
2. **Rating & Number of Reviewers**
3. **Editorial Summary** (use the "About" text directly from the script output)
4. **Google Maps Link**
