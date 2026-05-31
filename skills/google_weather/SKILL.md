---
name: google_weather
description: "Query real-time weather and conditions for any location using the Google Weather API."
version: 1.0.0
author: shlomsh
tags: [weather, conditions, forecast, travel]
platforms: [linux, macos, windows]
---

# Google Weather API Integration

Use this skill to fetch live weather conditions for any city, landmark, or location.

## When to Use
- The user asks about the weather in a specific place (e.g., "What's the weather in Yosemite?").
- The user asks about temperature or whether to pack a coat/umbrella.

## Usage
Run the script passing the location as arguments.

```bash
python google_weather.py lookup "Las Vegas"
```

## Parsing the Output
The script automatically finds the GPS coordinates for the location and then fetches the live weather conditions, which are printed as JSON.
Read the JSON output and provide a natural language summary to the user (e.g., "It's currently 75°F and sunny in Las Vegas!").
