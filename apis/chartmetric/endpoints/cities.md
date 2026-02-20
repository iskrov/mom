# Cities

Geographic/city-level music data.

## GET `/cities` - List Cities

List all cities tracked by Chartmetric.

**No parameters required.**

---

## GET `/city/:id/:source/top-artists` - Top Artists in City

Artists trending in a specific city.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric city ID |
| source | String | yes | Data source platform |

---

## GET `/city/:id/:source/top-tracks` - Top Tracks in City

Tracks trending in a specific city.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric city ID |
| source | String | yes | Data source platform |

**Notes:**
- Use `/cities` to find city IDs first
- City-level Shazam data is also available via `/charts/shazam` with the `city` parameter
- Cities are also searchable via the `/search` endpoint with `type=cities`
