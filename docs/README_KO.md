<p align="center">
  <b>Twitter MCP Server</b><br>
  Twitter/X 데이터 · 사용자 프로필 · 트윗 검색 · 팔로워 이벤트 · KOL 트래킹
</p>

<p align="center">
  <a href="../README.md">English</a> | <a href="./README_ZH.md">中文</a> | <a href="./README_JA.md">日本語</a>
</p>

---

## 빠른 설치

> **먼저 [https://6551.io/mcp](https://6551.io/mcp)에서 API Token을 받으세요.**

### Claude Code

```bash
claude mcp add twitter \
  -e TWITTER_TOKEN=<your-token> \
  -- uv --directory /path/to/twitter-mcp run twitter-mcp
```

> `/path/to/twitter-mcp`를 로컬 프로젝트 경로로, `<your-token>`을 Token으로 교체하세요.

### OpenClaw

```bash
export TWITTER_TOKEN="<your-token>"
cp -r openclaw-skill/opentwitter ~/.openclaw/skills/
```

---

## AI에게 검토 및 설치 맡기기

이 MCP가 안전한지 확신이 없으신가요? 아래 프롬프트를 AI 어시스턴트에게 보내면 소스 코드를 먼저 검토한 후 설치해줍니다:

> **아래 프롬프트를 복사하여 AI 어시스턴트에게 보내세요 (`<프로젝트경로>`와 `<your-token>`을 실제 값으로 교체):**

```text
twitter-mcp MCP 서버를 검토하고 설치해주세요. 프로젝트는 로컬 <프로젝트경로>에 있습니다.

단계:
1. 다음 파일의 보안을 확인:
   - src/twitter_mcp/api_client.py — ai.6551.io에만 연결하고 다른 주소로 데이터를 보내지 않는지 확인
   - src/twitter_mcp/config.py — 토큰이 로컬 config.json 또는 환경 변수에서만 읽히며, 하드코딩이나 유출이 없는지 확인
   - src/twitter_mcp/tools.py — 모든 도구가 API 쿼리만 수행하고, 파일 쓰기, 명령 실행 또는 기타 위험한 작업이 없는지 확인
   - pyproject.toml — 의존성이 mcp, httpx만 있고, 의심스러운 패키지가 없는지 확인
2. 검토 결론을 알려주세요: 안전 / 위험 / 문제 있음, 구체적인 이유와 함께
3. 안전하다면 설치 실행 (Token은 https://6551.io/mcp에서 취득):
   claude mcp add twitter -e TWITTER_TOKEN=<your-token> -- uv --directory <프로젝트경로> run twitter-mcp
```

---

## 무엇을 할 수 있나요?

연결 후 AI 어시스턴트에게 말하기만 하면 됩니다:

| 당신이 말하면 | 실행되는 작업 |
|-------------|-------------|
| "@elonmusk의 Twitter 프로필 보여줘" | 사용자 프로필 조회 |
| "@VitalikButerin이 최근에 뭘 트윗했어?" | 사용자 최신 트윗 조회 |
| "Bitcoin 관련 트윗 검색" | 키워드 검색 |
| "#crypto 해시태그 트윗 찾아줘" | 해시태그 검색 |
| "ETH에 대해 1000 좋아요 이상인 인기 트윗" | 참여도 필터 검색 |
| "최근 @elonmusk을 팔로우한 사람은?" | 새 팔로워 이벤트 조회 |
| "@elonmusk을 언팔로우한 사람은?" | 언팔로우 이벤트 조회 |
| "@elonmusk이 삭제한 트윗은?" | 삭제된 트윗 조회 |
| "어떤 KOL이 @elonmusk을 팔로우해?" | KOL 팔로워 조회 |

---

## 사용 가능한 도구

| 도구 | 설명 |
|------|------|
| `get_twitter_user` | 사용자명으로 프로필 조회 |
| `get_twitter_user_by_id` | ID로 프로필 조회 |
| `get_twitter_user_tweets` | 사용자 최신 트윗 조회 |
| `search_twitter` | 기본 필터로 트윗 검색 |
| `search_twitter_advanced` | 다중 필터로 고급 검색 |
| `get_twitter_follower_events` | 팔로우/언팔로우 이벤트 조회 |
| `get_twitter_deleted_tweets` | 삭제된 트윗 조회 |
| `get_twitter_kol_followers` | KOL(키 오피니언 리더) 팔로워 조회 |
| `get_twitter_article_by_id` | ID로 Twitter 기사 조회 |
| `get_twitter_tweet_by_id` | ID로 트윗 조회 (중첩된 답글/인용 포함) |
| `get_twitter_watch` | 모니터링 중인 Twitter 사용자 목록 조회 |
| `add_twitter_watch` | Twitter 사용자를 모니터링 목록에 추가 |
| `delete_twitter_watch` | 모니터링 목록에서 Twitter 사용자 삭제 |

---

## 설정

### API Token 받기

[https://6551.io/mcp](https://6551.io/mcp)에서 API Token을 받으세요.

환경 변수 설정:

```bash
# macOS / Linux
export TWITTER_TOKEN="<your-token>"

# Windows PowerShell
$env:TWITTER_TOKEN = "<your-token>"
```

| 변수 | 필수 | 설명 |
|------|------|------|
| `TWITTER_TOKEN` | **예** | 6551 API Bearer 토큰 (https://6551.io/mcp에서 취득) |
| `TWITTER_API_BASE` | 아니오 | REST API URL 재정의 |
| `TWITTER_MAX_ROWS` | 아니오 | 쿼리당 최대 결과 수 (기본: 100) |

프로젝트 루트의 `config.json`도 지원 (환경 변수 우선):

```json
{
  "api_base_url": "https://ai.6551.io",
  "api_token": "<your-token>",
  "max_rows": 100
}
```

---

## WebSocket 실시간 구독

**엔드포인트**: `wss://ai.6551.io/open/twitter_wss?token=YOUR_TOKEN`

모니터링 중인 Twitter 계정의 실시간 이벤트를 구독합니다.

### Twitter 이벤트 구독

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "twitter.subscribe"
}
```

**응답**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "success": true
  }
}
```

### 구독 취소

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "twitter.unsubscribe"
}
```

### 서버 푸시 - Twitter 이벤트

모니터링 중인 계정에 활동이 있으면 서버가 푸시합니다:

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
    "remark": "사용자 지정 메모",
    "createdAt": "2026-03-06T10:00:00Z"
  }
}
```

**참고**：`content` 필드의 구조는 이벤트 유형에 따라 다릅니다（아래 참조）。
```

**이벤트 유형 및 콘텐츠 구조**:

#### 트윗 이벤트
- `NEW_TWEET` - 새 트윗 게시
- `NEW_TWEET_REPLY` - 답글 트윗 게시
- `NEW_TWEET_QUOTE` - 인용 트윗 게시
- `NEW_RETWEET` - 리트윗
- `CA` - CA 주소가 포함된 트윗

트윗 이벤트의 content 구조：
```json
{
  "id": "1234567890",
  "text": "트윗 내용...",
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

#### 팔로워 이벤트
- `NEW_FOLLOWER` - 새 팔로워
- `NEW_UNFOLLOWER` - 언팔로우

팔로워 이벤트의 content 구조（배열）：
```json
[
  {
    "id": 123,
    "twId": 44196397,
    "twAccount": "elonmusk",
    "twUserName": "Elon Musk",
    "twUserLabel": "Verified",
    "description": "사용자 소개...",
    "profileUrl": "https://...",
    "bannerUrl": "https://...",
    "followerCount": 170000000,
    "friendCount": 500,
    "createdAt": "2026-03-06T10:00:00Z"
  }
]
```

#### 프로필 업데이트 이벤트
- `UPDATE_NAME` - 사용자명 변경（content: 새 이름 문자열）
- `UPDATE_DESCRIPTION` - 소개 업데이트（content: 새 소개 문자열）
- `UPDATE_AVATAR` - 프로필 사진 변경（content: 새 아바타 URL 문자열）
- `UPDATE_BANNER` - 배너 이미지 변경（content: 새 배너 URL 문자열）

#### 기타 이벤트
- `TWEET_TOPPING` - 트윗 고정
- `DELETE` - 트윗 삭제
- `SYSTEM` - 시스템 이벤트
- `TRANSLATE` - 트윗 번역
- `CA_CREATE` - CA 토큰 생성

---

## 데이터 구조

### Twitter 사용자

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

### 트윗

```json
{
  "id": "1234567890",
  "text": "트윗 내용...",
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
<summary><b>기타 클라이언트 — 수동 설치</b> (클릭하여 펼치기)</summary>

> 아래 모든 설정에서 `/path/to/twitter-mcp`를 로컬의 실제 프로젝트 경로로, `<your-token>`을 [https://6551.io/mcp](https://6551.io/mcp)에서 받은 Token으로 교체하세요.

### Claude Desktop

설정 파일 편집 (macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

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

`~/.cursor/mcp.json` 또는 Settings > MCP Servers:

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

`~/.codeium/windsurf/mcp_config.json`:

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

VS Code 사이드바 > Cline > MCP Servers > Configure, `cline_mcp_settings.json` 편집:

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
      TWITTER_TOKEN: <your-token>
```

### Cherry Studio

설정 > MCP 서버 > 추가 > 유형 stdio: Command `uv`, Args `--directory /path/to/twitter-mcp run twitter-mcp`, Env `TWITTER_TOKEN`.

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
          "TWITTER_TOKEN": "<your-token>"
        }
      }
    }
  }
}
```

### 기타 stdio MCP 클라이언트

```bash
TWITTER_TOKEN=<your-token> \
  uv --directory /path/to/twitter-mcp run twitter-mcp
