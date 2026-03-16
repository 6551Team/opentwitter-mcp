<p align="center">
  <b>Twitter MCP Server</b><br>
  Twitter/X 数据 · 用户资料 · 推文搜索 · 关注事件 · KOL 追踪
</p>

<p align="center">
  <a href="../README.md">English</a> | <a href="./README_JA.md">日本語</a> | <a href="./README_KO.md">한국어</a>
</p>

---

## 快速安装

> **首先前往 [https://6551.io/mcp](https://6551.io/mcp) 申请你的 API Token。**

### Claude Code

```bash
claude mcp add twitter \
  -e TWITTER_TOKEN=<your-token> \
  -- uv --directory /path/to/twitter-mcp run twitter-mcp
```

> `/path/to/twitter-mcp` 替换为你本地的项目路径，`<your-token>` 替换为你申请的 Token。

### OpenClaw

```bash
export TWITTER_TOKEN="<your-token>"
cp -r openclaw-skill/opentwitter ~/.openclaw/skills/
```

---

## 让 AI 帮你审查并安装

不确定这个 MCP 是否安全？把下面这段 prompt 发给你的 AI 助手，让它先审查源码再决定是否安装：

> **复制下方 prompt，粘贴给你的 AI 助手（将 `<项目路径>` 和 `<your-token>` 替换为实际值）：**

```text
请帮我审查并安装 twitter-mcp 这个 MCP server。项目在本地 <项目路径> 目录。

步骤：
1. 审查项目内包括但不限于以下文件的安全性：
   - src/twitter_mcp/api_client.py — 确认只连接了 ai.6551.io，没有向其他地址发送数据
   - src/twitter_mcp/config.py — 确认 token 只从本地 config.json 或环境变量读取，没有硬编码或外泄
   - src/twitter_mcp/tools.py — 确认所有工具只做 API 查询，没有文件写入、命令执行或其他危险操作
   - pyproject.toml — 确认依赖项只有 mcp、httpx，没有可疑包
2. 告诉我审查结论：安全/有风险/有问题，以及具体理由
3. 如果安全，帮我执行安装（Token 从 https://6551.io/mcp 申请）：
   claude mcp add twitter -e TWITTER_TOKEN=<your-token> -- uv --directory <项目路径> run twitter-mcp
```

---

## 它能做什么？

连接后，直接对你的 AI 助手说：

| 你说 | 它做 |
|------|------|
| "查看 elonmusk 的 Twitter 资料" | 获取用户资料 |
| "VitalikButerin 最近发了什么推文" | 获取用户推文 |
| "搜索 Bitcoin 相关推文" | 关键词搜索 |
| "找 #crypto 标签的推文" | 标签搜索 |
| "ETH 相关的热门推文，1000 赞以上" | 互动量筛选 |
| "最近谁关注了 elonmusk" | 获取新关注者 |
| "谁取关了 elonmusk" | 获取取关事件 |
| "elonmusk 删了哪些推文" | 获取删推数据 |
| "哪些大V关注了 elonmusk" | 获取大V关注者 |

---

## 可用工具一览

| 工具 | 说明 |
|------|------|
| `get_twitter_user` | 通过用户名获取资料 |
| `get_twitter_user_by_id` | 通过 ID 获取资料 |
| `get_twitter_user_tweets` | 获取用户推文 |
| `search_twitter` | 基础搜索 |
| `search_twitter_advanced` | 高级搜索（多过滤器） |
| `get_twitter_follower_events` | 获取关注/取关事件 |
| `get_twitter_deleted_tweets` | 获取删推数据 |
| `get_twitter_kol_followers` | 获取大V关注者 |
| `get_twitter_article_by_id` | 通过 ID 获取 Twitter 文章 |
| `get_twitter_tweet_by_id` | 通过 ID 获取推文（含嵌套回复/引用） |
| `get_twitter_watch` | 获取所有监控的 Twitter 用户 |
| `add_twitter_watch` | 添加 Twitter 用户到监控列表 |
| `delete_twitter_watch` | 从监控列表删除 Twitter 用户 |

---

## 配置

### 获取 API Token

前往 [https://6551.io/mcp](https://6551.io/mcp) 申请你的 API Token。

设置环境变量：

```bash
# macOS / Linux
export TWITTER_TOKEN="<your-token>"

# Windows PowerShell
$env:TWITTER_TOKEN = "<your-token>"
```

| 变量 | 必填 | 说明 |
|------|------|------|
| `TWITTER_TOKEN` | **是** | 6551 API Bearer Token（从 https://6551.io/mcp 申请） |
| `TWITTER_API_BASE` | 否 | 覆盖 REST API 地址 |
| `TWITTER_MAX_ROWS` | 否 | 单次最大结果数（默认 100） |

也支持项目根目录 `config.json`（环境变量优先级更高）：

```json
{
  "api_base_url": "https://ai.6551.io",
  "api_token": "<your-token>",
  "max_rows": 100
}
```

---

## WebSocket 实时订阅

**端点**: `wss://ai.6551.io/open/twitter_wss?token=YOUR_TOKEN`

订阅你监控的 Twitter 账号的实时事件。

### 订阅 Twitter 事件

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "twitter.subscribe"
}
```

**响应**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true
  }
}
```

### 取消订阅

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "twitter.unsubscribe"
}
```

### 服务端推送 - Twitter 事件

当监控的账号有活动时，服务端推送：

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
    "remark": "自定义备注",
    "createdAt": "2026-03-06T10:00:00Z"
  }
}
```

