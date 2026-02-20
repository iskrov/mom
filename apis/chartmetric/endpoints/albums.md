# Albums

## GET `/album/:id` - Metadata

Album metadata with cross-platform IDs and statistics. Cached daily.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric album ID |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Chartmetric album ID |
| name | String | Album name |
| upc | String | Universal Product Code |
| image_url | String | Album artwork URL |
| release_date | String | Release date |
| label | String | Record label |
| cm_label | String | Chartmetric label name |
| description | String | Album description |
| num_track | Integer | Number of tracks |
| spotify_popularity | Integer | Spotify popularity (0-100) |
| spotify_album_ids | Array | Spotify album IDs |
| itunes_album_ids | Array | iTunes album IDs |
| deezer_album_ids | Array | Deezer album IDs |
| artists | Array | `{ cm_artist, name, image_url }` |
| cm_statistics | Object | `{ sp_popularity, num_sp_editorial_playlists, num_sp_playlists, sp_playlist_total_reach, sp_editorial_playlist_total_reach }` |

---

## GET `/album/:id/tracks` - Album Tracks

All tracks in the album with full metadata.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric album ID |

**Response:** Array of track objects (see [tracks.md](tracks.md) for field details)

---

## GET `/album/:id/:platform/:stat` - Stats

Time-series album stats for a specific platform metric.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric album ID |
| platform | String | yes | `spotify` |
| stat | String | yes | `followers` |
| since | String | no | Start date (ISO) |
| until | String | no | End date (ISO), default: today |
| latest | Boolean | no | Return only latest data point |

**Response:** Array of `{ value, timestp }` objects

---

## GET `/album/:id/:platform/:status/playlists` - Playlists

Playlists currently or previously featuring the album.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric album ID |
| platform | String | yes | `spotify`, `applemusic`, `deezer`, `amazon`, `youtube` |
| status | String | yes | `current` or `past` |
| since | String | no | Start date (default: 180 days ago) |
| until | String | no | End date (default: today) |
| limit | Integer | no | Results per page (default: 10) |
| offset | Integer | no | Pagination offset |

Plus all playlist type filters (see [artists.md](artists.md) playlists section for full filter list)

**Response:** Contains `playlist` object (id, name, followers, owner, position, editorial status, tags) and nested `track` object

---

## GET `/album/:id/:type/charts` - Chart Positions

Historical chart data for the album.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric album ID |
| type | String | yes | `applemusic`, `itunes`, `amazon` |
| since | String | no | Start date (default: 180 days ago) |
| until | String | no | End date (default: today, max 365 days range) |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| rank | Integer | Chart position |
| pre_rank | Integer | Previous position |
| peak_rank | Integer | Best position achieved |
| peak_date | String | Date of peak |
| code2 | String | Country code |
| genre | String | Chart genre |
| added_at | String | Date recorded |
| name | String | Album name |
| release_date | String | Release date |
| label | String | Record label |
| is_single | Boolean | Single indicator |
| artists | Array | `{ itunes_artist_id, name, cm_artist }` |

---

## GET `/album/:type/:id/get-ids` - Cross-Platform IDs

Look up all platform IDs from one known ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | String | yes | ID type: `chartmetric`, `upc`, `spotify`, `itunes`, `deezer`, `amazon` |
| id | String | yes | The known ID value |

**Response:** `cm_album`, `album_name`, `upc`, `spotify_album_id`, `itunes_album_id`, `deezer_album_id`, `amazon_album_id`
