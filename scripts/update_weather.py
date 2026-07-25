#!/usr/bin/env python3
import json
import os
import re
import urllib.request
from typing import Any

README_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "README.md")
PLACEHOLDER = "{insert_weather_here}"

LOCATION_NAME = "St. John's, Newfoundland"
LATITUDE = 47.5605
LONGITUDE = -52.7126
TIMEZONE = "America/St_Johns"

WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mainly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Fog", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌧️"),
    55: ("Dense drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "⛈️"),
    71: ("Slight snow fall", "🌨️"),
    73: ("Moderate snow fall", "❄️"),
    75: ("Heavy snow fall", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with heavy hail", "⛈️"),
}


def fetch_weather() -> str:
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,weather_code&"
        f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone={TIMEZONE}&forecast_days=1"
    )

    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            payload: dict[str, Any] = json.load(response)
    except Exception:
        return "⚠️ Weather unavailable"

    current = payload.get("current", {})
    daily = payload.get("daily", {})
    code = current.get("weather_code", 0)
    temperature = round(float(current.get("temperature_2m", 0)))
    high = round(float(daily.get("temperature_2m_max", [0])[0]))
    low = round(float(daily.get("temperature_2m_min", [0])[0]))
    precipitation = round(float(daily.get("precipitation_sum", [0])[0]), 1)

    description, emoji = WEATHER_CODES.get(code, ("Unknown", "🌡️"))
    precipitation_text = "No rain" if precipitation <= 0 else f"{precipitation}mm rain"

    return f"{emoji} {temperature}°C • {description} • H:{high}°C • L:{low}°C • {precipitation_text}"


def update_readme(weather_text: str) -> None:
    with open(README_PATH, "r", encoding="utf-8") as handle:
        content = handle.read()

    section_pattern = re.compile(
        r"(?ms)(#### 📍 St\. John's, Newfoundland\s*\n---\s*\n)(.*?)(\n---)"
    )

    if section_pattern.search(content):
        updated = section_pattern.sub(rf"\1{weather_text}\3", content, count=1)
    elif PLACEHOLDER in content:
        updated = content.replace(PLACEHOLDER, weather_text)
    else:
        updated = content

    with open(README_PATH, "w", encoding="utf-8") as handle:
        handle.write(updated)


if __name__ == "__main__":
    weather_text = fetch_weather()
    update_readme(weather_text)
    print(f"Updated README with: {weather_text}")