**说明**：`content` 字段的结构根据事件类型不同而不同（见下方说明）。
```

**事件类型和内容结构**:

#### 推文事件
- `NEW_TWEET` - 发布新推文
- `NEW_TWEET_REPLY` - 发布回复推文
- `NEW_TWEET_QUOTE` - 发布引用推文
- `NEW_RETWEET` - 转推
- `CA` - 包含 CA 地址的推文

推文事件的 content 结构：
```json
{
  "id": "1234567890",
  "text": "推文内容...",
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

#### 关注事件
- `NEW_FOLLOWER` - 新增关注者
- `NEW_UNFOLLOWER` - 取消关注

关注事件的 content 结构（数组）：
```json
[
  {
    "id": 123,
    "twId": 44196397,
    "twAccount": "elonmusk",
    "twUserName": "Elon Musk",
    "twUserLabel": "Verified",
    "description": "用户简介...",
    "profileUrl": "https://...",
    "bannerUrl": "https://...",
    "followerCount": 170000000,
    "friendCount": 500,
    "createdAt": "2026-03-06T10:00:00Z"
  }
]
```

#### 资料更新事件
- `UPDATE_NAME` - 用户名变更（content: 新名称字符串）
- `UPDATE_DESCRIPTION` - 简介更新（content: 新简介字符串）
- `UPDATE_AVATAR` - 头像变更（content: 新头像 URL 字符串）
- `UPDATE_BANNER` - 背景图变更（content: 新背景图 URL 字符串）

#### 其他事件
- `TWEET_TOPPING` - 推文置顶
- `DELETE` - 推文删除
- `SYSTEM` - 系统事件
- `TRANSLATE` - 推文翻译
- `CA_CREATE` - CA 代币创建

---

## 数据结构

### Twitter 用户

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

### 推文

```json
{
  "id": "1234567890",
  "text": "推文内容...",
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
<summary><b>其他客户端手动安装</b>（点击展开）</summary>

> 以下所有配置中 `/path/to/twitter-mcp` 需替换为你本地的实际项目路径，`<your-token>` 替换为你从 [https://6551.io/mcp](https://6551.io/mcp) 申请的 Token。

### Claude Desktop

编辑配置文件（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`，Windows: `%APPDATA%\Claude\claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "TWITTER_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json` 或 Settings > MCP Servers：

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "TWITTER_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Windsurf

`~/.codeium/windsurf/mcp_config.json`：

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "TWITTER_TOKEN": "<your-token>"
      }
    }
  }
}
```

### Cline

VS Code 侧栏 > Cline > MCP Servers > Configure，编辑 `cline_mcp_settings.json`：

```json
{
  "mcpServers": {
    "twitter": {
      "command": "uv",
      "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
      "env": {
        "TWITTER_TOKEN": "<your-token>"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

### Continue.dev

`~/.continue/config.yaml`：

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
      TWITTER_TOKEN: <your-token>
```

### Cherry Studio

设置 > MCP 服务器 > 添加 > 类型 stdio：Command `uv`，Args `--directory /path/to/twitter-mcp run twitter-mcp`，Env `TWITTER_TOKEN`。

### Zed Editor

`~/.config/zed/settings.json`：

```json
{
  "context_servers": {
    "twitter": {
      "command": {
        "path": "uv",
        "args": ["--directory", "/path/to/twitter-mcp", "run", "twitter-mcp"],
        "env": {
          "TWITTER_TOKEN": "<your-token>"
        }
      }
    }
  }
}
```

### 任意 stdio MCP 客户端

```bash
TWITTER_TOKEN=<your-token> \
  uv --directory /path/to/twitter-mcp run twitter-mcp
```

</details>

---

## 兼容性

| 客户端 | 安装方式 | 状态 |
|--------|----------|------|
| **Claude Code** | `claude mcp add` | 一键安装 |
| **OpenClaw** | 复制 Skill 目录 | 一键安装 |
| Claude Desktop | JSON 配置 | 支持 |
| Cursor | JSON 配置 | 支持 |
| Windsurf | JSON 配置 | 支持 |
| Cline | JSON 配置 | 支持 |
| Continue.dev | YAML / JSON | 支持 |
| Cherry Studio | GUI | 支持 |
| Zed | JSON 配置 | 支持 |

---

## 开发

```bash
cd /path/to/twitter-mcp
uv sync
uv run twitter-mcp
```

```bash
# MCP Inspector 测试
npx @modelcontextprotocol/inspector uv --directory /path/to/twitter-mcp run twitter-mcp
```

### 项目结构

```
├── README.md                  # English
├── docs/
│   ├── README_ZH.md           # 中文
│   ├── README_JA.md           # 日本語
│   └── README_KO.md           # 한국어
├── openclaw-skill/opentwitter/    # OpenClaw Skill
├── pyproject.toml
├── config.json
└── src/twitter_mcp/
    ├── server.py              # 入口
    ├── app.py                 # FastMCP 实例
    ├── config.py              # 配置加载
    ├── api_client.py          # HTTP 客户端
    └── tools.py               # 8 个工具
```

## 许可证

MIT
