---
name: opentwitter
description: Twitter/X data via the 6551 API. Supports user profiles, tweet search, user tweets, follower events, deleted tweets, and KOL followers.

user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - TWITTER_TOKEN
      bins:
        - curl
    primaryEnv: TWITTER_TOKEN
    emoji: "\U0001F426"
    install:
      - id: curl
        kind: brew
        formula: curl
        label: curl (HTTP client)
    os:
      - darwin
      - linux
      - win32
  version: 1.0.0
---

# Twitter/X Data Skill

Query Twitter/X data from the 6551 platform REST API. All endpoints require a Bearer token via `$TWITTER_TOKEN`.

**Get your token**: https://6551.io/mcp

**Base URL**: `https://ai.6551.io`

## Authentication

All requests require the header:
```
Authorization: Bearer $TWITTER_TOKEN
```

---

## Twitter Operations

### 1. Get Twitter User Info

Get user profile by username.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_user_info" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk"}'
```

### 2. Get Twitter User by ID

Get user profile by numeric ID.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_user_by_id" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"userId": "44196397"}'
```

### 3. Get User Tweets

Get recent tweets from a user.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_user_tweets" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk", "maxResults": 20, "product": "Latest"}'
```

| Parameter         | Type    | Default  | Description                    |
|------------------|---------|----------|--------------------------------|
| `username`       | string  | required | Twitter username (without @)   |
| `maxResults`     | integer | 20       | Max tweets (1-100)             |
| `product`        | string  | "Latest" | "Latest" or "Top"              |
| `includeReplies` | boolean | false    | Include reply tweets           |
| `includeRetweets`| boolean | false    | Include retweets               |

### 4. Search Twitter

Search tweets with various filters.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_search" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "bitcoin", "maxResults": 20, "product": "Top"}'
```

**Search from specific user:**
```bash
curl -s -X POST "https://ai.6551.io/open/twitter_search" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"fromUser": "VitalikButerin", "maxResults": 20}'
```

**Search by hashtag:**
```bash
curl -s -X POST "https://ai.6551.io/open/twitter_search" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hashtag": "crypto", "minLikes": 100, "maxResults": 20}'
```

### Twitter Search Parameters

| Parameter         | Type    | Default | Description                         |
|------------------|---------|---------|-------------------------------------|
| `keywords`       | string  | -       | Search keywords                     |
| `fromUser`       | string  | -       | Tweets from specific user           |
| `toUser`         | string  | -       | Tweets to specific user             |
| `mentionUser`    | string  | -       | Tweets mentioning user              |
| `hashtag`        | string  | -       | Filter by hashtag (without #)       |
| `excludeReplies` | boolean | false   | Exclude reply tweets                |
| `excludeRetweets`| boolean | false   | Exclude retweets                    |
| `minLikes`       | integer | 0       | Minimum likes threshold             |
| `minRetweets`    | integer | 0       | Minimum retweets threshold          |
| `minReplies`     | integer | 0       | Minimum replies threshold           |
| `sinceDate`      | string  | -       | Start date (YYYY-MM-DD)             |
| `untilDate`      | string  | -       | End date (YYYY-MM-DD)               |
| `lang`           | string  | -       | Language code (e.g. "en", "zh")     |
| `product`        | string  | "Top"   | "Top" or "Latest"                   |
| `maxResults`     | integer | 20      | Max tweets (1-100)                  |

### 5. Get Follower Events

Get new followers or unfollowers for a user.

```bash
# Get new followers
curl -s -X POST "https://ai.6551.io/open/twitter_follower_events" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk", "isFollow": true, "maxResults": 20}'

# Get unfollowers
curl -s -X POST "https://ai.6551.io/open/twitter_follower_events" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk", "isFollow": false, "maxResults": 20}'
```

| Parameter    | Type    | Default | Description                              |
|-------------|---------|---------|------------------------------------------|
| `username`  | string  | required| Twitter username (without @)             |
| `isFollow`  | boolean | true    | true=new followers, false=unfollowers    |
| `maxResults`| integer | 20      | Max events (1-100)                       |

### 6. Get Deleted Tweets

Get deleted tweets from a user.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_deleted_tweets" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk", "maxResults": 20}'
```

| Parameter    | Type    | Default | Description                    |
|-------------|---------|---------|--------------------------------|
| `username`  | string  | required| Twitter username (without @)   |
| `maxResults`| integer | 20      | Max tweets (1-100)             |

### 7. Get KOL Followers

Get which KOLs (Key Opinion Leaders) are following a user.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_kol_followers" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk"}'
```

| Parameter   | Type   | Default | Description                    |
|------------|--------|---------|--------------------------------|
| `username` | string | required| Twitter username (without @)   |

### 8. Get Twitter Article by ID

Get Twitter article by ID.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_article_by_id" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": "article_id"}'
```

| Parameter | Type   | Default | Description           |
|-----------|--------|---------|----------------------|
| `id`      | string | required| Twitter article ID   |

### 9. Get Twitter Watch List

Get all Twitter monitoring users for the current user.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_watch" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 10. Add Twitter Watch

Add a Twitter user to monitoring list.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_watch_add" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk"}'
```

