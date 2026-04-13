"""Twitter tools — search and retrieve Twitter/X data via REST API.

Uses POST /open/twitter_* endpoints as the data source.
"""

from mcp.server.fastmcp import Context

from opentwitter_mcp.app import mcp
from opentwitter_mcp.config import make_serializable


@mcp.tool()
async def get_twitter_user(username: str, ctx: Context) -> dict:
    """Get Twitter/X user profile information by username.

    Args:
        username: Twitter username (without @, e.g. "elonmusk").
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_twitter_user_info(username)
        return make_serializable({"success": True, "data": result.get("data")})
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_user_by_id(user_id: str, ctx: Context) -> dict:
    """Get Twitter/X user profile information by user ID.

    Args:
        user_id: Twitter user ID (numeric string).
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_twitter_user_by_id(user_id)
        return make_serializable({"success": True, "data": result.get("data")})
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_user_tweets(
    username: str,
    ctx: Context,
    limit: int = 20,
    include_replies: bool = False,
    include_retweets: bool = False,
) -> dict:
    """Get recent tweets from a specific Twitter/X user.

    Args:
        username: Twitter username (without @).
        limit: Maximum tweets to return (default 20, max 100).
        include_replies: Include reply tweets (default False).
        include_retweets: Include retweets (default False).
    """
    api = ctx.request_context.lifespan_context.api
    limit = min(max(1, limit), 100)
    try:
        result = await api.get_twitter_user_tweets(
            username=username,
            max_results=limit,
            include_replies=include_replies,
            include_retweets=include_retweets,
        )
        data = result.get("data", [])
        return make_serializable({
            "success": True,
            "username": username,
            "data": data,
            "count": len(data) if isinstance(data, list) else 0,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def search_twitter(
    ctx: Context,
    keywords: str = "",
    from_user: str = "",
    hashtag: str = "",
    min_likes: int = 0,
    limit: int = 20,
) -> dict:
    """Search Twitter/X for tweets matching criteria.

    Args:
        keywords: Search keywords.
        from_user: Filter tweets from specific user (without @).
        hashtag: Filter by hashtag (without #).
        min_likes: Minimum likes threshold.
        limit: Maximum tweets to return (default 20, max 100).
    """
    api = ctx.request_context.lifespan_context.api
    limit = min(max(1, limit), 100)
    try:
        result = await api.search_twitter(
            keywords=keywords or None,
            from_user=from_user or None,
            hashtag=hashtag or None,
            min_likes=min_likes,
            max_results=limit,
        )
        data = result.get("data", [])
        return make_serializable({
            "success": True,
            "data": data,
            "count": len(data) if isinstance(data, list) else 0,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def search_twitter_advanced(
    ctx: Context,
    keywords: str = "",
    from_user: str = "",
    to_user: str = "",
    mention_user: str = "",
    hashtag: str = "",
    exclude_replies: bool = False,
    exclude_retweets: bool = False,
    min_likes: int = 0,
    min_retweets: int = 0,
    min_replies: int = 0,
    since_date: str = "",
    until_date: str = "",
    lang: str = "",
    product: str = "Top",
    limit: int = 20,
) -> dict:
    """Advanced Twitter/X search with multiple filters.

    Args:
        keywords: Search keywords.
        from_user: Filter tweets from specific user.
        to_user: Filter tweets to specific user.
        mention_user: Filter tweets mentioning specific user.
        hashtag: Filter by hashtag (without #).
        exclude_replies: Exclude reply tweets.
        exclude_retweets: Exclude retweets.
        min_likes: Minimum likes threshold.
        min_retweets: Minimum retweets threshold.
        min_replies: Minimum replies threshold.
        since_date: Start date (YYYY-MM-DD).
        until_date: End date (YYYY-MM-DD).
        lang: Language code (e.g. "en", "zh").
        product: Sort by "Top" or "Latest" (default "Top").
        limit: Maximum tweets to return (default 20, max 100).
    """
    api = ctx.request_context.lifespan_context.api
    limit = min(max(1, limit), 100)
    try:
        result = await api.search_twitter(
            keywords=keywords or None,
            from_user=from_user or None,
            to_user=to_user or None,
            mention_user=mention_user or None,
            hashtag=hashtag or None,
            exclude_replies=exclude_replies,
            exclude_retweets=exclude_retweets,
            min_likes=min_likes,
            min_retweets=min_retweets,
            min_replies=min_replies,
            since_date=since_date or None,
            until_date=until_date or None,
            lang=lang or None,
            product=product,
            max_results=limit,
        )
        data = result.get("data", [])
        return make_serializable({
            "success": True,
            "data": data,
            "count": len(data) if isinstance(data, list) else 0,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_follower_events(
    username: str,
    ctx: Context,
    is_follow: bool = True,
    limit: int = 20,
) -> dict:
    """Get follower/unfollower events for a Twitter/X user.

    Args:
        username: Twitter username (without @).
        is_follow: True for new followers, False for unfollowers.
        limit: Maximum events to return (default 20, max 100).
    """
    api = ctx.request_context.lifespan_context.api
    limit = min(max(1, limit), 100)
    try:
        result = await api.get_twitter_follower_events(
            username=username,
            is_follow=is_follow,
            max_results=limit,
        )
        data = result.get("data", [])
        return make_serializable({
            "success": True,
            "username": username,
            "is_follow": is_follow,
            "data": data,
            "count": len(data) if isinstance(data, list) else 0,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_deleted_tweets(
    username: str,
    ctx: Context,
    limit: int = 20,
) -> dict:
    """Get deleted tweets from a Twitter/X user.

    Args:
        username: Twitter username (without @).
        limit: Maximum tweets to return (default 20, max 100).
    """
    api = ctx.request_context.lifespan_context.api
    limit = min(max(1, limit), 100)
    try:
        result = await api.get_twitter_deleted_tweets(
            username=username,
            max_results=limit,
        )
        data = result.get("data", [])
        return make_serializable({
            "success": True,
            "username": username,
            "data": data,
            "count": len(data) if isinstance(data, list) else 0,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_kol_followers(username: str, ctx: Context) -> dict:
    """Get KOL (Key Opinion Leader) followers for a Twitter/X user.

    Returns which influential accounts (KOLs) are following this user.

    Args:
        username: Twitter username (without @).
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_twitter_kol_followers(username)
        data = result.get("data", {})
        return make_serializable({
            "success": True,
            "username": username,
            "data": data,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_article_by_id(article_id: str, ctx: Context) -> dict:
    """Get Twitter article by ID.

    Args:
        article_id: Twitter article ID.
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_twitter_article_by_id(article_id)
        return make_serializable({"success": True, "data": result.get("data")})
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_tweet_by_id(tw_id: str, ctx: Context) -> dict:
    """Get a specific tweet by its ID, including nested reply/quote tweets.

    This endpoint retrieves a tweet by ID and automatically fetches any tweets
    it replies to or quotes, providing complete context.

    Args:
        tw_id: Twitter tweet ID (numeric string).

    Returns:
        Tweet data with nested replyStatus and quotedStatus if applicable.
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_twitter_tweet_by_id(tw_id)
        return make_serializable({"success": True, "data": result.get("data")})
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_watch(ctx: Context) -> dict:
    """Get all Twitter monitoring users for the current user.

    Returns a list of Twitter accounts being monitored.
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_twitter_watch()
        data = result.get("data", [])
        return make_serializable({
            "success": True,
            "data": data,
            "count": len(data) if isinstance(data, list) else 0,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def add_twitter_watch(
    username: str,
    ctx: Context,
    new_tweet: bool | None = None,
    new_follow: bool | None = None,
    new_unfollow: bool | None = None,
    new_tweet_reply: bool | None = None,
    new_tweet_quote: bool | None = None,
    new_retweet: bool | None = None,
    update_name: bool | None = None,
    update_desc: bool | None = None,
    update_avatar: bool | None = None,
    update_banner: bool | None = None,
    new_ca: bool | None = None,
    tweet_topping: bool | None = None,
) -> dict:
    """Add a Twitter user to monitoring list.

    Args:
        username: Twitter username to monitor (without @).
        new_tweet: Monitor new tweets (default: true on server).
        new_follow: Monitor new followers (default: false on server).
        new_unfollow: Monitor unfollowers (default: false on server).
        new_tweet_reply: Monitor tweet replies (default: true on server).
        new_tweet_quote: Monitor quote tweets (default: true on server).
        new_retweet: Monitor retweets (default: true on server).
        update_name: Monitor username changes (default: true on server).
        update_desc: Monitor bio/description changes (default: true on server).
        update_avatar: Monitor profile picture changes (default: true on server).
        update_banner: Monitor banner image changes (default: true on server).
        new_ca: Monitor CA (contract address) events (default: false on server).
        tweet_topping: Monitor tweet pinning events (default: false on server).
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.add_twitter_watch(
            username,
            new_tweet=new_tweet,
            new_follow=new_follow,
            new_unfollow=new_unfollow,
            new_tweet_reply=new_tweet_reply,
            new_tweet_quote=new_tweet_quote,
            new_retweet=new_retweet,
            update_name=update_name,
            update_desc=update_desc,
            update_avatar=update_avatar,
            update_banner=update_banner,
            new_ca=new_ca,
            tweet_topping=tweet_topping,
        )
        return make_serializable({"success": True, "data": result.get("data")})
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def delete_twitter_watch(username: str, ctx: Context) -> dict:
    """Delete a Twitter user from monitoring list.

    Args:
        username: Twitter username to delete from monitoring (without @).
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.delete_twitter_watch(username)
        return make_serializable({"success": True, "data": result.get("data")})
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_quote_tweets_by_id(
    tweet_id: str,
    ctx: Context,
    limit: int = 20,
) -> dict:
    """Get tweets that quote a specific tweet.

    Args:
        tweet_id: Twitter tweet ID (numeric string).
        limit: Maximum tweets to return (default 20, max 100).
    """
    api = ctx.request_context.lifespan_context.api
    limit = min(max(1, limit), 100)
    try:
        result = await api.get_twitter_quote_tweets_by_id(tweet_id, max_results=limit)
        data = result.get("data", [])
        return make_serializable({
            "success": True,
            "tweet_id": tweet_id,
            "data": data,
            "count": result.get("total", len(data) if isinstance(data, list) else 0),
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}


@mcp.tool()
async def get_twitter_retweet_users_by_id(
    tweet_id: str,
    ctx: Context,
    cursor: str = "",
) -> dict:
    """Get users who retweeted a specific tweet.

    Args:
        tweet_id: Twitter tweet ID (numeric string).
        cursor: Pagination cursor for next page (empty for first page).
    """
    api = ctx.request_context.lifespan_context.api
    try:
        result = await api.get_twitter_retweet_users_by_id(tweet_id, cursor=cursor)
        data = result.get("data", {})
        return make_serializable({
            "success": True,
            "tweet_id": tweet_id,
            "data": data,
        })
    except Exception as e:
        return {"success": False, "error": str(e) or repr(e)}
