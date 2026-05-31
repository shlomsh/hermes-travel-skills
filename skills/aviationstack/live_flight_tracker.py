import sys
import os
import json
import urllib.request
import urllib.parse

# Free tier uses HTTP only; HTTPS requires a paid plan
BASE_URL = "http://api.aviationstack.com/v1"

STATUS_ICON = {
    "scheduled": "🕐",
    "active":    "✈️ ",
    "landed":    "🛬",
    "cancelled": "❌",
    "incident":  "⚠️ ",
    "diverted":  "↩️ ",
}


def get(endpoint, params):
    api_key = os.environ.get("AVIATIONSTACK_API_KEY")
    if not api_key:
        print("Error: AVIATIONSTACK_API_KEY environment variable not set.")
        sys.exit(1)
    params["access_key"] = api_key
    url = f"{BASE_URL}/{endpoint}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
    except Exception as e:
        print(f"API request failed: {e}")
        sys.exit(1)
    if "error" in data:
        print(f"API error: {data['error'].get('message', data['error'])}")
        sys.exit(1)
    return data


def fmt_time(iso):
    """Trim ISO8601 timestamp to HH:MM on YYYY-MM-DD."""
    if not iso:
        return None
    # format: 2019-12-12T04:20:00+00:00
    try:
        date_part, rest = iso[:10], iso[11:16]
        return f"{date_part} {rest}"
    except Exception:
        return iso[:16]


def fmt_delay(delay):
    """Return delay string or on-time indicator. delay=None means unknown."""
    if delay is None:
        return None
    if delay == 0:
        return "On time ✓"
    return f"+{delay} min delay ⚠️"


def fmt_leg(label, obj):
    """Format departure or arrival leg."""
    lines = []
    iata     = obj.get("iata", "?")
    airport  = obj.get("airport", "")
    terminal = obj.get("terminal")
    gate     = obj.get("gate")
    baggage  = obj.get("baggage")        # arrival only
    delay    = obj.get("delay")          # integer minutes or None

    scheduled       = fmt_time(obj.get("scheduled"))
    estimated       = fmt_time(obj.get("estimated"))
    actual          = fmt_time(obj.get("actual"))
    estimated_runway = fmt_time(obj.get("estimated_runway"))
    actual_runway    = fmt_time(obj.get("actual_runway"))

    # Header
    lines.append(f"   {label}  {iata}  {airport}")

    # Times — show each field separately so the agent knows what's confirmed vs estimated
    time_parts = [f"Scheduled: {scheduled or '?'}"]
    if actual:
        time_parts.append(f"Actual: {actual}")
    elif estimated and estimated != scheduled:
        time_parts.append(f"Estimated: {estimated}")
    lines.append("        " + "  |  ".join(time_parts))

    # Runway times (wheels off / wheels on) — only show when present
    if actual_runway:
        lines.append(f"        Runway actual: {actual_runway}")
    elif estimated_runway and estimated_runway != estimated:
        lines.append(f"        Runway est:    {estimated_runway}")

    # Delay
    delay_str = fmt_delay(delay)
    if delay_str:
        lines.append(f"        {delay_str}")

    # Terminal / Gate / Baggage
    facility_parts = []
    if terminal:
        facility_parts.append(f"Terminal {terminal}")
    if gate:
        facility_parts.append(f"Gate {gate}")
    if baggage:
        facility_parts.append(f"Baggage {baggage}")
    if facility_parts:
        lines.append("        " + "  |  ".join(facility_parts))

    return lines


