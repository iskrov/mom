# Search

## POST `/search`

Search across all music entity types. Returns basic identifiers for use with detailed data endpoints.

**Request Body (JSON):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| query | String | yes | Search text (name, title, keyword) |
| entity_type | String | yes | Entity to search (see values below) |
| from | Integer | no | Pagination offset (default: 0) |
| size | Integer | no | Results per page (default: 10, max: 50) |

**`entity_type` values:** `artist`, `song`, `musical_recording`, `musical_release_group`, `musical_product`

**Response:**

```json
{
  "results": [...],
  "from": 0,
  "size": 10,
  "total_results": 142
}
```

**Result fields for `artist`:**

| Field | Type | Description |
|-------|------|-------------|
| id | String | Luminate artist ID |
| artist_name | String | Artist name |

**Result fields for all other entity types:**

| Field | Type | Description |
|-------|------|-------------|
| id | String | Luminate entity ID |
| title | String | Entity title |
| display_artist_name | String | Associated artist name |

**Limits:**
- Max 10,000 total matches per search query
- Max 50 results per request
- Use `from` parameter for pagination through results

**Example:**

```bash
curl -X POST https://api.luminatedata.com/search \
  -H "x-api-key: KEY" \
  -H "authorization: TOKEN" \
  -H "Accept: application/vnd.luminate-data.svc-apibff.v1+json" \
  -H "Content-Type: application/json" \
  -d '{"query": "Taylor Swift", "entity_type": "artist", "size": 5}'
```
