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


SAMPLE_PAYLOAD = {
    "current": {"temperature_2m": 2.4, "weather_code": 3},
    "daily": {"temperature_2m_max": [9.6], "temperature_2m_min": [-0.2], "precipitation_sum": [0.0]},
}


def test_format_weather_builds_line_from_payload() -> None:
    assert MODULE.format_weather(SAMPLE_PAYLOAD) == "☁️ 2°C • Overcast • H:10°C • L:0°C • No rain\n"


def test_main_leaves_readme_unchanged_when_fetch_fails(tmp_path, monkeypatch) -> None:
    readme = tmp_path / "README.md"
    original = "#### 📍 St. John's, Newfoundland\n---\n\n> 🌤️ Weather: ☁️ 2°C • Overcast\n\n---\n"
    readme.write_text(original, encoding="utf-8")
    monkeypatch.setattr(MODULE, "README_PATH", str(readme))

    def fail() -> dict:
        raise RuntimeError("timed out")

    monkeypatch.setattr(MODULE, "request_payload", fail)

    assert MODULE.main() == 1
    assert readme.read_text(encoding="utf-8") == original


def test_request_payload_retries_then_succeeds(monkeypatch) -> None:
    calls = {"count": 0}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def read(self) -> bytes:
            return b'{"ok": true}'

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        if calls["count"] < 3:
            raise TimeoutError("timed out")
        return FakeResponse()

    monkeypatch.setattr(MODULE.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(MODULE.time, "sleep", lambda seconds: None)

    assert MODULE.request_payload() == {"ok": True}
    assert calls["count"] == 3
