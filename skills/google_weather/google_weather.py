import sys
import os
import urllib.parse
import json
import urllib.request

def cmd_weather(query: str):
    """Get weather using Google Places API (for coordinates) and Google Weather API"""
    api_key = os.environ.get("GOOGLE_WEATHER_API_KEY") or os.environ.get("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("Error: API Key environment variable not set.")
        return

    # Step 1: Geocode the query using Places API (New)
    places_url = "https://places.googleapis.com/v1/places:searchText"
    places_headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.location"
    }
    places_data = {"textQuery": query}
    
    req_places = urllib.request.Request(places_url, data=json.dumps(places_data).encode("utf-8"), headers=places_headers, method="POST")
    
    try:
        with urllib.request.urlopen(req_places) as response:
            result = json.loads(response.read().decode())
            places = result.get("places", [])
            
            if not places:
                print(f"Could not find coordinates for '{query}'.")
                return
                
            place = places[0]
            lat = place.get("location", {}).get("latitude")
            lng = place.get("location", {}).get("longitude")
            display_name = place.get("displayName", {}).get("text", query)
            
    except Exception as e:
        print(f"Failed to find location coordinates: {e}")
        return

    # Step 2: Fetch Current Conditions
    weather_url = f"https://weather.googleapis.com/v1/currentConditions:lookup?key={api_key}&location.latitude={lat}&location.longitude={lng}"
    
    try:
        with urllib.request.urlopen(weather_url) as response:
            weather_data = json.loads(response.read().decode())
            
            print(f"Current Weather for {display_name}:")
            # The API returns a currentConditions object, let's dump it or parse fields if available
            # We'll print the raw json nicely so the LLM can extract what it needs
            print(json.dumps(weather_data, indent=2))
            
    except Exception as e:
        print(f"Weather API request failed: {e}")
        print("Make sure you have enabled the 'Weather API' in Google Cloud Console!")

def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help", "help"):
        print("Usage: python google_weather.py lookup \"City Name\"")
        return

    cmd = args[0]
    if cmd == "lookup" and len(args) >= 2:
        cmd_weather(" ".join(args[1:]))
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python google_weather.py lookup \"City Name\"")

if __name__ == "__main__":
    main()
