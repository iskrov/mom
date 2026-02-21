# Reposts

All endpoints require authentication via `Authorization: OAuth ACCESS_TOKEN` header.

## POST `/reposts/tracks/:track_id` - Repost Track

Repost a track to the authenticated user's stream.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID to repost |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 201 | Successfully reposted |
| 401 | Unauthorized |
| 404 | Track not found |

---

## DELETE `/reposts/tracks/:track_id` - Remove Track Repost

Remove a track repost from the authenticated user's stream.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID to un-repost |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Successfully removed repost |
| 401 | Unauthorized |
| 404 | Track not found or not reposted |

---

## POST `/reposts/playlists/:playlist_id` - Repost Playlist

Repost a playlist to the authenticated user's stream.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID to repost |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 201 | Successfully reposted |
| 401 | Unauthorized |
| 404 | Playlist not found |

---

## DELETE `/reposts/playlists/:playlist_id` - Remove Playlist Repost

Remove a playlist repost from the authenticated user's stream.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID to un-repost |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Successfully removed repost |
| 401 | Unauthorized |
| 404 | Playlist not found or not reposted |
