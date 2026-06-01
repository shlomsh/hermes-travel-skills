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

To provide the best latency and efficiency, use the API's native ranking instead of manual list building. Follow this pattern:
1. Always run `python /data/.hermes/skills/travel/google_places/google_places.py --help` if you are unsure of the command syntax.
2. The `search` command already outputs the `editorialSummary` and rating data for each place. Do NOT run the `details` command unless absolutely necessary.
3. Use the `--open` flag if the user asks for places open *right now*.
4. Use `--top <N>` to fetch multiple options in one command.

### Orchestration Example (Always Provide 3 Options)
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
