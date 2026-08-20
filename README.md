<p align="center">
  <b>Twitter MCP Server</b><br>
  Twitter/X Data · User Profiles · Tweet Search · Follower Events · KOL Tracking
</p>

<p align="center">
  <a href="./docs/README_ZH.md">中文</a> | <a href="./docs/README_JA.md">日本語</a> | <a href="./docs/README_KO.md">한국어</a>
</p>

---

## Quick Install

> **First, go to [http://app.newsliquid.com/mcp](http://app.newsliquid.com/mcp) to get your API Token.**

### Claude Code

```bash
claude mcp add twitter \
  -e OPENNEWS_TOKEN=<your-token> \
  -- uv --directory /path/to/twitter-mcp run twitter-mcp
```

> Replace `/path/to/twitter-mcp` with your local project path, and `<your-token>` with your Token.

To use the optional read-only Hermes Tweet / Xquik backend for tweet search instead:

```bash
claude mcp add twitter \
  -e X_READ_BACKEND=hermes \
  -e HERMES_TWEET_API_KEY=<your-hermes-or-xquik-key> \
  -- uv --directory /path/to/twitter-mcp run twitter-mcp
```

### OpenClaw

```bash
export OPENNEWS_TOKEN="<your-token>"
cp -r openclaw-skill/opentwitter ~/.openclaw/skills/
```

---

## Let AI Review & Install For You

Not sure if this MCP is safe? Paste the prompt below to your AI assistant — it will review the source code first, then install if safe:

> **Copy this prompt and send it to your AI assistant (replace `<project-path>` and `<your-token>` with actual values):**

```text
Please review and install the twitter-mcp MCP server for me. The project is at <project-path>.

Steps:
1. Review these files for security:
   - src/opentwitter_mcp/api_client.py — Confirm it connects only to the configured 6551 API and, when explicitly enabled, the configured Xquik endpoint
   - src/opentwitter_mcp/config.py — Confirm tokens are only read from local config.json or env vars, with no hardcoded secrets or leaks
   - src/opentwitter_mcp/tools.py — Confirm all tools only perform API queries, with no file writes, command execution, or dangerous operations
   - pyproject.toml — Confirm dependencies are only mcp, httpx, no suspicious packages
2. Tell me your conclusion: safe / risky / problematic, with specific reasons
3. If safe, run the install (get Token from http://app.newsliquid.com/mcp):
   claude mcp add twitter -e OPENNEWS_TOKEN=<your-token> -- uv --directory <project-path> run twitter-mcp
```

---

## What Can It Do?

Once connected, just ask your AI assistant:

| You say | It does |
|---------|---------|
| "Show @elonmusk's Twitter profile" | Get user profile info |
| "What did @VitalikButerin tweet recently" | Get user's recent tweets |
| "Search Bitcoin related tweets" | Keyword search |
| "Find tweets with #crypto hashtag" | Hashtag search |
| "Popular tweets about ETH with 1000+ likes" | Search with engagement filters |
| "Monitor @elonmusk with follower tracking" | Add user to watch list with options |
| "Who quoted this tweet" | Get quote tweets for a tweet |
| "Who retweeted this tweet" | Get users who retweeted a tweet |
| "Who followed @elonmusk recently" | Get new follower events |
| "Who unfollowed @elonmusk" | Get unfollower events |
| "What tweets did @elonmusk delete" | Get deleted tweets |
| "Which KOLs follow @elonmusk" | Get KOL followers |

---

## Available Tools

| Tool | Description |
|------|-------------|
| `get_twitter_user` | Get user profile by username |
| `get_twitter_user_by_id` | Get user profile by numeric ID |
| `get_twitter_user_tweets` | Get recent tweets from a user |
| `search_twitter` | Search tweets with basic filters |
| `search_twitter_advanced` | Advanced search with multiple filters |
| `get_twitter_follower_events` | Get follower/unfollower events |
| `get_twitter_deleted_tweets` | Get deleted tweets from a user |
| `get_twitter_kol_followers` | Get KOL (Key Opinion Leader) followers |
| `get_twitter_article_by_id` | Get Twitter article by ID |
| `get_twitter_tweet_by_id` | Get tweet by ID with nested reply/quote tweets |
| `get_twitter_quote_tweets_by_id` | Get tweets that quote a specific tweet |
| `get_twitter_retweet_users_by_id` | Get users who retweeted a specific tweet |
| `get_twitter_watch` | Get all Twitter monitoring users |
| `add_twitter_watch` | Add a Twitter user to monitoring list (with event type options) |
| `delete_twitter_watch` | Delete a Twitter user from monitoring list |

---

## Configuration

### Get API Token

Go to [http://app.newsliquid.com/mcp](http://app.newsliquid.com/mcp) to get your API Token.

Set the environment variable:

```bash
# macOS / Linux
export OPENNEWS_TOKEN="<your-token>"

# Windows PowerShell
$env:OPENNEWS_TOKEN = "<your-token>"
```

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENNEWS_TOKEN` | Yes, unless using the Hermes Tweet backend | 6551 API Bearer Token (get from http://app.newsliquid.com/mcp) |
| `TWITTER_TOKEN` | No | Legacy alternative to `OPENNEWS_TOKEN` |
| `TWITTER_API_BASE` | No | Override REST API URL |
| `TWITTER_MAX_ROWS` | No | Positive maximum results per query (default: 100) |
| `X_READ_BACKEND` | No | Set to `hermes` to use Hermes Tweet / Xquik for read-only tweet search |
| `HERMES_TWEET_API_KEY` | No | Hermes Tweet / Xquik API key for the optional read-only search backend |
| `XQUIK_API_KEY` | No | Alternative env name for `HERMES_TWEET_API_KEY` |
| `HERMES_TWEET_BASE_URL` | No | Override the Hermes Tweet / Xquik base URL (default: `https://xquik.com`) |
| `XQUIK_BASE_URL` | No | Alternative env name for `HERMES_TWEET_BASE_URL` |

Also supports `config.json` in the project root (env vars take precedence):

```json
{
  "api_base_url": "https://ai.6551.io",
  "api_token": "<your-token>",
  "max_rows": 100
}
```

When `OPENNEWS_TOKEN` or its legacy `TWITTER_TOKEN` alias is present, the 6551 API
remains the default. The Hermes Tweet backend is used only when
`X_READ_BACKEND=hermes` is set, or when no 6551 token is configured and
`HERMES_TWEET_API_KEY` or `XQUIK_API_KEY` is available. The
optional backend currently maps `search_twitter`, `search_twitter_advanced`, and
`get_twitter_user_tweets` to `/api/v1/x/tweets/search`; the other tools keep using
the 6551 API. Xquik search responses include `has_more` and `next_cursor`; pass
`next_cursor` as the tool's `cursor` argument to continue a partial page.

---

## WebSocket Real-time Subscriptions

**Endpoint**: `wss://ai.6551.io/open/twitter_wss?token=YOUR_TOKEN`

Subscribe to real-time events from your monitored Twitter accounts.

### Heartbeat

To keep the connection alive, the client can send `ping`, and the server responds with `pong`.

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
- `NEW_FOLLOWER` - This account followed a user
- `NEW_UNFOLLOWER` - This account unfollowed a user

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

<details>
<summary><b>Other Clients — Manual Install</b> (click to expand)</summary>

> In all configs below, replace `/path/to/twitter-mcp` with your actual local project path, and `<your-token>` with your Token from [http://app.newsliquid.com/mcp](http://app.newsliquid.com/mcp).

### Claude Desktop

Edit config (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "OPENNEWS_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json` or Settings > MCP Servers:

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "OPENNEWS_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "OPENNEWS_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Cline

VS Code sidebar > Cline > MCP Servers > Configure, edit `cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "OPENNEWS_TOKEN": "<your-token>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Continue.dev

`~/.continue/config.yaml`:

```yaml
mcpServers:
  - name: twitter
    command: uv
    args:
      - --directory
      - /path/to/twitter-mcp
      - run
      - twitter-mcp
    env:
      OPENNEWS_TOKEN: <your-token>
```

### Cherry Studio

Settings > MCP Servers > Add > Type stdio: Command `uv`, Args `--directory /path/to/twitter-mcp run twitter-mcp`, Env `OPENNEWS_TOKEN`.

### Zed Editor

`~/.config/zed/settings.json`:

```json
{
  "context_servers": {
    "twitter": {
      "command": {
        "path": "uv",
        "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
        "env": {
          "OPENNEWS_TOKEN": "<your-token>"
        }
      }
    }
  }
}
```

### Any stdio MCP client

```bash
OPENNEWS_TOKEN=<your-token> \
  uv --directory /path/to/twitter-mcp run twitter-mcp
```

</details>

---

## Compatibility

| Client | Install Method | Status |
|--------|---------------|--------|
| **Claude Code** | `claude mcp add` | One-liner |
| **OpenClaw** | Copy skill directory | One-liner |
| Claude Desktop | JSON config | Supported |
| Cursor | JSON config | Supported |
| Windsurf | JSON config | Supported |
| Cline | JSON config | Supported |
| Continue.dev | YAML / JSON | Supported |
| Cherry Studio | GUI | Supported |
| Zed | JSON config | Supported |

---

## Development

```bash
cd /path/to/twitter-mcp
uv sync
uv run twitter-mcp
```

```bash
# MCP Inspector
npx @modelcontextprotocol/inspector uv --directory /path/to/twitter-mcp run twitter-mcp
```

### Project Structure

```
├── README.md
├── docs/
│   ├── README_JA.md           # 日本語
│   └── README_KO.md           # 한국어
├── openclaw-skill/opentwitter/    # OpenClaw Skill
├── pyproject.toml
├── config.json
└── src/opentwitter_mcp/
    ├── server.py              # Entry point
    ├── app.py                 # FastMCP instance
    ├── config.py              # Config loader
    ├── api_client.py          # HTTP client
    └── tools.py               # 8 tools
```

## License

MIT

Xquik is an independent third-party service. Not affiliated with X Corp. "Twitter" and "X" are trademarks of X Corp.