def fmt_flight(f):
    status     = f.get("flight_status", "unknown").lower()
    icon       = STATUS_ICON.get(status, "✈️ ")
    status_str = status.upper()

    flight_obj  = f.get("flight", {})
    flight_iata = (flight_obj.get("iata") or "?").upper()
    airline     = f.get("airline", {}).get("name", "?")
    flight_date = f.get("flight_date", "")

    codeshared = flight_obj.get("codeshared")
    codeshare_str = ""
    if codeshared:
        cs_airline = codeshared.get("airline_name", "")
        cs_iata    = codeshared.get("flight_iata", "")
        if cs_airline or cs_iata:
            codeshare_str = f"  (codeshare: {cs_airline} {cs_iata})".strip()

    lines = []
    lines.append(f"{icon} {flight_iata}  {airline}{codeshare_str}  [{status_str}]  {flight_date}")
    lines.extend(fmt_leg("DEP", f.get("departure", {})))
    lines.extend(fmt_leg("ARR", f.get("arrival", {})))

    # Live position — only show when airborne
    live = f.get("live")
    if live and not live.get("is_ground"):
        lat   = live.get("latitude")
        lng   = live.get("longitude")
        alt   = live.get("altitude")
        speed = live.get("speed_horizontal")
        updated = (live.get("updated") or "")[:16]
        if lat is not None and lng is not None:
            extras = []
            if alt is not None:
                extras.append(f"alt {alt}m")
            if speed is not None:
                extras.append(f"{speed}km/h")
            extra_str = ("  " + "  ".join(extras)) if extras else ""
            lines.append(f"   LIVE  {lat:.2f},{lng:.2f}{extra_str}  (as of {updated})")

    return "\n".join(lines)


def cmd_flight(args):
    """Look up a specific flight by IATA number.
    Usage: flight <IATA>
    Examples: flight LY8
              flight AA100
    """
    if not args:
        print("Usage: flight <IATA> [YYYY-MM-DD]  e.g. flight LY8  or  flight AA100 2026-07-13")
        return

    flight_iata = args[0].upper()

    data = get("flights", {
        "flight_iata": flight_iata,
        "limit": 5,
    })
    flights = data.get("data", [])
    if not flights:
        print(f"No data found for {flight_iata}.")
        return
    total = data.get("pagination", {}).get("total", len(flights))
    print(f"Status for {flight_iata}  ({len(flights)} of {total}):\n")
    for f in flights:
        print(fmt_flight(f))
        print()


def cmd_airport(args):
    """Live departure or arrival board for an airport.
    Usage: airport <IATA> [dep|arr] [active|scheduled|landed|cancelled]
    Examples: airport TLV dep
              airport MIA arr active
    """
    if not args:
        print("Usage: airport <IATA> [dep|arr] [status]")
        return

    iata      = args[0].upper()
    direction = "dep"
    status    = None

    for arg in args[1:]:
        if arg in ("dep", "arr"):
            direction = arg
        elif arg in ("active", "scheduled", "landed", "cancelled", "incident", "diverted"):
            status = arg

    params = {"limit": 10}
    if direction == "arr":
        params["arr_iata"] = iata
        label = f"Arrivals at {iata}"
    else:
        params["dep_iata"] = iata
        label = f"Departures from {iata}"
    if status:
        params["flight_status"] = status
        label += f" [{status}]"

    data = get("flights", params)
    flights = data.get("data", [])
    total   = data.get("pagination", {}).get("total", len(flights))
    if not flights:
        print(f"No flights found for {iata}.")
        return
    print(f"{label} — showing {len(flights)} of {total}:\n")
    for f in flights:
        print(fmt_flight(f))
        print()


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print("Usage:")
        print("  python live_flight_tracker.py flight <IATA> [YYYY-MM-DD]")
        print("  python live_flight_tracker.py airport <IATA> [dep|arr] [active|scheduled|landed|cancelled]")
        print()
        print("Examples:")
        print("  python live_flight_tracker.py flight LY8        # today only on free tier")
        print("  python live_flight_tracker.py airport TLV dep")
        print("  python live_flight_tracker.py airport MIA arr active")
        print()
        print("Note: a [YYYY-MM-DD] other than today requires a paid aviationstack plan.")
        return

    cmd = args[0]
    if cmd == "flight":
        cmd_flight(args[1:])
    elif cmd == "airport":
        cmd_airport(args[1:])
    else:
        print(f"Unknown command: {cmd}")
        print("Commands: flight, airport")


if __name__ == "__main__":
    main()
