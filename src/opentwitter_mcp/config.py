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
API_TOKEN    = os.environ.get("OPENNEWS_TOKEN") or _cfg.get("api_token", "")

# 检查 token 是否配置
if not API_TOKEN:
    raise ValueError(
        "OPENNEWS_TOKEN not configured. Get your API token at http://app.newsliquid.com/mcp, "
        "then set the OPENNEWS_TOKEN environment variable or configure api_token in config.json."
    )

# ---------- Safety ----------
MAX_ROWS = int(os.environ.get("TWITTER_MAX_ROWS", 0) or _cfg.get("max_rows", 100))


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
