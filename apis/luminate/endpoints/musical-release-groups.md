# Musical Release Groups

## GET `/musical_release_groups/{id}`

Album-level data. A release group is a logical album grouping that may contain multiple products (editions/formats). This is the entity type (`MRELG`) used in album charts.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | String | yes | Luminate release group ID, ICPN, or GRID |

**Query Parameters - Identification:**

| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| id_type | String | `luminate`, `icpn`, `grid` | `luminate` | ID type being used |

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
| external_ids | String | `true`, `false` | Include ICPN, GRID |
| relationships | Array | `song`, `musical_product`, `all`, `none` | Related entities |
| metrics | Array | `none`, `all`, `streams`, `sales`, `airplay`, `equivalents` | Consumption metrics |
| atd | Array | `none`, `all`, `streams`, `sales`, `airplay`, `equivalents` | Activity-to-date |
| aggregate_interval | String | `total`, `day`, `week`, `chart_week` | Time aggregation |

**Query Parameters - Streaming Filters:**

| Name | Values |
|------|--------|
| commercial_model | `ad_supported`, `premium`, `none` |
| service_type | `on_demand`, `programmed`, `none` |
| content_type | `audio`, `video`, `none` (US, CA, AA only) |
| breakouts | `none`, `all`, `commercial_model`, `service_type`, `content_type`, `distribution_channel`, `store_strata`, `purchase_method`, `product_format` |

**Query Parameters - Sales Filters (US/CA only):**

| Name | Values |
|------|--------|
| sales_type | `song_sales`, `product_sales`, `all` |
| distribution_channel | `digital`, `physical`, `none` |
| purchase_method | `online`, `storefront`, `none` |
| store_strata | `e-commerce`, `mass_market`, `independent`, `direct_to_consumer`, `venue`, `non-traditional`, `none` |
| product_format | `cd`, `cassette`, `vinyl`, `mxcd`, `digital`, `dvd`, `vhs`, `laser`, `none`, `unknown` |

**Query Parameters - Market & Airplay:**

| Name | Description |
|------|-------------|
| markets | US/CA DMA markets |
| market_filter | Filter by specific markets |
| airplay_formats | Airplay format IDs (e.g., `ACMA`, `CW`, `HOH`) |
| airplay_format_filter | Single format filter |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | String | Luminate release group ID |
| icpn | Array[String] | ICPN identifiers |
| grid | Array[String] | GRID identifiers |
| title | String | Album title |
| display_artist_name | String | Primary artist |
| artists | Array | `{ name, role, id }` |
| genres | Array | `{ domain, main_genre, genres[] }` |
| release_date | String | Release date |
| duration | String | Total duration |
| languages | Array | Languages |
| parental_warning_type | String | Content warning |
| label | String | Record label |
| compilation_type | String | Compilation classification |
| release_type | String | Release category (album, EP, single, etc.) |
| external_ids | Object | Cross-platform IDs |
| relationships | Array | Related songs + products |
| metrics | Array | Full consumption (streams, sales, airplay, equivalents) |

**Note:** Release groups support the full set of metrics including `airplay` and `equivalents`, unlike recordings and products.
