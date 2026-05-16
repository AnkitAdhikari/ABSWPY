import os
import sys
import datetime
import argparse

import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_BASE = "https://api.openweathermap.org"
_WIND_DIRS = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]


def _wind_dir(degrees):
    return _WIND_DIRS[int((degrees + 11.25) // 22.5) % 16]


def _format(data):
    city = data.get("name", "?")
    cc = data.get("sys", {}).get("country", "")
    desc = data["weather"][0]["description"].title()
    lat, lon = data["coord"]["lat"], data["coord"]["lon"]

    main = data["main"]
    temp = main["temp"] - 273.15
    feels = main["feels_like"] - 273.15

    wind = data.get("wind", {})
    wind_line = f"Wind {wind.get('speed', 0):.1f} m/s {_wind_dir(wind.get('deg', 0))}"
    if gust := wind.get("gust"):
        wind_line += f" gust {gust:.1f}"
    if rain := data.get("rain", {}).get("1h"):
        wind_line += f" • Rain {rain:.1f} mm/h"

    tz = datetime.timezone(datetime.timedelta(seconds=data.get("timezone", 0)))

    def fmt(ts):
        return datetime.datetime.fromtimestamp(ts, tz).strftime("%H:%M")

    lines = [
        f"{city}, {cc} • {desc}",
        f"{lat:.2f}, {lon:.2f}\n",
        f"{temp:.0f}°C feels {feels:.0f}°C",
        f"Humidity {main['humidity']}% • Pressure {main['pressure']} hPa",
        wind_line,
        f"Clouds {data.get('clouds', {}).get('all')}% • Visibility {data.get('visibility', 0) / 1000:.0f} km",
        f"Sunrise {fmt(data['sys']['sunrise'])} • Sunset {fmt(data['sys']['sunset'])}",
    ]
    return "\n".join(lines)


def get_weather(city, country):
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        sys.exit("Error: OPENWEATHER_API_KEY environment variable not set.")

    session = requests.Session()

    geo = session.get(
        f"{OPENWEATHER_BASE}/geo/1.0/direct",
        params={"q": f"{city},{country}", "limit": 1, "appid": api_key},
    )
    geo.raise_for_status()
    locations = geo.json()
    if not locations:
        sys.exit(f"Error: city '{city}' not found.")

    lat, lon = locations[0]["lat"], locations[0]["lon"]

    weather = session.get(
        f"{OPENWEATHER_BASE}/data/2.5/weather",
        params={"lat": lat, "lon": lon, "appid": api_key},
    )
    weather.raise_for_status()
    print(_format(weather.json()))


def main():
    parser = argparse.ArgumentParser(description="Current weather for a city.")
    parser.add_argument("city")
    parser.add_argument("country", nargs="?", default="", help="ISO country code (optional)")
    args = parser.parse_args()
    get_weather(args.city, args.country)
