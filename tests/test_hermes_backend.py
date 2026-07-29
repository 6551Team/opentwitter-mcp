import json
import os
import unittest
from unittest.mock import AsyncMock, patch

import httpx

os.environ.setdefault("XQUIK_API_KEY", "xq_test")

from opentwitter_mcp.api_client import TwitterAPIClient


class HermesBackendTests(unittest.IsolatedAsyncioTestCase):
    async def test_search_uses_hermes_backend_with_x_api_key_header(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(
                200,
                json={
                    "data": {"tweets": [{"id": "1", "text": "hello"}]},
                    "meta": {"result_count": 1},
                },
            )

        client = TwitterAPIClient(
            token="",
            hermes_key="xq_test",
            hermes_base_url="https://xquik.test",
            x_read_backend="hermes",
            transport=httpx.MockTransport(handler),
        )

        result = await client.search_twitter(
            keywords="ai agents",
            from_user="alice",
            hashtag="mcp",
            exclude_retweets=True,
            min_likes=10,
            product="Latest",
            max_results=5,
        )

        self.assertEqual(result["data"], [{"id": "1", "text": "hello"}])
        self.assertEqual(result["meta"]["source"], "hermes_tweet")
        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(str(request.url.copy_with(query=None)), "https://xquik.test/api/v1/x/tweets/search")
        self.assertEqual(request.headers["x-api-key"], "xq_test")
        self.assertEqual(request.url.params["limit"], "5")
        self.assertEqual(request.url.params["queryType"], "Latest")
        self.assertEqual(
            request.url.params["q"],
            "ai agents from:alice #mcp -filter:nativeretweets min_faves:10",
        )

    async def test_user_tweets_uses_hermes_from_query_with_bearer_header(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={"data": [{"id": "2"}]})

        client = TwitterAPIClient(
            token="",
            hermes_key="plain-token",
            hermes_base_url="https://xquik.test/",
            x_read_backend="hermes",
            transport=httpx.MockTransport(handler),
        )

        result = await client.get_twitter_user_tweets("alice", max_results=12)

        self.assertEqual(result["data"], [{"id": "2"}])
        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(request.headers["Authorization"], "Bearer plain-token")
        self.assertEqual(
            request.url.params["q"],
            "from:alice -filter:replies -filter:nativeretweets",
        )
        self.assertEqual(request.url.params["limit"], "12")
        self.assertEqual(request.url.params["queryType"], "Latest")

    async def test_existing_twitter_token_backend_remains_default(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            return httpx.Response(200, json={"data": [{"id": "3"}]})

        client = TwitterAPIClient(
            base_url="https://api.6551.test",
            token="twitter-token",
            hermes_key="xq_test",
            x_read_backend="",
            transport=httpx.MockTransport(handler),
        )

        result = await client.search_twitter(keywords="bitcoin", max_results=20)

        self.assertEqual(result, {"data": [{"id": "3"}]})
        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(str(request.url), "https://api.6551.test/open/twitter_search")
        self.assertEqual(request.headers["Authorization"], "Bearer twitter-token")
        self.assertEqual(json.loads(request.content), {"maxResults": 20, "product": "Top", "keywords": "bitcoin"})

    async def test_search_follows_current_xquik_pagination_contract(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if request.url.params.get("cursor") == "page-2":
                return httpx.Response(
                    200,
                    json={
                        "tweets": [{"id": "2"}],
                        "has_next_page": False,
                        "next_cursor": "",
                    },
                )
            return httpx.Response(
                200,
                json={
                    "tweets": [{"id": "1"}],
                    "has_next_page": True,
                    "next_cursor": "page-2",
                },
            )

        client = TwitterAPIClient(
            token="",
            hermes_key="xq_test",
            hermes_base_url="https://xquik.test",
            x_read_backend="xquik",
            transport=httpx.MockTransport(handler),
            hermes_retry_delay=0,
        )

        first = await client.search_twitter(keywords="agents", max_results=3)
        second = await client.search_twitter(
            keywords="agents",
            max_results=3,
            cursor=first["meta"]["next_cursor"],
        )

        self.assertEqual(first["data"], [{"id": "1"}])
        self.assertEqual(first["meta"]["has_more"], True)
        self.assertEqual(first["meta"]["next_cursor"], "page-2")
        self.assertEqual(second["data"], [{"id": "2"}])
        self.assertEqual(second["meta"]["has_more"], False)
        self.assertEqual(second["meta"]["next_cursor"], "")
        self.assertEqual(len(requests), 2)
        self.assertEqual(requests[1].url.params["cursor"], "page-2")

    async def test_xquik_search_retries_transient_statuses(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            statuses = [503, 429, 200]
            status = statuses[len(requests) - 1]
            if status == 200:
                return httpx.Response(200, json={"tweets": [{"id": "1"}]})
            return httpx.Response(status, json={"error": "retry"})

        client = TwitterAPIClient(
            token="",
            hermes_key="xq_test",
            x_read_backend="xquik",
            transport=httpx.MockTransport(handler),
            hermes_retry_delay=0,
        )

        result = await client.search_twitter(keywords="agents", max_results=1)

        self.assertEqual(result["data"], [{"id": "1"}])
        self.assertEqual(len(requests), 3)

    async def test_xquik_search_respects_retry_after_header(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if len(requests) == 1:
                return httpx.Response(
                    429,
                    headers={"Retry-After": "2"},
                    json={"error": "rate_limit_exceeded"},
                )
            return httpx.Response(200, json={"tweets": [{"id": "1"}]})

        client = TwitterAPIClient(
            token="",
            hermes_key="xq_test",
            x_read_backend="xquik",
            transport=httpx.MockTransport(handler),
        )

        with patch(
            "opentwitter_mcp.api_client.asyncio.sleep",
            new_callable=AsyncMock,
        ) as sleep:
            result = await client.search_twitter(
                keywords="agents",
                max_results=1,
            )

        self.assertEqual(result["data"], [{"id": "1"}])
        self.assertEqual(len(requests), 2)
        sleep.assert_awaited_once_with(2.0)

    async def test_xquik_search_retries_connection_errors(self):
        requests = []

        def handler(request: httpx.Request) -> httpx.Response:
            requests.append(request)
            if len(requests) == 1:
                raise httpx.ConnectError("temporary", request=request)
            return httpx.Response(200, json={"tweets": [{"id": "1"}]})

        client = TwitterAPIClient(
            token="",
            hermes_key="xq_test",
            x_read_backend="xquik",
            transport=httpx.MockTransport(handler),
            hermes_retry_delay=0,
        )

        result = await client.search_twitter(keywords="agents", max_results=1)

        self.assertEqual(result["data"], [{"id": "1"}])
        self.assertEqual(len(requests), 2)

    async def test_xquik_search_uses_server_compatible_timeout(self):
        read_timeouts = []

        def handler(request: httpx.Request) -> httpx.Response:
            read_timeouts.append(request.extensions["timeout"]["read"])
            return httpx.Response(200, json={"tweets": []})

        client = TwitterAPIClient(
            token="",
            hermes_key="xq_test",
            x_read_backend="xquik",
            transport=httpx.MockTransport(handler),
        )

        await client.search_twitter(keywords="agents", max_results=1)

        self.assertGreaterEqual(read_timeouts[0], 60)

    def test_explicit_xquik_backend_requires_its_key(self):
        with self.assertRaisesRegex(ValueError, "XQUIK_API_KEY is required"):
            TwitterAPIClient(
                token="primary-token",
                hermes_key="",
                x_read_backend="xquik",
            )


if __name__ == "__main__":
    unittest.main()
