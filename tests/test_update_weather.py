import importlib.util
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
