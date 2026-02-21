# SoundCloud API

Audio distribution platform with 300M+ tracks, enabling upload, streaming, social interaction, and discovery.

- **Base URL:** `https://api.soundcloud.com`
- **Auth URL:** `https://secure.soundcloud.com`
- **Docs:** https://developers.soundcloud.com/docs
- **API Spec:** https://developers.soundcloud.com/docs/api/explorer/open-api
- **Format:** JSON responses, form-encoded or JSON requests
- **CORS:** Enabled for browser-based JavaScript; JSONP supported via `callback` parameter

## Authentication

OAuth 2.1 with PKCE mandatory. Two flows:

1. **Authorization Code Flow** - user-delegated access (uploads, likes, follows, private content)
2. **Client Credentials Flow** - app-only access (search, playback, public data)

Both return access tokens (~1 hour expiry) and refresh tokens.

```bash
# Client Credentials: get access token
curl -X POST https://secure.soundcloud.com/oauth/token \
  -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
  -d "grant_type=client_credentials"

# Use access token on all requests
curl -H "Authorization: OAuth ACCESS_TOKEN" \
  -H "accept: application/json; charset=utf-8" \
  https://api.soundcloud.com/me
```

**Client Credentials rate limit:** 50 tokens per 12h per app, 30 tokens per 1h per IP.

## Security Schemes

| Scheme | Type | Location | Description |
|--------|------|----------|-------------|
| ClientId | API Key | Query `client_id` | Application client ID |
| AuthHeader | API Key | Header `Authorization` | Format: `OAuth ACCESS_TOKEN` |

## Rate Limits

- **No global aggregate limit** on total API calls per application
- **Play requests:** 15,000 per 24-hour rolling window for `/tracks/:id/stream` endpoints
- Time windows calculated per application `client_id`
- Exceeding limits returns HTTP 429 with JSON body:

```json
{
  "rate_limit": {
    "group": "plays",
    "max_nr_of_requests": 15000,
    "time_window": "PT24H",
    "remaining_requests": 0,
    "reset_time": "2025/01/15 12:00:00 +0000"
  }
}
```

## Track Access Levels

| Level | Description |
|-------|-------------|
| `playable` | Fully streamable |
| `preview` | Preview snippet only |
| `blocked` | Metadata only, no streaming |

## Pagination

- Default: 50 items per page, maximum: 200
- Use `linked_partitioning=true` to enable cursor-based pagination
- Response includes `next_href` for next page (follow the URL directly)
- `offset` parameter is deprecated in favor of cursor-based pagination

## Supported Audio Formats (Upload)

AIFF, WAVE, FLAC, OGG, MP2, MP3, AAC, AMR, WMA (max 500MB per upload)

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 302 | Found (redirect, used by `/resolve`) |
| 400 | Bad Request - malformed request |
| 401 | Unauthorized - expired/missing token |
| 403 | Forbidden - insufficient permissions |
| 404 | Not Found |
| 406 | Not Acceptable - check Accept header |
| 422 | Unprocessable Entity - invalid parameter format |
| 429 | Too Many Requests - rate limited |
| 500 | Internal Server Error |
| 503 | Service Unavailable |
| 504 | Gateway Timeout |

## Error Response Format

```json
{
  "code": 404,
  "message": "404 - Not Found",
  "errors": [{"error_message": "..."}]
}
```

## Endpoint Categories

| Category | Endpoints | Description |
|----------|-----------|-------------|
| [Authentication](endpoints/authentication.md) | 3 | OAuth flows, token management, sign-out |
| [Me (Current User)](endpoints/me.md) | 19 | Authenticated user profile, activities, social |
| [Tracks](endpoints/tracks.md) | 10 | Track CRUD, streaming, comments, related |
| [Playlists](endpoints/playlists.md) | 7 | Playlist CRUD, tracks, reposters |
| [Users](endpoints/users.md) | 11 | User profiles, tracks, social, web profiles |
| [Likes](endpoints/likes.md) | 4 | Like/unlike tracks and playlists |
| [Reposts](endpoints/reposts.md) | 4 | Repost/unrepost tracks and playlists |
| [Search & Resolve](endpoints/search.md) | 4 | Search tracks/users/playlists, resolve URLs |

**Total: ~62 endpoints**

See [quick-reference.md](quick-reference.md) for a compact endpoint table.
