import sys
import os
import json
import datetime
import urllib.request

PLACES_BASE = "https://places.googleapis.com/v1/places"

# Shared "card" fields for list results (search + nearby).
# currentOpeningHours.openNow = LIVE open status; id = needed to chain into `details`.
LIST_FIELDS = (
    "places.id,places.displayName,places.formattedAddress,places.rating,"
    "places.userRatingCount,places.websiteUri,places.googleMapsUri,"
    "places.priceLevel,places.primaryType,places.editorialSummary,"
    "places.currentOpeningHours.openNow,places.regularOpeningHours.weekdayDescriptions"
)

DETAILS_FIELDS = (
    "id,displayName,formattedAddress,rating,userRatingCount,websiteUri,"
    "googleMapsUri,priceLevel,primaryType,editorialSummary,location,"
    "currentOpeningHours.openNow,regularOpeningHours.weekdayDescriptions,reviews"
)


def _get_api_key():
    key = os.environ.get("GOOGLE_PLACES_API_KEY")
    if not key:
        print("Error: GOOGLE_PLACES_API_KEY environment variable not set.")
        sys.exit(1)
    return key


def _geocode(location_name):
    """Resolve a place/area name to (lat, lng) using the Places API itself
    (searchText -> first result's location). Lets `nearby` accept "Williamsburg"
    instead of raw coordinates, without needing the separate Geocoding API enabled."""
    result = _post(
        f"{PLACES_BASE}:searchText",
        {"textQuery": location_name, "maxResultCount": 1},
        "places.location,places.formattedAddress,places.displayName",
    )
    places = result.get("places", [])
    if not places:
        raise ValueError(f"could not locate '{location_name}'")
    top = places[0]
    loc = top.get("location", {})
    lat, lng = loc.get("latitude"), loc.get("longitude")
    if lat is None or lng is None:
        raise ValueError(f"no coordinates returned for '{location_name}'")
    label = top.get("formattedAddress") or top.get("displayName", {}).get("text", location_name)
    print(f"📍 {location_name} → {label} ({lat:.5f}, {lng:.5f})\n")
    return lat, lng


