# Hermes Travel Skills — Real-Time Travel Tools for the Nous Hermes Agent

> Open-source **Hermes Agent skills** that give your AI agent live **place search, weather, and flight status** through official APIs — one fast, deterministic call instead of slow, flaky web scraping.

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen.svg)
![For Nous Research Hermes Agent](https://img.shields.io/badge/for-Hermes%20Agent-7b3fe4.svg)
![Skills: 3](https://img.shields.io/badge/skills-3-orange.svg)

**Hermes Travel Skills** is an open-source pack of real-time travel tools (skills) for the [Nous Research **Hermes Agent**](https://github.com/NousResearch/hermes-agent). It equips an AI agent with three deterministic, API-backed capabilities — **Google Places search, live weather, and live flight status** — that replace the slow, error-prone "search the web and parse the page" fallback. Each skill is a single Python script with **zero pip dependencies** (standard library only) and is **MIT licensed**.

> I built these while using Hermes as a family travel planner. I couldn't find them on any skill registry, so I'm open-sourcing them for the Hermes and AI-agent community.

**Keywords:** Hermes Agent skills · Nous Research · AI agent travel tools · Google Places API (New) · Google Weather API · aviationstack flight tracker · LLM tool use · open-source AI agent · real-time travel API.

---

## Contents

- [Why these exist — the reasoning](#why-these-exist--the-reasoning)
- [The skills](#the-skills)
- [Getting the API keys](#getting-the-api-keys)
- [Installing into Hermes — step by step](#installing-into-hermes--step-by-step)
- [FAQ](#faq)
- [Repo layout](#repo-layout)

---

## Why these exist — the reasoning

Out of the box, when a Hermes agent needs live travel facts ("a good coffee place open now near Times Square", "what's the weather in Vegas", "what gate is my flight?"), it falls back to **generic web search + page parsing**. In practice that path is:

- **Slow & loopy** — search → open results → parse HTML → maybe hit a CAPTCHA or consent wall → retry. Each step is another agent iteration.
- **Flaky** — page layouts change, anti-bot walls block the fetch, and the agent sometimes re-reads the same page several times because the answer didn't survive its context window.
- **Expensive** — every iteration re-sends the whole conversation to the model, so one "where should we eat?" can balloon into many LLM calls and a lot of tokens.
- **Stale or made-up** — without a structured source the model leans on training-data memory for ratings, hours, and gates, which are exactly the facts that change.

Giving the agent **purpose-built tools backed by official APIs** collapses all of that into **one deterministic call** that returns clean, structured, current data:

| | Generic web search | Hermes Travel Skills |
|---|---|---|
| Agent iterations | many (search, open, parse, retry) | **one tool call** |
| CAPTCHAs / consent walls | frequent | none (official API) |
| Data freshness | stale / guessed | **live** (ratings, open-now, gates) |
| Output | unstructured HTML | clean structured text |
| Token cost | high (loops re-send history) | **low** (single round-trip) |

**The result: faster, more reliable, and noticeably cheaper answers** for the exact questions a travel agent gets all day.

---

## The skills

This repo ships **three Hermes Agent skills**. Each is a folder under [`skills/`](skills/) with a `SKILL.md` (what the agent reads to decide when to use it) and one Python script.

| Skill | What it does | API | Key env var |
|---|---|---|---|
| **`google_places`** | Top-rated & open-now restaurants, cafés, and attractions with live ratings, hours, reviews, and tappable Google Maps links. Natural-language search, strict-radius `nearby`, and a `details` deep-dive. | Google Places API (New) | `GOOGLE_PLACES_API_KEY` |
| **`google_weather`** | Live current conditions for any city or landmark (geocodes the name, then fetches weather). | Google Weather API (+ Places for geocoding) | `GOOGLE_WEATHER_API_KEY` *(falls back to `GOOGLE_PLACES_API_KEY`)* |
| **`aviationstack`** | Live flight status — gate, terminal, boarding, delay, and baggage belt — by IATA flight number or airport board. | aviationstack | `AVIATIONSTACK_API_KEY` |

The scripts run **standalone** too (no Hermes required), which makes them easy to test:

```bash
export GOOGLE_PLACES_API_KEY=...   # see "Getting the API keys" below
python skills/google_places/google_places.py search "top rated coffee around Times Square" --open
python skills/google_weather/google_weather.py lookup "Las Vegas"
python skills/aviationstack/live_flight_tracker.py flight LY8
```

### `google_places` — places, restaurants & attractions

```bash
# Natural-language search (~90% of uses) — put quality words in the query, Google ranks on them
python google_places.py search "popular steak house in New York" --min-rating 4.5 --open --top 5

# Strict radius around an anchor (name auto-geocoded, or raw lat/lng)
python google_places.py nearby "Williamsburg Brooklyn" 800 cafe --open
python google_places.py nearby 40.758 -73.985 600 restaurant,cafe

# Deep dive on one place (full weekly hours, coordinates, top reviews)
python google_places.py details <place_id>
```

### `google_weather` — live conditions

```bash
python google_weather.py lookup "Yosemite"
```

### `aviationstack` — live flight status

```bash
python live_flight_tracker.py flight LY8                       # today only on the free tier
python live_flight_tracker.py airport TLV dep
python live_flight_tracker.py airport MIA arr active
```

---

## Getting the API keys

### 1. Google Maps Platform key (`google_places` + `google_weather`)

Both Google skills share **one** Google Maps Platform key.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create (or pick) a project.
2. **Enable billing** on the project. Google requires a billing account even for the free monthly credit; these APIs have a generous free tier.
3. Open **APIs & Services → Library** and enable:
   - **Places API (New)** — used by `google_places` and for geocoding in `google_weather`.
   - **Weather API** — used by `google_weather`.
4. Go to **APIs & Services → Credentials → Create credentials → API key**. Copy the key.
5. *(Recommended)* Click the key → **Restrict key** → under *API restrictions* limit it to *Places API (New)* and *Weather API*.
6. Export it:
   ```bash
   export GOOGLE_PLACES_API_KEY="your-key"
   # google_weather reuses this automatically; set GOOGLE_WEATHER_API_KEY only if you want a separate key
   ```

> If weather calls fail with a permission error, the **Weather API** isn't enabled on that key's project (step 3).

### 2. aviationstack key (`aviationstack`)

1. Sign up at [aviationstack.com](https://aviationstack.com/) and pick the **Free** plan.
2. Copy your **API access key** from the dashboard.
3. Export it:
   ```bash
   export AVIATIONSTACK_API_KEY="your-key"
   ```

**Free-tier limits worth knowing:** same-day flights only (a past/future date needs a paid plan), **HTTP-only** (the key travels unencrypted in the URL — don't reuse a sensitive key), and **100 requests/month**. Query a flight on its travel day, one call per question, never poll.

---

## Installing into Hermes — step by step

These are [Hermes Agent](https://github.com/NousResearch/hermes-agent) skills. A skill is just a folder (`SKILL.md` + script) placed under your agent's skills directory; Hermes lazily loads `SKILL.md` when the agent decides it's relevant.

### A. If you already run Hermes

1. **Find your `HERMES_HOME`** (the agent's data dir — often `~/.hermes`, or `/data/.hermes` on a server / Railway deploy). Skills live in `$HERMES_HOME/skills/<category>/<skill>/`.

2. **Copy the skills in.** This repo's `skills/` maps onto a `travel/` category:
   ```bash
   git clone https://github.com/shlomsh/hermes-travel-skills.git
   mkdir -p "$HERMES_HOME/skills/travel"
   cp -r hermes-travel-skills/skills/* "$HERMES_HOME/skills/travel/"
   ```
   You should now have e.g. `$HERMES_HOME/skills/travel/google_places/SKILL.md`.

3. **Set the API keys** where the agent's runtime can read them — add them to `$HERMES_HOME/.env`:
   ```bash
   GOOGLE_PLACES_API_KEY=your-google-maps-platform-key
   AVIATIONSTACK_API_KEY=your-aviationstack-key
   # GOOGLE_WEATHER_API_KEY=...   # optional; defaults to GOOGLE_PLACES_API_KEY
   ```

4. **Restart the agent / gateway** so it picks up the new `.env` and rescans skills.

5. **Verify.** Ask the agent something that should trigger a skill — "find a top-rated coffee place open now near Times Square", "what's the weather in Vegas", "what gate is flight LY8?". Hermes will `skill_view` the matching `SKILL.md` and run the script. To confirm the scripts themselves work first, run the standalone commands from [The skills](#the-skills) above.

### B. From scratch (fresh Hermes install)

```bash
# 1. Install Hermes Agent (see its README for the current version/extras)
git clone https://github.com/NousResearch/hermes-agent.git /opt/hermes-agent
cd /opt/hermes-agent
uv pip install -e ".[all]"

# 2. Point HERMES_HOME somewhere persistent and initialize it
export HERMES_HOME="$HOME/.hermes"
mkdir -p "$HERMES_HOME"

# 3. Drop these skills in
git clone https://github.com/shlomsh/hermes-travel-skills.git
mkdir -p "$HERMES_HOME/skills/travel"
cp -r hermes-travel-skills/skills/* "$HERMES_HOME/skills/travel/"

# 4. Add your keys to $HERMES_HOME/.env (see step A.3)

# 5. Run the gateway
hermes gateway
```

> **No Python dependencies to install** — every script uses only the Python standard library, so as long as the agent can run `python`, the skills work.

### Requirements

- Python 3.8+ (standard library only — no `pip install` needed)
- A Hermes Agent install (for agent use) — or just run the scripts directly
- The API keys above

---

## FAQ

### What is the Nous Research Hermes Agent?

[Hermes Agent](https://github.com/NousResearch/hermes-agent) is an open-source AI agent framework from Nous Research. It runs a tool-calling LLM that can use **skills** — small, self-contained capabilities the agent loads on demand — to take real actions like searching, reading files, and calling APIs.

### What is a Hermes "skill"?

A skill is a folder containing a `SKILL.md` description plus a script. Hermes reads `SKILL.md` to decide *when* the skill is relevant, then runs the script to do the work. These three travel skills follow that exact pattern.

### Do these skills need any Python packages?

No. Every script uses **only the Python standard library** (`urllib`, `json`, `os`, `sys`, `datetime`). There is nothing to `pip install` — if the agent can run `python`, the skills work.

### Which APIs and keys do I need?

`google_places` and `google_weather` share one **Google Maps Platform** key (enable *Places API (New)* and *Weather API*). `aviationstack` uses a free **aviationstack** key. See [Getting the API keys](#getting-the-api-keys).

### Are they free to run?

Largely yes on light, personal use. Google Maps Platform has a generous monthly free tier; aviationstack's free plan allows same-day lookups, 100 requests/month. Heavy usage may incur Google API costs.

### Can I use these outside of Hermes?

Yes. Each script is a standalone CLI — set the relevant environment variable and run it directly (see the [standalone examples](#the-skills)). That also makes them easy to drop into other AI agent frameworks or MCP-style tool setups.

### How are these different from letting the agent just search the web?

Web search makes the agent open and parse pages, fight CAPTCHAs, and loop on retries — slow, flaky, and token-heavy. These skills hit an **official API** and return clean structured data in **one deterministic call**. See [Why these exist](#why-these-exist--the-reasoning).

### Which travel use cases do they cover?

Restaurant/café/attraction recommendations with live ratings and open-now status, current weather for any location, and live flight status (gate, terminal, delay, baggage belt). Contributions for transit, currency, and visa/entry-rule skills are welcome.

---

## Repo layout

```
hermes-travel-skills/
├── skills/
│   ├── google_places/      SKILL.md + google_places.py     (search / nearby / details)
│   ├── google_weather/     SKILL.md + google_weather.py    (lookup)
│   └── aviationstack/      SKILL.md + live_flight_tracker.py  (flight / airport)
├── .env.example            template for the three keys
├── LICENSE                 MIT
└── README.md
```

## Contributing

Issues and PRs welcome — new travel skills (transit, currency, visa/entry rules) in the same "one official API, one deterministic call" spirit are especially appreciated.

## License

[MIT](LICENSE) © 2026 Shlomi Shemesh

---

<sub>Open-source travel skills for the Nous Research Hermes Agent — real-time Google Places search, Google Weather, and aviationstack live flight tracking for AI agents and LLM tool use.</sub>
