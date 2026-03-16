<p align="center">
  <b>Twitter MCP Server</b><br>
  Twitter/X データ · ユーザープロフィール · ツイート検索 · フォロワーイベント · KOL トラッキング
</p>

<p align="center">
  <a href="../README.md">English</a> | <a href="./README_ZH.md">中文</a> | <a href="./README_KO.md">한국어</a>
</p>

---

## クイックインストール

> **まず [https://6551.io/mcp](https://6551.io/mcp) で API Token を取得してください。**

### Claude Code

```bash
claude mcp add twitter \
  -e TWITTER_TOKEN=<your-token> \
  -- uv --directory /path/to/twitter-mcp run twitter-mcp
```

> `/path/to/twitter-mcp` をローカルのプロジェクトパスに、`<your-token>` を Token に置き換えてください。

### OpenClaw

```bash
export TWITTER_TOKEN="<your-token>"
cp -r openclaw-skill/opentwitter ~/.openclaw/skills/
```

---

## AI にレビュー＆インストールしてもらう

この MCP が安全かどうか不安ですか？以下のプロンプトを AI アシスタントに送信すれば、ソースコードをレビューしてからインストールしてくれます：

> **以下のプロンプトをコピーして AI アシスタントに送信してください（`<プロジェクトパス>` と `<your-token>` を実際の値に置き換え）：**

```text
twitter-mcp という MCP サーバーをレビューしてインストールしてください。プロジェクトはローカルの <プロジェクトパス> にあります。

手順：
1. 以下のファイルのセキュリティを確認：
   - src/twitter_mcp/api_client.py — ai.6551.io のみに接続し、他のアドレスにデータを送信していないことを確認
   - src/twitter_mcp/config.py — トークンがローカルの config.json または環境変数からのみ読み取られ、ハードコードや漏洩がないことを確認
   - src/twitter_mcp/tools.py — すべてのツールが API クエリのみを実行し、ファイル書き込み、コマンド実行、その他の危険な操作がないことを確認
   - pyproject.toml — 依存関係が mcp、httpx のみで、不審なパッケージがないことを確認
2. レビュー結論を教えてください：安全 / リスクあり / 問題あり、具体的な理由とともに
3. 安全であれば、インストールを実行（Token は https://6551.io/mcp から取得）：
   claude mcp add twitter -e TWITTER_TOKEN=<your-token> -- uv --directory <プロジェクトパス> run twitter-mcp
```

---

## 何ができる？

接続後、AI アシスタントに話しかけるだけ：

| あなたが言う | 実行される操作 |
|-------------|---------------|
| 「@elonmusk の Twitter プロフィールを見せて」 | ユーザープロフィール取得 |
| 「@VitalikButerin は最近何をツイートした？」 | ユーザーの最新ツイート取得 |
| 「Bitcoin 関連のツイートを検索」 | キーワード検索 |
| 「#crypto ハッシュタグのツイートを探して」 | ハッシュタグ検索 |
| 「ETH について 1000 いいね以上の人気ツイート」 | エンゲージメントフィルター検索 |
| 「最近 @elonmusk をフォローしたのは誰？」 | 新規フォロワーイベント取得 |
| 「@elonmusk をフォロー解除したのは誰？」 | フォロー解除イベント取得 |
| 「@elonmusk が削除したツイートは？」 | 削除ツイート取得 |
| 「どの KOL が @elonmusk をフォローしている？」 | KOL フォロワー取得 |

---

## 利用可能なツール

| ツール | 説明 |
|--------|------|
| `get_twitter_user` | ユーザー名でプロフィール取得 |
| `get_twitter_user_by_id` | ID でプロフィール取得 |
| `get_twitter_user_tweets` | ユーザーの最新ツイート取得 |
| `search_twitter` | 基本フィルターでツイート検索 |
| `search_twitter_advanced` | 複数フィルターで高度な検索 |
| `get_twitter_follower_events` | フォロー/フォロー解除イベント取得 |
| `get_twitter_deleted_tweets` | 削除ツイート取得 |
| `get_twitter_kol_followers` | KOL（キーオピニオンリーダー）フォロワー取得 |
| `get_twitter_article_by_id` | ID で Twitter 記事取得 |
| `get_twitter_tweet_by_id` | ID でツイート取得（ネストされた返信/引用を含む） |
| `get_twitter_watch` | 監視中の Twitter ユーザー一覧取得 |
| `add_twitter_watch` | Twitter ユーザーを監視リストに追加 |
| `delete_twitter_watch` | 監視リストから Twitter ユーザーを削除 |

---

## 設定

### API Token を取得

[https://6551.io/mcp](https://6551.io/mcp) で API Token を取得してください。

環境変数を設定：

```bash
# macOS / Linux
export TWITTER_TOKEN="<your-token>"

# Windows PowerShell
$env:TWITTER_TOKEN = "<your-token>"
```

| 変数 | 必須 | 説明 |
|------|------|------|
| `TWITTER_TOKEN` | **はい** | 6551 API Bearer トークン（https://6551.io/mcp から取得） |
| `TWITTER_API_BASE` | いいえ | REST API URL のオーバーライド |
| `TWITTER_MAX_ROWS` | いいえ | クエリあたりの最大結果数（デフォルト: 100） |

プロジェクトルートの `config.json` もサポート（環境変数が優先）：

```json
{
  "api_base_url": "https://ai.6551.io",
  "api_token": "<your-token>",
  "max_rows": 100
}
```

---

## WebSocket リアルタイム購読

**エンドポイント**: `wss://ai.6551.io/open/twitter_wss?token=YOUR_TOKEN`

監視している Twitter アカウントのリアルタイムイベントを購読します。

### Twitter イベントを購読

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "twitter.subscribe"
}
```

**レスポンス**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true
  }
}
```

### 購読解除

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "twitter.unsubscribe"
}
```

### サーバープッシュ - Twitter イベント

監視しているアカウントにアクティビティがあると、サーバーがプッシュします：

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
    "remark": "カスタムメモ",
    "createdAt": "2026-03-06T10:00:00Z"
  }
}
```

