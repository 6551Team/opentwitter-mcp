"""Configuration for the Twitter MCP server.

Reads settings from config.json at project root. Environment variables
can override any value.
"""

import json
import os
from datetime import datetime, date
from decimal import Decimal
from pathlib import Path

# ---------- Load config.json ----------
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config.json"

_cfg: dict = {}
if _CONFIG_PATH.exists():
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        _cfg = json.load(f)

# ---------- API (env vars take precedence) ----------
API_BASE_URL = os.environ.get("TWITTER_API_BASE") or _cfg.get("api_base_url", "https://ai.6551.io")
API_TOKEN = (
    os.environ.get("OPENNEWS_TOKEN")
    or os.environ.get("TWITTER_TOKEN")
    or _cfg.get("api_token", "")
)

# Optional read-only Hermes Tweet / Xquik backend for tweet search.
X_READ_BACKEND = os.environ.get("X_READ_BACKEND", "").strip().lower()
HERMES_TWEET_API_KEY = os.environ.get("HERMES_TWEET_API_KEY") or os.environ.get("XQUIK_API_KEY", "")
HERMES_TWEET_BASE_URL = (
    os.environ.get("HERMES_TWEET_BASE_URL")
    or os.environ.get("XQUIK_BASE_URL")
    or "https://xquik.com"
).rstrip("/")

if X_READ_BACKEND and X_READ_BACKEND not in {"hermes", "xquik"}:
    raise ValueError("X_READ_BACKEND must be hermes or xquik when configured.")
if X_READ_BACKEND in {"hermes", "xquik"} and not HERMES_TWEET_API_KEY:
    raise ValueError(
        "HERMES_TWEET_API_KEY or XQUIK_API_KEY is required when X_READ_BACKEND selects Hermes Tweet / Xquik."
    )

if not API_TOKEN and not HERMES_TWEET_API_KEY:
    raise ValueError(
        "OPENNEWS_TOKEN not configured. Get your API token at http://app.newsliquid.com/mcp, "
        "then set OPENNEWS_TOKEN or configure api_token in config.json. "
        "For read-only tweet search, set HERMES_TWEET_API_KEY or XQUIK_API_KEY instead."
    )

# ---------- Safety ----------
DEFAULT_MAX_ROWS = 100
_MAX_ROWS_ERROR = "TWITTER_MAX_ROWS or max_rows must be a positive integer."


def parse_max_rows(value: object) -> int:
    """Parse and validate the configured maximum result count."""
    if isinstance(value, bool):
        raise ValueError(_MAX_ROWS_ERROR)

    if isinstance(value, int):
        max_rows = value
    elif isinstance(value, str) and value.strip().isdecimal():
        max_rows = int(value)
    else:
        raise ValueError(_MAX_ROWS_ERROR)

    if max_rows < 1:
        raise ValueError(_MAX_ROWS_ERROR)
    return max_rows


_environment_max_rows = os.environ.get("TWITTER_MAX_ROWS")
MAX_ROWS = parse_max_rows(
    _cfg.get("max_rows", DEFAULT_MAX_ROWS)
    if not _environment_max_rows
    else _environment_max_rows
)


def clamp_limit(limit: int) -> int:
    """Clamp user-supplied limit to [1, MAX_ROWS]."""
    return min(max(1, limit), MAX_ROWS)


def make_serializable(obj):
    """Recursively convert non-JSON-serializable types."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [make_serializable(item) for item in obj]
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.decode("utf-8", errors="replace")
    return obj
