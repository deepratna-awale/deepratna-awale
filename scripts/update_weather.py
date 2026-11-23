#!/usr/bin/env python3
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

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


WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast?"
    f"latitude={LATITUDE}&longitude={LONGITUDE}&current=temperature_2m,weather_code&"
    f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone={TIMEZONE}&forecast_days=1"
)
# The Open-Meteo request occasionally hangs from GitHub-hosted runners, so use a
# short per-attempt timeout and retry instead of one long attempt.
ATTEMPTS = 5
ATTEMPT_TIMEOUT_SECONDS = 15
RETRY_DELAYS_SECONDS = (5, 15, 30, 60)


def request_payload() -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, ATTEMPTS + 1):
        try:
            request = urllib.request.Request(WEATHER_URL, headers={"User-Agent": "readme-weather-updater"})
            with urllib.request.urlopen(request, timeout=ATTEMPT_TIMEOUT_SECONDS) as response:
                return json.load(response)
        except Exception as error:  # noqa: BLE001 - log and retry any network/parse error
            last_error = error
            print(f"Attempt {attempt}/{ATTEMPTS} failed: {error!r}", file=sys.stderr)
            if attempt < ATTEMPTS:
                time.sleep(RETRY_DELAYS_SECONDS[min(attempt - 1, len(RETRY_DELAYS_SECONDS) - 1)])
    raise RuntimeError(f"Open-Meteo request failed after {ATTEMPTS} attempts") from last_error


def format_weather(payload: dict[str, Any]) -> str:
    current = payload["current"]
    daily = payload["daily"]
    code = int(current["weather_code"])
    temperature = round(float(current["temperature_2m"]))
    high = round(float(daily["temperature_2m_max"][0]))
    low = round(float(daily["temperature_2m_min"][0]))
    precipitation = round(float(daily["precipitation_sum"][0] or 0), 1)

    description, emoji = WEATHER_CODES.get(code, ("Unknown", "🌡️"))
    precipitation_text = "No rain" if precipitation <= 0 else f"{precipitation}mm rain"

    return f"{emoji} {temperature}°C • {description} • H:{high}°C • L:{low}°C • {precipitation_text}\n"


def sanitize_weather_text(weather_text: str) -> str:
    if not weather_text:
        return ""

    cleaned_text = weather_text.strip()
    if not cleaned_text:
        return ""

    if "•" not in cleaned_text:
        return weather_text.rstrip()

    parts = [part.strip() for part in cleaned_text.split("•")]
    filtered_parts: list[str] = []

    for part in parts:
        if not part:
            continue
        if re.search(r"\b(unknown|nan|none|null|n/a|na|unavailable)\b", part, flags=re.IGNORECASE):
            continue
        filtered_parts.append(part)

    if not filtered_parts:
        return ""

    sanitized = " • ".join(filtered_parts)
    if weather_text.endswith("\n"):
        sanitized += "\n"
    return sanitized


def format_last_updated(now: datetime | None = None) -> str:
    current_time = now or datetime.now(ZoneInfo(TIMEZONE))
    return current_time.strftime("Last Updated: %Y-%m-%d %H:%M")


def build_weather_section(weather_text: str, now: datetime | None = None) -> str:
    weather_line = weather_text.strip()
    timestamp_line = format_last_updated(now)

    if weather_line:
        return f"> 🌤️ Weather: {weather_line}\n\n> 🕒 {timestamp_line}\n"

    return f"> 🌤️ Weather: ⚠️ Weather unavailable\n\n> 🕒 {timestamp_line}\n"


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


def main() -> int:
    try:
        weather_text = sanitize_weather_text(format_weather(request_payload()))
    except Exception as error:  # noqa: BLE001
        # Keep the last good weather in the README instead of overwriting it
        # with "Weather unavailable", and fail the run so the problem is visible.
        print(f"::error::Weather fetch failed, README left unchanged: {error!r}")
        return 1

    if not weather_text:
        print("::error::Weather response had no usable fields, README left unchanged")
        return 1

    weather_section = build_weather_section(weather_text)
    update_readme(weather_section)
    print(f"Updated README with: {weather_section.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
