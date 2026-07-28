import importlib.util
from datetime import datetime
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "update_weather.py"
SPEC = importlib.util.spec_from_file_location("update_weather", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_sanitize_weather_text_removes_unknown_segments() -> None:
    raw = "☀️ 20°C • Unknown • H:22°C • L:18°C • No rain\n"
    sanitized = MODULE.sanitize_weather_text(raw)

    assert sanitized == "☀️ 20°C • H:22°C • L:18°C • No rain\n"


def test_sanitize_weather_text_returns_empty_for_all_unknown_values() -> None:
    raw = "☀️ Unknown • None • N/A\n"
    sanitized = MODULE.sanitize_weather_text(raw)

    assert sanitized == ""


def test_format_last_updated_includes_date_and_time() -> None:
    now = datetime(2026, 7, 26, 14, 5)

    assert MODULE.format_last_updated(now) == "Last Updated: 2026-07-26 14:05"


def test_build_weather_section_includes_weather_and_timestamp() -> None:
    now = datetime(2026, 7, 26, 9, 7)
    weather = "☁️ 15°C • Overcast • H:17°C • L:13°C • No rain\n"

    section = MODULE.build_weather_section(weather, now)

    assert (
        section
        == "> 🌤️ Weather: ☁️ 15°C • Overcast • H:17°C • L:13°C • No rain\n\n> 🕒 Last Updated: 2026-07-26 09:07\n"
    )


def test_build_weather_section_keeps_timestamp_when_weather_empty() -> None:
    now = datetime(2026, 7, 26, 6, 0)

    section = MODULE.build_weather_section("", now)

    assert section == "> 🌤️ Weather: ⚠️ Weather unavailable\n\n> 🕒 Last Updated: 2026-07-26 06:00\n"
