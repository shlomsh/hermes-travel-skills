---
name: google_places
description: "Google Places API: discovery engine for restaurants/attractions. Live ratings, reviews, open status, maps links."
version: 3.2.0
author: shlomsh
tags: [travel, places, maps, local-search]
platforms: [linux, macos, windows]
---

# Google Places

Live discovery engine for places. 

## Work Efficiently (Orchestration)

To provide the best latency and efficiency, use the API's native ranking instead of manual list building. Follow this pattern:
1. Always run `python /data/.hermes/skills/travel/google_places/google_places.py --help` if you are unsure of the command syntax.
2. To save I/O roundtrips, you can append `--reviews` and `--top <N>` to your `search` and `nearby` commands. This fetches the top N places and prints their reviews all in a single command, eliminating the need to call `details` for each place individually.
3. Use the `--open` flag if the user asks for places open *right now*.
4. If a place is missing reviews or detailed summaries, simply use its `rating`, `userRatingCount`, and `editorialSummary` to justify why it's a great pick, and move on.

### Orchestration Example (Always Provide 3 Options)
To ensure you can present exactly 3 high-quality options to the user, query a buffer of places (e.g. `--top 5`) so you still have 3 valid choices even if some are closed or poorly rated.

To save I/O roundtrips, you can use `--reviews` to get everything in one shot:
```bash
# One-Shot: Fetch 5 places AND their top reviews instantly
python google_places.py search "trendy cafes in Brooklyn" --top 5 --reviews
```

Alternatively, if you need a deeper dive into a specific place:
```bash
# Multi-Shot: Discover first, then fetch deeper details
python google_places.py search "trendy cafes in Brooklyn" --top 5
python google_places.py details ChIJ_1234567890
python google_places.py details ChIJ_0987654321
```

### Formatting the Best Search Query
Do not just search for a generic category (like "restaurant"). The Places API is a semantic engine. **Always inject qualitative modifiers and specific locations** directly into the `<query>` string to let Google do the heavy lifting on ranking.
* **Good Query:** `"top rated kid friendly Italian restaurants in Times Square"`
* **Bad Query:** `"Italian restaurant"` (too broad, leaves the ranking to chance)

## Examples / Use Cases
Map the user's ask straight to a query:
```bash
# "top rated coffee around times square, open now"
python google_places.py search "top rated coffee around Times Square" --open --top 3 --reviews

# "popular steak house in new york"
python google_places.py search "popular steak house in New York" --min-rating 4.5 --top 5 --reviews
```

## `nearby`
Strict radius bounded search. Prefer `search` generally, use `nearby` only when strict distance bounds matter.
```bash
python google_places.py nearby <"location name" | lat lng> <radius_m> [type1,type2] [--open] [--top N]
```

## Output Formatting for the User
You MUST present exactly 3 high-quality options to the user. When giving the end recommendation, each option MUST include:
1. **Rating & Number of Reviewers**.
2. **Review Insights**: Summarize what people are saying based on the `reviews` (e.g., special dishes, service quality, vibe).
3. **Google Maps Link**: Always provide the tappable link for navigation.
