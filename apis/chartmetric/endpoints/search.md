# Search

## GET `/search`

Unified search across all entity types. Accepts names or URLs as queries.

**Parameters:**

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| q | String | yes | - | Search query (name, keyword, or URL) |
| type | String | no | "all" | Entity type filter |
| limit | Integer | no | 10 | Results per page |
| offset | Integer | no | 0 | Pagination offset (max 10,000) |

**`type` values:** `all`, `artists`, `tracks`, `playlists`, `curators`, `albums`, `stations`, `cities`

**Response:**

Returns a dictionary with keys for each entity type:

| Field | Type | Description |
|-------|------|-------------|
| artists | Array | Matching artist objects (id, name, image_url, code2, tags, spotify_artist_ids) |
| tracks | Array | Matching track objects (id, name, isrc, artist_names, spotify_track_ids) |
| albums | Array | Matching album objects (id, name, upc, release_date) |
| playlists | Array | Matching playlist objects (id, name, platform, followers) |
| curators | Array | Matching curator objects |
| labels | Array | Matching record labels |
| stations | Array | Matching radio stations |
| cities | Array | Matching cities |

**Example:**

```
GET /api/search?q=Taylor+Swift&type=artists&limit=5
```
