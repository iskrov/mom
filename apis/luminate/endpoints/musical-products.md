# Musical Products

## GET `/musical_products/{id}`

Specific commercial release/SKU data, identified by barcode (ICPN/GRID). Represents a particular edition or format of a release (e.g., the CD version vs the vinyl version of an album).

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | String | yes | Luminate product ID, ICPN, or GRID |

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
| external_ids | String | `true`, `false` | Include cross-platform IDs |
| relationships | Array | `musical_recording`, `musical_release_group`, `all`, `none` | Related entities |
| metrics | Array | `none`, `all`, `streams`, `sales` | Consumption metrics |
| atd | Array | `none`, `all`, `streams`, `sales`, `airplay`, `equivalents` | Activity-to-date |
| aggregate_interval | String | `total`, `day`, `week`, `chart_week` | Time aggregation |

**Query Parameters - Streaming Filters:**

| Name | Values |
|------|--------|
| commercial_model | `ad_supported`, `premium`, `none` |
| service_type | `on_demand`, `programmed`, `none` |
| content_type | `audio`, `video`, `none` |
| breakouts | `none`, `all`, `commercial_model`, `service_type`, `content_type`, `distribution_channel`, `store_strata`, `purchase_method`, `product_format` |

**Query Parameters - Sales Filters (US/CA only):**

| Name | Values |
|------|--------|
| sales_type | `song_sales`, `product_sales`, `all` |
| distribution_channel | `digital`, `physical`, `none` |
| purchase_method | `online`, `storefront`, `none` |
| store_strata | `e-commerce`, `mass_market`, `independent`, `direct_to_consumer`, `venue`, `non-traditional`, `none` |
| product_format | `cd`, `cassette`, `vinyl`, `mxcd`, `digital`, `dvd`, `vhs`, `laser`, `none`, `unknown` |

**Query Parameters - Market:**

| Name | Description |
|------|-------------|
| markets | US/CA DMA markets |
| market_filter | Filter by specific markets |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | String | Luminate product ID |
| icpn | Array[String] | ICPN identifiers |
| grid | Array[String] | GRID identifiers |
| title | String | Product title |
| display_artist_name | String | Primary artist |
| artists | Array | `{ name, role, id }` |
| genres | Array | `{ domain, main_genre, genres[] }` |
| release_date | String | Release date |
| duration | String | Total duration |
| languages | Array | Languages |
| parental_warning_type | String | Content warning |
| label | String | Record label |
| compilation_type | String | Compilation classification |
| release_type | String | Release category |
| product_format | String | Physical/digital format |
| edition | String | Edition information |
| external_ids | Object | Cross-platform IDs |
| relationships | Array | Related recordings + release groups |
| metrics | Array | Consumption data (streams, sales) |

**Note:** Products have `product_format` and `edition` fields that are unique to this entity (not on release groups). Metrics include `streams` and `sales` but not direct `airplay` or `equivalents`.
