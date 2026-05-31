---
name: aviationstack
description: "Live flight status — gate, terminal, boarding, delay, baggage belt. Same-day only."
version: 1.1.0
author: shlomsh
tags: [travel, flights, status, tracking, real-time]
platforms: [linux, macos, windows]
---

# Aviationstack — Live Flight Tracker

Live gate, terminal, delay, and baggage-belt data for any flight, by IATA flight number or airport.

## When to use

Reach for this whenever the user asks about the live status of a flight — gate, terminal,
boarding, delay, landing, or which belt the baggage is on. Resolve the IATA flight number
from context (itinerary, a forwarded confirmation, a screenshot) when you can, so you don't
have to ask the user for it.

| User asks | You do |
|---|---|
| gate / terminal / boarding | `flight <IATA>` → `departure.terminal`, `departure.gate`, `departure.delay` |
| landed / touched down | `flight <IATA>` → status LANDED + `arrival.actual` |
| luggage / baggage belt | `flight <IATA>` → `arrival.baggage` (belt number) |
| delay / on time | `flight <IATA>` → `departure.delay` (0 = on time ✓) |

## Example questions

| You ask | You run |
|---|---|
| "Which baggage belt is the luggage from flight LY574 coming out on?" | `flight LY574` → `arrival.baggage` |
| "Is flight IZ212 departing on time, or is it delayed?" | `flight IZ212` → `departure.delay` (0 = on time ✓) |
| "Where do I pick up my bags — which carousel?" | `flight <IATA>` → `arrival.baggage` |
| "Has flight AA100 landed yet?" | `flight AA100` → status + `arrival.actual` |

## Usage

```bash
python live_flight_tracker.py flight LY8           # today (the only reliable mode on free tier)
python live_flight_tracker.py airport TLV dep
python live_flight_tracker.py airport MIA arr active
```

The `flight` command takes an optional `[YYYY-MM-DD]`, but a date other than today needs a
**paid** aviationstack plan — on the free key it returns "No data found". Track each flight
**on its travel day**, not in advance.

## Status icons
`🕐 SCHEDULED` · `✈️  ACTIVE` · `🛬 LANDED` · `❌ CANCELLED` · `↩️  DIVERTED` · `⚠️  INCIDENT`

## Notes
- Free tier: same-day real-time only, HTTP, 100 req/month — one call per question, never poll.
- Gate and baggage belt can change — always fetch live.
- Requires `AVIATIONSTACK_API_KEY` in the environment. Note: the free tier is HTTP-only, so the
  key travels unencrypted in the request URL.
