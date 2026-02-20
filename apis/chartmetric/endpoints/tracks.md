# Tracks

## GET `/track/:id` - Metadata

Comprehensive track metadata with cross-platform IDs and statistics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric track ID |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Chartmetric track ID |
| name | String | Track name |
| isrc | String | International Standard Recording Code |
| image_url | String | Cover art URL |
| cm_track | Integer | Chartmetric track ID |
| cm_artist | Array | Chartmetric artist IDs |
| artist_names | Array | Artist name strings |
| code2s | Array | Country codes |
| spotify_track_ids | Array | Spotify track IDs |
| spotify_album_ids | Array | Spotify album IDs |
| spotify_duration_ms | Integer | Duration in milliseconds |
| spotify_popularity | Integer | Spotify popularity (0-100) |
| itunes_track_ids | Array | iTunes track IDs |
| deezer_track_ids | Array | Deezer track IDs |
| amazon_track_ids | Array | Amazon track IDs |
| album_ids | Array | Chartmetric album IDs |
| album_names | Array | Album name strings |
| album_upc | Array | Album UPC codes |
| album_label | Array | Record labels |
| release_dates | Array | Release dates |
| tags | Array | Genre tags |
| cm_statistics | Object | Aggregate stats (see below) |

**`cm_statistics` fields:** `num_sp_playlists`, `num_sp_editorial_playlists`, `sp_playlist_total_reach`, `sp_editorial_playlist_total_reach`, `num_tiktok_videos`, `shazam_plays`, `youtube_views`, and more

---

## GET `/track/:id/:platform/stats` - Platform Stats

Time-series statistics for a track on a specific platform.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric track ID |
| platform | String | yes | Platform name |
| since | String | no | Start date (ISO) |
| until | String | no | End date (ISO), default: today |

**Response:** Array of `{ value, timestp }` objects

---

## GET `/track/:id/:type/charts` - Chart Positions

Chart performance data for the track.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric track ID |
| type | String | yes | Chart type |
| since | String | no | Start date (default: 180 days ago) |
| until | String | no | End date (default: today) |

---

## GET `/track/:id/:platform/:status/playlists` - Playlists

Playlists currently or previously containing the track.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric track ID |
| platform | String | yes | `spotify`, `applemusic`, `deezer`, `amazon`, `youtube` |
| status | String | yes | `current` or `past` |
| since | String | no | Start date |
| until | String | no | End date |
| limit | Integer | no | Results per page (default: 10) |
| offset | Integer | no | Pagination offset |
| indie | Boolean | no | Filter by indie curation |

---

## GET `/track/:id/:platform/playlists/snapshot` - Playlist Snapshot

Snapshot of all playlists containing the track on a specific date.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric track ID |
| platform | String | yes | Platform name |
| date | String | no | Snapshot date (ISO) |
| limit | Integer | no | Results per page |
| offset | Integer | no | Pagination offset |

---

## GET `/track/:id/tunefind` - Sync Placements

TV/movie sync placement data from Tunefind.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric track ID |

---

## GET `/track/:type/:id/get-ids` - Cross-Platform IDs

Look up all platform IDs from one known ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | String | yes | ID type: `chartmetric`, `isrc`, `spotify`, `itunes`, `deezer`, `amazon` |
| id | String | yes | The known ID value |

**Response:** `cm_track`, `track_name`, `isrc`, `spotify_track_id`, `itunes_track_id`, `deezer_track_id`, `amazon_track_id`