| Parameter  | Type   | Default | Description                    |
|-----------|--------|---------|--------------------------------|
| `username`| string | required| Twitter username (without @)   |

### 11. Delete Twitter Watch

Delete a Twitter user from monitoring list.

```bash
curl -s -X POST "https://ai.6551.io/open/twitter_watch_delete" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"id": 123}'
```

| Parameter | Type    | Default | Description                      |
|-----------|---------|---------|----------------------------------|
| `id`      | integer | required| Monitoring record ID to delete   |

---

## WebSocket Real-time Subscriptions

**Endpoint**: `wss://ai.6551.io/open/twitter_wss?token=YOUR_TOKEN`

Subscribe to real-time events from your monitored Twitter accounts.

### Subscribe to Twitter Events

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "twitter.subscribe"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true
  }
}
```

### Unsubscribe

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "twitter.unsubscribe"
}
```

### Server Push - Twitter Event

When a monitored account has activity, the server pushes:

```json
{
  "jsonrpc": "2.0",
  "method": "twitter.event",
  "params": {
    "id": 123456,
    "twAccount": "elonmusk",
    "twUserName": "Elon Musk",
    "profileUrl": "https://twitter.com/elonmusk",
    "eventType": "NEW_TWEET",
    "content": "...",
    "ca": "0x1234...",
    "remark": "Custom note",
    "createdAt": "2026-03-06T10:00:00Z"
  }
}
```

**Note**: The `content` field structure varies by event type (see below).
```

**Event Types and Content Structure**:

#### Tweet Events
- `NEW_TWEET` - New tweet posted
- `NEW_TWEET_REPLY` - New reply tweet
- `NEW_TWEET_QUOTE` - New quote tweet
- `NEW_RETWEET` - Retweeted
- `CA` - Tweet with CA address

Content structure for tweet events:
```json
{
  "id": "1234567890",
  "text": "Tweet content...",
  "createdAt": "2026-03-06T10:00:00Z",
  "language": "en",
  "retweetCount": 100,
  "favoriteCount": 500,
  "replyCount": 20,
  "quoteCount": 10,
  "viewCount": 10000,
  "userScreenName": "elonmusk",
  "userName": "Elon Musk",
  "userIdStr": "44196397",
  "userFollowers": 170000000,
  "userVerified": true,
  "conversationId": "1234567890",
  "isReply": false,
  "isQuote": false,
  "hashtags": ["crypto", "bitcoin"],
  "media": [
    {
      "type": "photo",
      "url": "https://...",
      "thumbUrl": "https://..."
    }
  ],
  "urls": [
    {
      "url": "https://...",
      "expandedUrl": "https://...",
      "displayUrl": "example.com"
    }
  ],
  "mentions": [
    {
      "username": "VitalikButerin",
      "name": "Vitalik Buterin"
    }
  ]
}
```

#### Follower Events
- `NEW_FOLLOWER` - New follower
- `NEW_UNFOLLOWER` - Unfollower event

Content structure for follower events (array):
```json
[
  {
    "id": 123,
    "twId": 44196397,
    "twAccount": "elonmusk",
    "twUserName": "Elon Musk",
    "twUserLabel": "Verified",
    "description": "User bio...",
    "profileUrl": "https://...",
    "bannerUrl": "https://...",
    "followerCount": 170000000,
    "friendCount": 500,
    "createdAt": "2026-03-06T10:00:00Z"
  }
]
```

#### Profile Update Events
- `UPDATE_NAME` - Username changed (content: new name string)
- `UPDATE_DESCRIPTION` - Bio updated (content: new description string)
- `UPDATE_AVATAR` - Profile picture changed (content: new avatar URL string)
- `UPDATE_BANNER` - Banner image changed (content: new banner URL string)

#### Other Events
- `TWEET_TOPPING` - Tweet pinned
- `DELETE` - Tweet deleted
- `SYSTEM` - System event
- `TRANSLATE` - Tweet translation
- `CA_CREATE` - CA token created

---

## Data Structures

### Twitter User

```json
{
  "userId": "44196397",
  "screenName": "elonmusk",
  "name": "Elon Musk",
  "description": "...",
  "followersCount": 170000000,
  "friendsCount": 500,
  "statusesCount": 30000,
  "verified": true
}
```

### Tweet

```json
{
  "id": "1234567890",
  "text": "Tweet content...",
  "createdAt": "2024-02-20T12:00:00Z",
  "retweetCount": 1000,
  "favoriteCount": 5000,
  "replyCount": 200,
  "userScreenName": "elonmusk",
  "hashtags": ["crypto", "bitcoin"],
  "urls": [{"url": "https://..."}]
}
```

---

## Common Workflows

### Crypto Twitter KOL Tweets
```bash
curl -s -X POST "https://ai.6551.io/open/twitter_user_tweets" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "VitalikButerin", "maxResults": 10}'
```

### Trending Crypto Tweets
```bash
curl -s -X POST "https://ai.6551.io/open/twitter_search" \
  -H "Authorization: Bearer $TWITTER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"keywords": "bitcoin", "minLikes": 1000, "product": "Top", "maxResults": 20}'
```

## Notes

- Get your API token at https://6551.io/mcp
- Rate limits apply; max 100 results per request
- Twitter usernames should not include the @ symbol