def _post(url, payload, field_mask):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "X-Goog-Api-Key": _get_api_key(),
            "X-Goog-FieldMask": field_mask,
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _get(url, field_mask):
    req = urllib.request.Request(
        url,
        headers={
            "X-Goog-Api-Key": _get_api_key(),
            "X-Goog-FieldMask": field_mask,
        },
        method="GET",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def _open_now(p):
    """Live open status, preferring currentOpeningHours over regular."""
    cur = p.get("currentOpeningHours", {})
    if "openNow" in cur:
        return cur["openNow"]
    reg = p.get("regularOpeningHours", {})
    return reg.get("openNow")


def _today_hours(p):
    """Today's hours line from regularOpeningHours.weekdayDescriptions."""
    descs = p.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
    if not descs:
        return ""
    idx = datetime.date.today().weekday()  # Mon=0 … Sun=6, matches Google order
    return descs[idx] if idx < len(descs) else ""


def _print_place(i, p):
    name = p.get("displayName", {}).get("text", "Unknown")
    pid = p.get("id", "")
    address = p.get("formattedAddress", "No address")
    rating = p.get("rating", "N/A")
    count = p.get("userRatingCount", 0)
    maps_uri = p.get("googleMapsUri", "")
    website = p.get("websiteUri", "")
    price = p.get("priceLevel", "")
    ptype = p.get("primaryType", "")
    summary = p.get("editorialSummary", {}).get("text", "")
    open_now = _open_now(p)
    today = _today_hours(p)
    reviews = p.get("reviews", [])

    header = f"{i}. {name}"
    if ptype:
        header += f"  [{ptype}]"
    if open_now is True:
        header += "  🟢 OPEN NOW"
    elif open_now is False:
        header += "  🔴 CLOSED"
    print(header)
    if summary:
        print(f"   {summary}")
    print(f"   Address: {address}")
    rating_str = f"{rating}★ ({count} reviews)"
    if price:
        rating_str += f" | {price}"
    print(f"   Rating: {rating_str}")
    if today:
        print(f"   Today: {today}")
    if website:
        print(f"   Website: {website}")
    print(f"   Google Maps: {maps_uri}")
    if reviews:
        print(f"   Top Reviews:")
        for r in reviews[:3]:
            author = r.get("authorAttribution", {}).get("displayName", "Anonymous")
            rr = r.get("rating", "")
            text = r.get("text", {}).get("text", "")
            stars = f"{'★' * int(rr)}{'☆' * (5 - int(rr))}" if rr else ""
            if text:
                snippet = text[:150].replace("\n", " ")
                print(f"     [{author}] {stars} \"{snippet}{'…' if len(text) > 150 else ''}\"")
    print(f"   place_id: {pid}   (use: details {pid})")
    print()


def cmd_search(query, open_now=False, min_rating=None, top=None):
    """Text search — handles natural-language queries with implicit location.
    e.g. 'top rated coffee around Times Square', 'popular steak house in NYC'."""
    payload = {"textQuery": query}
    if open_now:
        payload["openNow"] = True
    if min_rating is not None:
        payload["minRating"] = min_rating
    if top is not None:
        payload["maxResultCount"] = top

    filters = []
    if open_now:
        filters.append("open now")
    if min_rating is not None:
        filters.append(f"rating ≥ {min_rating}")
    suffix = f"  [{', '.join(filters)}]" if filters else ""

    mask = LIST_FIELDS

    try:
        result = _post(f"{PLACES_BASE}:searchText", payload, mask)
        places = result.get("places", [])
        if not places:
            print(f"No results for '{query}'{suffix}.")
            return
        print(f"Found {len(places)} results for '{query}'{suffix}:\n")
        for i, p in enumerate(places, 1):
            _print_place(i, p)
    except Exception as e:
        print(f"API request failed: {e}")


def cmd_nearby(lat, lng, radius, types=None, open_now=False, top=None):
    """Nearby search ranked by POPULARITY (top-rated/popular first).
    open-now is filtered client-side (the API has no openNow request filter)."""
    payload = {
        "rankPreference": "POPULARITY",
        "locationRestriction": {
            "circle": {
                "center": {"latitude": lat, "longitude": lng},
                "radius": radius,
            }
        },
    }
    if types:
        payload["includedTypes"] = types
    if top is not None:
        payload["maxResultCount"] = top

    mask = LIST_FIELDS

    try:
        result = _post(f"{PLACES_BASE}:searchNearby", payload, mask)
        places = result.get("places", [])
        if open_now:
            places = [p for p in places if _open_now(p) is True]
        if not places:
            extra = " open now" if open_now else ""
            print(f"No results{extra} near ({lat}, {lng}) within {radius}m.")
            return
        label = f"near ({lat}, {lng}), radius {radius}m, ranked by popularity"
        if types:
            label += f", types: {', '.join(types)}"
        if open_now:
            label += ", open now"
        print(f"Found {len(places)} results {label}:\n")
        for i, p in enumerate(places, 1):
            _print_place(i, p)
    except Exception as e:
        print(f"API request failed: {e}")


def cmd_details(place_id):
    pid = place_id.split("places/")[-1]
    try:
        p = _get(f"{PLACES_BASE}/{pid}", DETAILS_FIELDS)
        name = p.get("displayName", {}).get("text", "Unknown")
        ptype = p.get("primaryType", "")
        summary = p.get("editorialSummary", {}).get("text", "")
        address = p.get("formattedAddress", "No address")
        rating = p.get("rating", "N/A")
        count = p.get("userRatingCount", 0)
        price = p.get("priceLevel", "")
        website = p.get("websiteUri", "")
        maps_uri = p.get("googleMapsUri", "")
        loc = p.get("location", {})
        open_now = _open_now(p)
        reviews = p.get("reviews", [])

        print(f"=== {name} ===")
        if ptype:
            print(f"Type: {ptype}")
        if summary:
            print(f"About: {summary}")
        print(f"Address: {address}")
        rating_str = f"{rating}★ ({count} reviews)"
        if price:
            rating_str += f" | {price}"
        print(f"Rating: {rating_str}")
        if open_now is True:
            print("Status: 🟢 OPEN NOW")
        elif open_now is False:
            print("Status: 🔴 CLOSED")
        descs = p.get("regularOpeningHours", {}).get("weekdayDescriptions", [])
        if descs:
            print("Hours:")
            for d in descs:
                print(f"  {d}")
        if website:
            print(f"Website: {website}")
        print(f"Google Maps: {maps_uri}")
        if loc:
            print(f"Coordinates: {loc.get('latitude')}, {loc.get('longitude')}")
        if reviews:
            print(f"\nTop {min(len(reviews), 5)} reviews:")
            for r in reviews[:5]:
                author = r.get("authorAttribution", {}).get("displayName", "Anonymous")
                rr = r.get("rating", "")
                text = r.get("text", {}).get("text", "")
                rel = r.get("relativePublishTimeDescription", "")
                stars = f"{'★' * int(rr)}{'☆' * (5 - int(rr))}" if rr else ""
                print(f"  [{author}{', ' + rel if rel else ''}] {stars}")
                if text:
                    snippet = text[:200].replace("\n", " ")
                    print(f"  \"{snippet}{'…' if len(text) > 200 else ''}\"")
                print()
    except Exception as e:
        print(f"API request failed: {e}")


def _parse_flags(args):
    """Extract --open, --open, --min-rating X, --top N from args; return (positionals, opts)."""
    opts = {"open_now": False, "min_rating": None, "top": None, "with_reviews": False}
    pos = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--open":
            opts["open_now"] = True
        elif a == "--open":
            opts["with_reviews"] = True
        elif a == "--min-rating" and i + 1 < len(args):
            opts["min_rating"] = float(args[i + 1]); i += 1
        elif a == "--top" and i + 1 < len(args):
            opts["top"] = int(args[i + 1]); i += 1
        else:
            pos.append(a)
        i += 1
    return pos, opts


def _usage():
    print(
        "Usage:\n"
        '  python google_places.py search "<natural language query>" [--open] [--open] [--min-rating X] [--top N]\n'
        "  python google_places.py nearby <lat lng | \"location name\"> <radius_m> [type1,type2] [--open] [--open] [--top N]\n"
        "  python google_places.py details <place_id>\n"
        "\nExamples:\n"
        '  python google_places.py search "top rated coffee around Times Square" --open\n'
        '  python google_places.py search "popular steak house in New York" --min-rating 4.5 --open\n'
        '  python google_places.py search "trendy donut shops in Miami"\n'
        '  python google_places.py nearby "Williamsburg Brooklyn" 800 cafe --open --open\n'
        "  python google_places.py nearby 40.758 -73.985 600 restaurant,cafe --open\n"
        "  python google_places.py details ChIJN1t_tDeuEmsRUsoyG83frY4"
    )


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        _usage()
        return

    cmd, rest = args[0], args[1:]
    pos, opts = _parse_flags(rest)

    if cmd == "search":
        if not pos:
            print("Error: search requires a query.")
            _usage()
            return
        cmd_search(" ".join(pos), opts["open_now"], opts["min_rating"], opts["top"])

    elif cmd == "nearby":
        # Two forms:
        #   nearby <lat> <lng> <radius_m> [types]      (raw coordinates)
        #   nearby "<location name>" <radius_m> [types] (auto-geocoded)
        try:
            lat, lng = float(pos[0]), float(pos[1])
            radius = float(pos[2])
            types = pos[3].split(",") if len(pos) >= 4 else None
        except (ValueError, IndexError):
            if len(pos) < 2:
                print("Error: nearby requires a location and radius.")
                _usage()
                return
            try:
                lat, lng = _geocode(pos[0])
                radius = float(pos[1])
            except Exception as e:
                print(f"Error: {e}")
                return
            types = pos[2].split(",") if len(pos) >= 3 else None
        cmd_nearby(lat, lng, radius, types, opts["open_now"], opts["top"], opts["with_reviews"])

    elif cmd == "details":
        if not pos or pos[0] in ("-h", "--help", "help"):
            print("Error: details requires a place_id.")
            _usage()
            return
        cmd_details(pos[0])

    else:
        print(f"Unknown command: {cmd}")
        _usage()


if __name__ == "__main__":
    main()
