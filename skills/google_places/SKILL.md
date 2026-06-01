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
1. **Discovery (`search`)**: Run ONE `search` command using `--top N` to fetch the best candidates based on the user's intent.
2. **Deep Dive (`details`)**: Run `details <place_id>` on the top choices to pull specific review snippets or deeper insights. You can fetch details for multiple places if needed to give a great recommendation.

### Multi-shot Orchestration Example
```bash
# Step 1: User asks for trendy cafes in Brooklyn. Run one search to discover them.
python google_places.py search "trendy cafes in Brooklyn" --top 3
# (Returns 3 places with their place_ids)

# Step 2: Fetch details for the top recommendations to get review insights.
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
python google_places.py search "top rated coffee around Times Square" --open

# "popular steak house in new york"
python google_places.py search "popular steak house in New York" --min-rating 4.5
```

## `nearby`
Strict radius bounded search. Prefer `search` generally, use `nearby` only when strict distance bounds matter.
```bash
python google_places.py nearby <"location name" | lat lng> <radius_m> [type1,type2] [--open] [--top N]
```

## Output Formatting for the User
When giving the end recommendation, you MUST include:
1. **Rating & Number of Reviewers**.
2. **Review Insights**: Summarize what people are saying based on the `reviews` (e.g., special dishes, service quality, vibe).
3. **Google Maps Link**: Always provide the tappable link for navigation.
