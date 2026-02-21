# Playlists

## GET `/playlists` - Search Playlists

Search and filter playlists.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| q | query | String | yes | Search keyword |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0, deprecated) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Playlist collection

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | Array of Playlist objects |
| next_href | String | URL for next page of results |

**Playlist Object:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Playlist ID |
| title | String | Playlist title |
| description | String | Playlist description |
| kind | String | Resource type (`playlist`) |
| uri | String | API resource URI |
| permalink | String | URL slug |
| permalink_url | String | Full playlist URL on SoundCloud |
| artwork_url | String | Cover art URL |
| tracks_uri | String | API URI for playlist tracks |
| user | MetaUser | Playlist creator |
| user_id | Integer | Creator user ID |
| track_count | Integer | Number of tracks |
| duration | Integer | Total duration in milliseconds |
| created_at | DateTime | Creation timestamp |
| last_modified | DateTime | Last modification timestamp |
| sharing | String | `public` or `private` |
| license | String | License type |
| streamable | Boolean | Whether playlist is streamable |
| downloadable | Boolean | Whether playlist is downloadable |
| tag_list | String | Space-separated tags |
| tags | String | Tags |
| genre | String | Genre |
| playlist_type | String | Playlist type |
| type | String | Type classifier |
| likes_count | Integer | Number of likes |
| embeddable_by | String | Who can embed: `all`, `me`, `none` |
| purchase_url | String | External purchase URL |
| purchase_title | String | Purchase link text |
| release | String | Release identifier |
| release_day | Integer | Release day |
| release_month | Integer | Release month |
| release_year | Integer | Release year |
| ean | String | EAN barcode |
| label_id | Integer | Label user ID |
| label_name | String | Label name |
| label | MetaUser | Label as user object |
| tracks | Array | Array of Track objects (when included) |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |

---

## POST `/playlists` - Create Playlist

Create a new playlist.

**Request Body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| playlist.title | String | yes | Playlist title |
| playlist.description | String | no | Playlist description |
| playlist.sharing | String | no | `public` (default) or `private` |
| playlist.tracks | Array | no | Array of objects with `id` property (track IDs) |

**Example Request Body:**

```json
{
  "playlist": {
    "title": "My Playlist",
    "description": "A collection of tracks",
    "sharing": "public",
    "tracks": [
      {"id": 12345},
      {"id": 67890}
    ]
  }
}
```

**Response:** Playlist object

**Status Codes:**

| Code | Description |
|------|-------------|
| 201 | Playlist created |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/playlists/:playlist_id` - Playlist Details

Get metadata for a specific playlist.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID |
| secret_token | query | String | no | Secret token for private playlists |
| access | query | Array | no | Filter tracks: `playable`, `preview`, `blocked` |
| show_tracks | query | Boolean | no | Include tracks in response (default: `true`; set `false` for faster response) |

**Response:** Playlist object (full schema above)

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |

---

## PUT `/playlists/:playlist_id` - Update Playlist

Update playlist metadata or track list.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID |

**Request Body** (`application/json`):

Same fields as POST `/playlists`. To add/reorder tracks, provide the complete `tracks` array.

**Response:** Updated Playlist object

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## DELETE `/playlists/:playlist_id` - Delete Playlist

Delete a playlist.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Not Found |

---

## GET `/playlists/:playlist_id/tracks` - Playlist Tracks

Get the tracks in a playlist.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID |
| secret_token | query | String | no | Secret token for private playlists |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | Track objects |
| next_href | String | URL for next page |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |

---

## GET `/playlists/:playlist_id/reposters` - Playlist Reposters

Get users who reposted a playlist.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Array of MetaUser objects

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |
