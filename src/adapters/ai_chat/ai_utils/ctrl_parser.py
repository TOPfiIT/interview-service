from typing import Any
import json


def parse_control_json(raw: str) -> dict[str, Any]:
    """
    Parse JSON from the control block inside <ctrl>...</ctrl>.
    If parsing fails, return an empty dict.
    """
    raw = raw.strip()
    if not raw:
        return {}

    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            return data
        # If it's not a dict, wrap it so we don't crash the caller
        return {"value": data}
    except json.JSONDecodeError:
        # In production you might want to log this
        return {}