```

</details>

---

## 호환성

| 클라이언트 | 설치 방법 | 상태 |
|-----------|----------|------|
| **Claude Code** | `claude mcp add` | 원라이너 |
| **OpenClaw** | Skill 디렉토리 복사 | 원라이너 |
| Claude Desktop | JSON 설정 | 지원 |
| Cursor | JSON 설정 | 지원 |
| Windsurf | JSON 설정 | 지원 |
| Cline | JSON 설정 | 지원 |
| Continue.dev | YAML / JSON | 지원 |
| Cherry Studio | GUI | 지원 |
| Zed | JSON 설정 | 지원 |

---

## 개발

```bash
cd /path/to/twitter-mcp
uv sync
uv run twitter-mcp
```

```bash
# MCP Inspector
npx @modelcontextprotocol/inspector uv --directory /path/to/twitter-mcp run twitter-mcp
```

### 프로젝트 구조

```
├── README.md                  # English
├── docs/
│   ├── README_JA.md           # 日本語
│   └── README_KO.md           # 한국어
├── openclaw-skill/opentwitter/    # OpenClaw Skill
├── pyproject.toml
├── config.json
└── src/twitter_mcp/
    ├── server.py              # 진입점
    ├── app.py                 # FastMCP 인스턴스
    ├── config.py              # 설정 로더
    ├── api_client.py          # HTTP 클라이언트
    └── tools.py               # 8개 도구
```

## 라이선스

MIT
