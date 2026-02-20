# Charts

Luminate provides 200+ charts including all Billboard charts. Chart data is available from 2023-W01 onward.

## GET `/charts` - List Available Charts

Browse and filter the chart catalog.

**Query Parameters:**

| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| location | String | ISO 3166-1 alpha-2 or `all` | - | Filter by territory |
| chart_owner | String | `all`, `billboard`, `luminate` | - | Filter by chart owner |

**Response:**

```json
{
  "charts": [
    {
      "id": "chart_abc123",
      "chart_name": "Billboard Hot 100",
      "chart_owner": "billboard",
      "entity_type": "SONG",
      "description": "...",
      "location": "US",
      "depth": 200,
      "earliest_chart_week": "2023-W01"
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| id | String | Chart identifier (use with `/charts/{id}`) |
| chart_name | String | Chart name |
| chart_owner | String | `billboard` or `luminate` |
| entity_type | String | `SONG` or `MRELG` (album/release group) |
| description | String | Chart methodology description |
| location | String | Territory (ISO code) |
| depth | Integer | Number of ranked positions (typically 200) |
| earliest_chart_week | String | Earliest available week (`YYYY-Www`) |

---

## GET `/charts/{id}` - Chart Rankings

Get rankings for a specific chart and week.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | String | yes | Chart ID (from `/charts` listing) |

**Query Parameters:**

| Name | Type | Format | Default | Description |
|------|------|--------|---------|-------------|
| chart_week | String | `YYYY-Www` | Latest published week | Chart week to retrieve |

**Response:**

```json
{
  "id": "chart_abc123",
  "chart_name": "Billboard Hot 100",
  "chart_owner": "billboard",
  "entity_type": "SONG",
  "description": "...",
  "location": "US",
  "depth": 200,
  "earliest_chart_week": "2023-W01",
  "chart_metrics": ["Total", "Audio Streams", "Video Streams", ...],
  "chart_week": "2026-W07",
  "start_date": "2026-02-07",
  "end_date": "2026-02-13",
  "ranking": [
    {
      "rank": 1,
      "id": "LUMINATE_ENTITY_ID",
      "href": "/songs/LUMINATE_ENTITY_ID",
      "chart_history": {
        "premiere_week": "2025-W48",
        "weeks_on": 12,
        "peak": 1,
        "low": 15
      },
      "chart_metrics": [
        {"name": "Total", "value": 12345678},
        {"name": "Audio Streams", "value": 10000000}
      ]
    }
  ]
}
```

**Ranking item fields:**

| Field | Type | Description |
|-------|------|-------------|
| rank | Integer | Chart position |
| id | String | Luminate entity ID |
| href | String | Link to entity detail endpoint |
| chart_history.premiere_week | String | First week on chart |
| chart_history.weeks_on | Integer | Total weeks on chart |
| chart_history.peak | Integer | Best (lowest number) rank |
| chart_history.low | Integer | Worst rank achieved |
| chart_metrics | Array | Metric values for this entry |

**Available chart metric names:**

| Metric | Description |
|--------|-------------|
| Total | Aggregate activity score |
| Album Sales | Physical + digital album sales |
| Song Sales | Digital song sales |
| Audio Streams | Audio streaming count |
| Video Streams | Video streaming count |
| Audio Ad Supported Streams | Ad-supported audio streams |
| Audio Premium Streams | Premium audio streams |
| Video Ad Supported Streams | Ad-supported video streams |
| Video Premium Streams | Premium video streams |
| Streams (Album Equivalents) | Stream-to-album conversion |
| Song Sales (Album Equivalents) | Song-sale-to-album conversion |

**Status Codes:**
- `200` - Success
- `204` - Chart not found
