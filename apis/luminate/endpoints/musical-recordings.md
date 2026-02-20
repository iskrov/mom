# Musical Recordings

## GET `/musical_recordings/{id}`

Individual recording metadata and consumption data. A recording is the most granular music entity, identified by ISRC.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | String | yes | Luminate recording ID or ISRC |

**Query Parameters - Identification:**

| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| id_type | String | `luminate`, `isrc` | `luminate` | ID type being used |

**Query Parameters - Time & Location:**

| Name | Type | Format | Default | Description |
|------|------|--------|---------|-------------|
| location | String | ISO 3166-1 alpha-2 | - | Territory |
| start_date | String | `YYYY-MM-DD` | 7 days prior | Aggregation start |
| end_date | String | `YYYY-MM-DD` | Current date | Aggregation end |
| chart_week | String | `YYYY-Www` | - | Chart week (Fri-Thu) |

**Query Parameters - Data Control:**

| Name | Type | Values | Description |
|------|------|--------|-------------|
| metadata_level | String | `max`, `min` | Metadata verbosity |
| external_ids | String | `true`, `false` | Include cross-platform IDs |
| relationships | Array | `song`, `musical_product`, `all`, `none` | Related entities |
| metrics | Array | `none`, `all`, `streams`, `sales` | Consumption metrics |
| atd | Array | `none`, `all`, `streams`, `sales`, `airplay`, `equivalents` | Activity-to-date |
| aggregate_interval | String | `total`, `day`, `week`, `chart_week` | Time aggregation |

**Query Parameters - Streaming Filters:**

| Name | Values | Description |
|------|--------|-------------|
| commercial_model | `ad_supported`, `premium`, `none` | Subscription type |
| service_type | `on_demand`, `programmed`, `none` | Delivery type |
| content_type | `audio`, `video`, `none` | Content format (US, CA, AA) |
| breakouts | `none`, `all`, `commercial_model`, `service_type`, `content_type` | Segmentation |

**Query Parameters - Market:**

| Name | Description |
|------|-------------|
| markets | US/CA DMA markets to include |
| market_filter | Filter by specific markets |
| airplay_formats | Airplay format IDs |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | String | Luminate recording ID |
| isrc | String | ISRC code |
| title | String | Recording title |
| display_artist_name | String | Primary artist |
| artists | Array | `{ name, role, id }` |
| genres | Array | `{ domain, main_genre, genres[] }` |
| release_date | String | Release date |
| duration | Number | Duration |
| languages | Array | Languages |
| parental_warning_type | String | Content warning |
| label | String | Record label |
| external_ids | Object | Cross-platform IDs |
| relationships | Array | Related entities (songs, products) |
| metrics | Array | Consumption data (streams, sales) |

**Note:** Recordings have `streams` and `sales` metrics but no direct `airplay` or `equivalents` (those are available at the song and release group level).
