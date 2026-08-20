import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("XQUIK_API_KEY", "xq_test")

from opentwitter_mcp.tools import search_twitter


class RecordingAPI:
    def __init__(self):
        self.arguments = None

    async def search_twitter(self, **arguments):
        self.arguments = arguments
        return {
            "data": [{"id": "1"}],
            "meta": {
                "has_more": True,
                "next_cursor": "next-page",
            },
        }


class ToolLimitTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_tool_enforces_configured_limit_and_returns_cursor(self):
        api = RecordingAPI()
        context = SimpleNamespace(
            request_context=SimpleNamespace(
                lifespan_context=SimpleNamespace(api=api),
            ),
        )

        with patch("opentwitter_mcp.config.MAX_ROWS", 5):
            result = await search_twitter(
                context,
                keywords="agents",
                limit=100,
            )

        self.assertEqual(api.arguments["max_results"], 5)
        self.assertEqual(result["data"], [{"id": "1"}])
        self.assertEqual(result["has_more"], True)
        self.assertEqual(result["next_cursor"], "next-page")


if __name__ == "__main__":
    unittest.main()
