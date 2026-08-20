"""HTTP client for the 6551 Twitter API."""

import asyncio
import logging
import time
from typing import Any, Optional

import httpx

from opentwitter_mcp.config import (
    API_BASE_URL,
    API_TOKEN,
    HERMES_TWEET_API_KEY,
    HERMES_TWEET_BASE_URL,
    X_READ_BACKEND,
)

logger = logging.getLogger(__name__)

MAX_RETRIES = 2
HERMES_REQUEST_TIMEOUT_SECONDS = 70.0
HERMES_RETRY_DEADLINE_SECONDS = 210.0
HERMES_RETRY_BASE_DELAY_SECONDS = 0.25


class TwitterAPIClient:
    """Async HTTP client for the 6551 Twitter REST API."""

    def __init__(
        self,
        base_url: str = API_BASE_URL,
        token: str = API_TOKEN,
        hermes_base_url: str = HERMES_TWEET_BASE_URL,
        hermes_key: str = HERMES_TWEET_API_KEY,
        x_read_backend: str = X_READ_BACKEND,
        transport: httpx.AsyncBaseTransport | None = None,
        hermes_retry_delay: float = HERMES_RETRY_BASE_DELAY_SECONDS,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.hermes_base_url = hermes_base_url.rstrip("/")
        self.hermes_key = hermes_key
        self.x_read_backend = x_read_backend.strip().lower()
        if self.x_read_backend not in {"", "hermes", "xquik"}:
            raise ValueError("X_READ_BACKEND must be hermes or xquik when configured.")
        if self.x_read_backend in {"hermes", "xquik"} and not self.hermes_key:
            raise ValueError(
                "HERMES_TWEET_API_KEY or XQUIK_API_KEY is required when X_READ_BACKEND selects Hermes Tweet / Xquik."
            )
        self._transport = transport
        self._hermes_retry_delay = max(0.0, hermes_retry_delay)
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def use_hermes_backend(self) -> bool:
        """Return True when read-only search should use Hermes Tweet / Xquik."""
        if self.x_read_backend in {"hermes", "xquik"}:
            return True
        return bool(self.hermes_key) and not self.token

    def _headers(self) -> dict:
        if not self.token:
            raise RuntimeError(
                "OPENNEWS_TOKEN is not configured. "
                "The Hermes Tweet backend currently supports search_twitter and get_twitter_user_tweets only."
            )
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _hermes_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.hermes_key.startswith("xq_"):
            headers["x-api-key"] = self.hermes_key
        else:
            headers["Authorization"] = f"Bearer {self.hermes_key}"
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                transport=self._transport,
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
                resp = await client.request(method, url, headers=self._headers(), **kwargs)
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

    async def _request_hermes_search(
        self,
        query: str,
        max_results: int,
        product: str = "Top",
        cursor: str = "",
    ) -> Any:
        """Run a read-only Hermes Tweet / Xquik tweet search."""
        if not self.hermes_key:
            raise RuntimeError("HERMES_TWEET_API_KEY or XQUIK_API_KEY is required for the Hermes Tweet backend.")

        params = {
            "q": query,
            "limit": str(min(max(1, max_results), 100)),
            "queryType": "Latest" if product.lower() == "latest" else "Top",
        }
        if cursor:
            params["cursor"] = cursor

        request_deadline = time.monotonic() + HERMES_RETRY_DEADLINE_SECONDS
        last_error: Exception | None = None
        for attempt in range(MAX_RETRIES + 1):
            remaining = request_deadline - time.monotonic()
            if remaining <= 0:
                if last_error is not None:
                    raise last_error
                raise TimeoutError("Hermes Tweet / Xquik search exceeded its request deadline.")

            try:
                client = await self._get_client()
                resp = await client.request(
                    "GET",
                    f"{self.hermes_base_url}/api/v1/x/tweets/search",
                    params=params,
                    headers=self._hermes_headers(),
                    timeout=httpx.Timeout(min(HERMES_REQUEST_TIMEOUT_SECONDS, remaining)),
                )
                resp.raise_for_status()
                return resp.json()
            except (
                httpx.ConnectError,
                httpx.RemoteProtocolError,
                httpx.TimeoutException,
            ) as error:
                last_error = error
            except httpx.HTTPStatusError as error:
                if error.response.status_code != 429 and error.response.status_code < 500:
                    raise
                last_error = error

            if attempt == MAX_RETRIES:
                break
            await self._reset_client()
            remaining = request_deadline - time.monotonic()
            if remaining <= 0:
                break
            delay = self._hermes_retry_delay * (2**attempt)
            if (
                isinstance(last_error, httpx.HTTPStatusError)
                and last_error.response.status_code == 429
            ):
                retry_after = last_error.response.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = max(delay, float(retry_after))
                    except ValueError:
                        pass
            if delay >= remaining:
                break
            if delay > 0:
                await asyncio.sleep(delay)

        if last_error is not None:
            raise last_error
        raise RuntimeError("Hermes Tweet / Xquik search failed without an error response.")

    def _extract_hermes_page(
        self,
        payload: Any,
    ) -> tuple[list[Any], bool, str, dict[str, Any]]:
        """Extract one page from current and legacy response envelopes."""
        containers: list[dict[str, Any]] = []
        tweets: Any = []
        if isinstance(payload, dict):
            containers.append(payload)
            nested = payload.get("data")
            if isinstance(nested, dict):
                containers.append(nested)
            elif isinstance(nested, list):
                tweets = nested
        elif isinstance(payload, list):
            tweets = payload

        for container in containers:
            for key in ("tweets", "results", "items", "statuses"):
                candidate = container.get(key)
                if isinstance(candidate, list):
                    tweets = candidate
                    break
            if isinstance(tweets, list) and tweets:
                break

        has_more = False
        next_cursor = ""
        for container in containers:
            raw_has_more = container.get("has_more", container.get("has_next_page"))
            if isinstance(raw_has_more, bool):
                has_more = raw_has_more
            raw_cursor = container.get("next_cursor", container.get("nextCursor"))
            if isinstance(raw_cursor, str) and raw_cursor:
                next_cursor = raw_cursor

        meta: dict[str, Any] = {}
        if isinstance(payload, dict) and isinstance(payload.get("meta"), dict):
            meta = dict(payload["meta"])
        return (tweets if isinstance(tweets, list) else [], has_more, next_cursor, meta)

    def _normalize_hermes_search(self, payload: Any, query: str) -> dict:
        """Expose current and legacy Xquik page envelopes consistently."""
        tweets, has_more, next_cursor, meta = self._extract_hermes_page(payload)
        return {
            "data": tweets,
            "meta": {
                **meta,
                "has_more": has_more,
                "next_cursor": next_cursor,
                "query": query,
                "result_count": len(tweets),
                "source": "hermes_tweet",
            },
        }

    def _build_hermes_query(
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
    ) -> str:
        parts: list[str] = []
        if keywords:
            parts.append(keywords)
        if from_user:
            parts.append(f"from:{from_user.lstrip('@')}")
        if to_user:
            parts.append(f"to:{to_user.lstrip('@')}")
        if mention_user:
            parts.append(f"@{mention_user.lstrip('@')}")
        if hashtag:
            parts.append(f"#{hashtag.lstrip('#')}")
        if exclude_replies:
            parts.append("-filter:replies")
        if exclude_retweets:
            parts.append("-filter:nativeretweets")
        if min_likes > 0:
            parts.append(f"min_faves:{min_likes}")
        if min_retweets > 0:
            parts.append(f"min_retweets:{min_retweets}")
        if min_replies > 0:
            parts.append(f"min_replies:{min_replies}")
        if since_date:
            parts.append(f"since:{since_date}")
        if until_date:
            parts.append(f"until:{until_date}")
        if lang:
            parts.append(f"lang:{lang}")
        return " ".join(parts).strip() or "*"

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
        cursor: str = "",
    ) -> dict:
        """POST /open/twitter_user_tweets — Get user tweets"""
        if self.use_hermes_backend:
            query = self._build_hermes_query(
                from_user=username,
                exclude_replies=not include_replies,
                exclude_retweets=not include_retweets,
            )
            payload = await self._request_hermes_search(
                query,
                max_results,
                product,
                cursor,
            )
            return self._normalize_hermes_search(payload, query)

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
        cursor: str = "",
    ) -> dict:
        """POST /open/twitter_search — Twitter search"""
        if self.use_hermes_backend:
            query = self._build_hermes_query(
                keywords=keywords,
                from_user=from_user,
                to_user=to_user,
                mention_user=mention_user,
                hashtag=hashtag,
                exclude_replies=exclude_replies,
                exclude_retweets=exclude_retweets,
                min_likes=min_likes,
                min_retweets=min_retweets,
                min_replies=min_replies,
                since_date=since_date,
                until_date=until_date,
                lang=lang,
            )
            payload = await self._request_hermes_search(
                query,
                max_results,
                product,
                cursor,
            )
            return self._normalize_hermes_search(payload, query)

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

    async def get_twitter_article_by_id(self, article_id: str) -> dict:
        """POST /open/twitter_article_by_id — Get Twitter article by ID"""
        resp = await self._request("POST", f"{self.base_url}/open/twitter_article_by_id", json={"id": article_id})
        return resp.json()

    async def get_twitter_tweet_by_id(self, tw_id: str) -> dict:
        """POST /open/twitter_tweet_by_id — Get tweet by ID with nested reply/quote tweets"""
        resp = await self._request("POST", f"{self.base_url}/open/twitter_tweet_by_id", json={"twId": tw_id})
        return resp.json()

    async def get_twitter_watch(self) -> dict:
        """POST /open/twitter_watch — Get all Twitter monitoring users"""
        resp = await self._request("POST", f"{self.base_url}/open/twitter_watch", json={})
        return resp.json()

    async def add_twitter_watch(
        self,
        username: str,
        new_tweet: Optional[bool] = None,
        new_follow: Optional[bool] = None,
        new_unfollow: Optional[bool] = None,
        new_tweet_reply: Optional[bool] = None,
        new_tweet_quote: Optional[bool] = None,
        new_retweet: Optional[bool] = None,
        update_name: Optional[bool] = None,
        update_desc: Optional[bool] = None,
        update_avatar: Optional[bool] = None,
        update_banner: Optional[bool] = None,
        new_ca: Optional[bool] = None,
        tweet_topping: Optional[bool] = None,
    ) -> dict:
        """POST /open/twitter_watch_add — 添加Twitter监控用户"""
        body: dict[str, Any] = {"username": username}
        if new_tweet is not None:
            body["newTweetBol"] = new_tweet
        if new_follow is not None:
            body["newFlwBol"] = new_follow
        if new_unfollow is not None:
            body["newUnFlwBol"] = new_unfollow
        if new_tweet_reply is not None:
            body["newTweetReplyBol"] = new_tweet_reply
        if new_tweet_quote is not None:
            body["newTweetQuoteBol"] = new_tweet_quote
        if new_retweet is not None:
            body["newRetweetBol"] = new_retweet
        if update_name is not None:
            body["updateNameBol"] = update_name
        if update_desc is not None:
            body["updateDescBol"] = update_desc
        if update_avatar is not None:
            body["updateAvatarBol"] = update_avatar
        if update_banner is not None:
            body["updateBannerBol"] = update_banner
        if new_ca is not None:
            body["newCaBol"] = new_ca
        if tweet_topping is not None:
            body["tweetToppingBol"] = tweet_topping
        resp = await self._request("POST", f"{self.base_url}/open/twitter_watch_add", json=body)
        return resp.json()

    async def delete_twitter_watch(self, username: str) -> dict:
        """POST /open/twitter_watch_delete — Delete Twitter monitoring user"""
        resp = await self._request("POST", f"{self.base_url}/open/twitter_watch_delete", json={"username": username})
        return resp.json()

    async def get_twitter_quote_tweets_by_id(self, tweet_id: str, max_results: int = 20) -> dict:
        """POST /open/twitter_quote_tweets_by_id — Get quote tweets for a tweet"""
        body = {"id": tweet_id, "maxResults": max_results}
        resp = await self._request("POST", f"{self.base_url}/open/twitter_quote_tweets_by_id", json=body)
        return resp.json()

    async def get_twitter_retweet_users_by_id(self, tweet_id: str, cursor: str = "") -> dict:
        """POST /open/twitter_retweet_users_by_id — Get users who retweeted a tweet"""
        body: dict[str, Any] = {"id": tweet_id}
        if cursor:
            body["cursor"] = cursor
        resp = await self._request("POST", f"{self.base_url}/open/twitter_retweet_users_by_id", json=body)
        return resp.json()
