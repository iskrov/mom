# Playlists

## GET `/playlist/:platform/:id` - Metadata

Playlist metadata for a specific streaming platform.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer` |
| id | String/Integer | yes | Chartmetric playlist ID |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Chartmetric playlist ID |
| name | String | Playlist name |
| description | String | Playlist description |
| image_url | String | Cover image |
| owner_name | String | Curator/owner name |
| owner_id | String | Platform owner ID |
| followers | Integer | Follower count |
| num_track | Integer | Number of tracks |
| editorial | Boolean | Platform editorial playlist |
| personalized | Boolean | Algorithmically personalized |
| code2 | String | Country code |
| tags | Array | Playlist tags `{ id, name }` |
| last_updated | String | Last modification date |
| fdiff_week | Integer | Weekly follower change |
| fdiff_month | Integer | Monthly follower change |
| active_ratio | Float | Activity metric |

---

## GET `/playlist/:platform/lists` - Browse Playlists

Browse and filter playlists by platform.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer`, `amazon` |
| sort | String | no | Sort column (default: `followers`) |
| country | String | no | Country code (default: `US`) |
| limit | Integer | no | Results per page (max: 100, default: 100) |
| offset | Integer | no | Pagination offset (default: 0) |
| indie | Boolean | no | Filter indie playlists (default: false) |

---

## GET `/playlist/:platform/:id/snapshot` - Track Snapshot

Snapshot of all tracks in the playlist at a specific date.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer`, `amazon` |
| id | String/Integer | yes | Chartmetric playlist ID |
| date | String | no | Snapshot date (ISO format YYYY-MM-DD) |

---

## GET `/playlist/:platform/:id/:span/tracks` - Current/Past Tracks

Tracks currently in or previously removed from the playlist.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer`, `amazon` |
| id | String/Integer | yes | Chartmetric playlist ID |
| span | String | yes | `current` or `past` |

---

## GET `/playlist/:platform/:id/similarplaylists` - Similar Playlists

Find playlists similar to the given one.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer` |
| id | String/Integer | yes | Chartmetric playlist ID |
| storefront | String | conditional | Required for Apple Music |
| indie | Boolean | no | Filter indie playlists (Spotify only) |
| limit | Integer | no | Results (default: 9, max: 100) |
