# Search & Resolve

## GET `/tracks` - Search Tracks

Search tracks by keyword with optional filters. See [tracks.md](tracks.md) for the full endpoint documentation including all filter parameters (genres, BPM, duration, created_at, etc.).

**Key Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| q | query | String | yes | Search keyword (searches title, username, description) |
| genres | query | String | no | Comma-separated genres (e.g., `Pop,House`) |
| tags | query | String | no | Comma-separated tags |
| bpm[from] | query | Integer | no | Minimum BPM |
| bpm[to] | query | Integer | no | Maximum BPM |
| duration[from] | query | Integer | no | Minimum duration (ms) |
| duration[to] | query | Integer | no | Maximum duration (ms) |
| created_at[from] | query | String | no | Created after (ISO 8601) |
| created_at[to] | query | String | no | Created before (ISO 8601) |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| ids | query | String | no | Comma-separated track IDs |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

---

## GET `/users` - Search Users

Search users by keyword. See [users.md](users.md) for the full endpoint documentation.

**Key Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| q | query | String | yes | Search keyword (searches username, description) |
| ids | query | String | no | Comma-separated user IDs |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated User collection

---

## GET `/playlists` - Search Playlists

Search playlists by keyword. See [playlists.md](playlists.md) for the full endpoint documentation.

**Key Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| q | query | String | yes | Search keyword |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Playlist collection

---

## GET `/resolve` - Resolve URL

Convert a SoundCloud permalink URL (e.g., `https://soundcloud.com/username/track-name`) to its full API resource representation.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| url | query | String | yes | SoundCloud permalink URL to resolve |

**Response:** HTTP 302 redirect to the API resource URL. The redirect target returns the full resource object (Track, User, or Playlist depending on the URL).

**Status Codes:**

| Code | Description |
|------|-------------|
| 302 | Found - redirects to API resource URL |
| 404 | URL not found or invalid |

**Usage:**

```bash
# Resolve a track URL
curl -L -H "Authorization: OAuth ACCESS_TOKEN" \
  "https://api.soundcloud.com/resolve?url=https://soundcloud.com/artist/track-name"

# Resolve a user URL
curl -L -H "Authorization: OAuth ACCESS_TOKEN" \
  "https://api.soundcloud.com/resolve?url=https://soundcloud.com/username"

# Resolve a playlist URL
curl -L -H "Authorization: OAuth ACCESS_TOKEN" \
  "https://api.soundcloud.com/resolve?url=https://soundcloud.com/username/sets/playlist-name"
```

**Notes:**
- Use the `-L` flag with curl to follow the 302 redirect automatically
- The resolved resource type depends on the URL path structure
- Returns the full resource object with all fields (same as calling the specific resource endpoint directly)
- Works with track URLs, user profile URLs, and playlist/set URLs