**注意**：`content` フィールドの構造はイベントタイプにより異なります（以下参照）。
```

**イベントタイプとコンテンツ構造**:

#### ツイートイベント
- `NEW_TWEET` - 新しいツイート投稿
- `NEW_TWEET_REPLY` - 返信ツイート投稿
- `NEW_TWEET_QUOTE` - 引用ツイート投稿
- `NEW_RETWEET` - リツイート
- `CA` - CA アドレス付きツイート

ツイートイベントの content 構造：
```json
{
  "id": "1234567890",
  "text": "ツイート内容...",
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

#### フォロワーイベント
- `NEW_FOLLOWER` - 新しいフォロワー
- `NEW_UNFOLLOWER` - フォロー解除

フォロワーイベントの content 構造（配列）：
```json
[
  {
    "id": 123,
    "twId": 44196397,
    "twAccount": "elonmusk",
    "twUserName": "Elon Musk",
    "twUserLabel": "Verified",
    "description": "ユーザー紹介...",
    "profileUrl": "https://...",
    "bannerUrl": "https://...",
    "followerCount": 170000000,
    "friendCount": 500,
    "createdAt": "2026-03-06T10:00:00Z"
  }
]
```

#### プロフィール更新イベント
- `UPDATE_NAME` - ユーザー名変更（content: 新しい名前の文字列）
- `UPDATE_DESCRIPTION` - 紹介文更新（content: 新しい紹介文の文字列）
- `UPDATE_AVATAR` - プロフィール画像変更（content: 新しいアバター URL 文字列）
- `UPDATE_BANNER` - バナー画像変更（content: 新しいバナー URL 文字列）

#### その他のイベント
- `TWEET_TOPPING` - ツイート固定
- `DELETE` - ツイート削除
- `SYSTEM` - システムイベント
- `TRANSLATE` - ツイート翻訳
- `CA_CREATE` - CA トークン作成

---

## データ構造

### Twitter ユーザー

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

### ツイート

```json
{
  "id": "1234567890",
  "text": "ツイート内容...",
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
<summary><b>その他のクライアント — 手動インストール</b>（クリックで展開）</summary>

> 以下のすべての設定で `/path/to/twitter-mcp` をローカルの実際のプロジェクトパスに、`<your-token>` を [https://6551.io/mcp](https://6551.io/mcp) から取得した Token に置き換えてください。

### Claude Desktop

設定ファイルを編集（macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`、Windows: `%APPDATA%\Claude\claude_desktop_config.json`）：

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

`~/.cursor/mcp.json` または Settings > MCP Servers：

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

VS Code サイドバー > Cline > MCP Servers > Configure、`cline_mcp_settings.json` を編集：

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

設定 > MCP サーバー > 追加 > タイプ stdio：Command `uv`、Args `--directory /path/to/twitter-mcp run twitter-mcp`、Env `TWITTER_TOKEN`。

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

### 任意の stdio MCP クライアント

```bash
TWITTER_TOKEN=<your-token> \
  uv --directory /path/to/twitter-mcp run twitter-mcp
```

</details>

---

## 互換性

| クライアント | インストール方法 | ステータス |
|-------------|-----------------|-----------|
| **Claude Code** | `claude mcp add` | ワンライナー |
| **OpenClaw** | Skill ディレクトリコピー | ワンライナー |
| Claude Desktop | JSON 設定 | 対応 |
| Cursor | JSON 設定 | 対応 |
| Windsurf | JSON 設定 | 対応 |
| Cline | JSON 設定 | 対応 |
| Continue.dev | YAML / JSON | 対応 |
| Cherry Studio | GUI | 対応 |
| Zed | JSON 設定 | 対応 |

---

## 開発

```bash
cd /path/to/twitter-mcp
uv sync
uv run twitter-mcp
```

```bash
# MCP Inspector
npx @modelcontextprotocol/inspector uv --directory /path/to/twitter-mcp run twitter-mcp
```

### プロジェクト構造

```
├── README.md                  # English
├── docs/
│   ├── README_JA.md           # 日本語
│   └── README_KO.md           # 한국어
├── openclaw-skill/opentwitter/    # OpenClaw Skill
├── pyproject.toml
├── config.json
└── src/twitter_mcp/
    ├── server.py              # エントリポイント
    ├── app.py                 # FastMCP インスタンス
    ├── config.py              # 設定ローダー
    ├── api_client.py          # HTTP クライアント
    └── tools.py               # 8 ツール
```

## ライセンス

MIT
