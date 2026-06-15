import re
from typing import Any


def sanitize_string(value: Any) -> str:
    """Sanitize a string for safe logging and minimal injection prevention."""
    text = str(value or "").strip()
    return re.sub(r"[^a-zA-Z0-9_@.\- ]", "", text)


def get_placeholder_data(defaults: dict[str, Any]) -> dict[str, Any]:
    """Return default placeholder values when no request payload is provided."""
    return {key: f"<FRONTEND_{key.upper()}>" for key in defaults}
