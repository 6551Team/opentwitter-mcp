"""HTTP client for the 6551 Twitter API."""

import logging
from typing import Any, Optional

import httpx

from opentwitter_mcp.config import API_BASE_URL, API_TOKEN

logger = logging.getLogger(__name__)

MAX_RETRIES = 2


class TwitterAPIClient:
    """Async HTTP client for the 6551 Twitter REST API."""

    def __init__(self, base_url: str = API_BASE_URL, token: str = API_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self._client: Optional[httpx.AsyncClient] = None

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers=self._headers(),
            )
        return self._client

    async def _reset_client(self):
        """Force close and recreate the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
        self._client = None

    async def close(self):
        await self._reset_client()

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Execute an HTTP request with automatic retry on connection errors."""
        last_exc = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                client = await self._get_client()
                resp = await client.request(method, url, **kwargs)
                resp.raise_for_status()
                return resp
            except (httpx.ConnectError, httpx.RemoteProtocolError) as e:
                last_exc = e
                logger.warning(
                    "Connection error (attempt %d/%d): %s",
                    attempt + 1, MAX_RETRIES + 1, repr(e),
                )
                await self._reset_client()
            except httpx.HTTPStatusError:
                raise
        raise last_exc  # type: ignore[misc]

    # ---------- Twitter endpoints ----------

    async def get_twitter_user_info(self, username: str) -> dict:
        """POST /open/twitter_user_info — Get Twitter user info by username"""
        resp = await self._request("POST", f"{self.base_url}/open/twitter_user_info", json={"username": username})
        return resp.json()

    async def get_twitter_user_by_id(self, user_id: str) -> dict:
        """POST /open/twitter_user_by_id — Get Twitter user info by ID"""
        resp = await self._request("POST", f"{self.base_url}/open/twitter_user_by_id", json={"userId": user_id})
        return resp.json()

    async def get_twitter_user_tweets(
        self,
        username: str,
        max_results: int = 20,
        product: str = "Latest",
        include_replies: bool = False,
        include_retweets: bool = False,
    ) -> dict:
        """POST /open/twitter_user_tweets — Get user tweets"""
        body = {
            "username": username,
            "maxResults": max_results,
            "product": product,
            "includeReplies": include_replies,
            "includeRetweets": include_retweets,
        }
        resp = await self._request("POST", f"{self.base_url}/open/twitter_user_tweets", json=body)
        return resp.json()

    async def search_twitter(
        self,
        keywords: Optional[str] = None,
        from_user: Optional[str] = None,
        to_user: Optional[str] = None,
        mention_user: Optional[str] = None,
        hashtag: Optional[str] = None,
        exclude_replies: bool = False,
        exclude_retweets: bool = False,
        min_likes: int = 0,
        min_retweets: int = 0,
        min_replies: int = 0,
        since_date: Optional[str] = None,
        until_date: Optional[str] = None,
        lang: Optional[str] = None,
        product: str = "Top",
        max_results: int = 20,
    ) -> dict:
        """POST /open/twitter_search — Twitter search"""
        body: dict[str, Any] = {
            "maxResults": max_results,
            "product": product,
        }
        if keywords:
            body["keywords"] = keywords
        if from_user:
            body["fromUser"] = from_user
        if to_user:
            body["toUser"] = to_user
        if mention_user:
            body["mentionUser"] = mention_user
        if hashtag:
            body["hashtag"] = hashtag
        if exclude_replies:
            body["excludeReplies"] = exclude_replies
        if exclude_retweets:
            body["excludeRetweets"] = exclude_retweets
        if min_likes > 0:
            body["minLikes"] = min_likes
        if min_retweets > 0:
            body["minRetweets"] = min_retweets
        if min_replies > 0:
            body["minReplies"] = min_replies
        if since_date:
            body["sinceDate"] = since_date
        if until_date:
            body["untilDate"] = until_date
        if lang:
            body["lang"] = lang

        resp = await self._request("POST", f"{self.base_url}/open/twitter_search", json=body)
        return resp.json()

    async def get_twitter_follower_events(
        self,
        username: str,
        is_follow: bool = True,
        max_results: int = 20,
    ) -> dict:
        """POST /open/twitter_follower_events — Get follow/unfollow events"""
        body = {
            "username": username,
            "isFollow": is_follow,
            "maxResults": max_results,
        }
        resp = await self._request("POST", f"{self.base_url}/open/twitter_follower_events", json=body)
        return resp.json()

    async def get_twitter_deleted_tweets(
        self,
        username: str,
        max_results: int = 20,
    ) -> dict:
        """POST /open/twitter_deleted_tweets — Get deleted tweets"""
        body = {
            "username": username,
            "maxResults": max_results,
        }
        resp = await self._request("POST", f"{self.base_url}/open/twitter_deleted_tweets", json=body)
        return resp.json()

    async def get_twitter_kol_followers(self, username: str) -> dict:
        """POST /open/twitter_kol_followers — Get KOL followers"""
        resp = await self._request("POST", f"{self.base_url}/open/twitter_kol_followers", json={"username": username})
        return resp.json()
