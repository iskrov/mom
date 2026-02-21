# Likes

All endpoints require authentication via `Authorization: OAuth ACCESS_TOKEN` header.

## POST `/likes/tracks/:track_id` - Like Track

Like (favorite) a track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID to like |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success (already liked) |
| 201 | Successfully liked |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Track not found |
| 429 | Too Many Requests |

---

## DELETE `/likes/tracks/:track_id` - Unlike Track

Remove a like from a track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID to unlike |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Successfully unliked |
| 400 | Bad Request |
| 404 | Track not found or not liked |

---

## POST `/likes/playlists/:playlist_id` - Like Playlist

Like (favorite) a playlist.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID to like |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success (already liked) |
| 201 | Successfully liked |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Playlist not found |
| 429 | Too Many Requests |

---

## DELETE `/likes/playlists/:playlist_id` - Unlike Playlist

Remove a like from a playlist.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID to unlike |

**Response:** Empty body on success

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Successfully unliked |
| 400 | Bad Request |
| 404 | Playlist not found or not liked |
