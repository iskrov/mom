# Artists

## GET `/artists/{id}`

Artist metadata, discography, and consumption data. The most feature-rich endpoint with the broadest set of filters.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | String | yes | Luminate artist ID or ISNI |

**Query Parameters - Identification:**

| Name | Type | Values | Default | Description |
|------|------|--------|---------|-------------|
| id_type | String | `luminate`, `isni` | `luminate` | ID type being used |

**Query Parameters - Time & Location:**

| Name | Type | Format | Default | Description |
|------|------|--------|---------|-------------|
| location | String | ISO 3166-1 alpha-2 | - | Territory for consumption data |
| start_date | String | `YYYY-MM-DD` | 7 days prior | Aggregation start date |
| end_date | String | `YYYY-MM-DD` | Current date | Aggregation end date |
| chart_week | String | `YYYY-Www` | - | Chart week (Fri-Thu, overrides date range) |

**Query Parameters - Data Control:**

| Name | Type | Values | Description |
|------|------|--------|-------------|
| metadata_level | String | `max`, `min` | Metadata verbosity |
| external_ids | String | `true`, `false` | Include Spotify, ISNI, etc. |
| relationships | Array | `artist`, `none` | Related artist entities |
| discography | String | `musical_release_group`, `song`, `none` | Include artist's works |
| metrics | Array | `none`, `all`, `streams`, `sales`, `airplay`, `equivalents` | Consumption metrics |
| atd | Array | `none`, `all`, `streams`, `sales`, `airplay`, `equivalents` | Activity-to-date totals |
| aggregate_interval | String | `total`, `day`, `week`, `chart_week` | Time aggregation |

**Query Parameters - Streaming Filters:**

| Name | Type | Values | Description |
|------|------|--------|-------------|
| commercial_model | String | `ad_supported`, `premium`, `none` | Subscription type |
| service_type | String | `on_demand`, `programmed`, `none` | Delivery type |
| content_type | String | `audio`, `video`, `none` | Content format (US, CA, AA only) |
| breakouts | Array | `none`, `all`, `commercial_model`, `content_type`, `service_type`, `distribution_channel`, `store_strata`, `purchase_method`, `product_format`, `release_type` | Data segmentation |

**Query Parameters - Sales Filters (US/CA only):**

| Name | Type | Values | Description |
|------|------|--------|-------------|
| sales_type | Array | `song_sales`, `product_sales`, `all` | Sales metric types |
| distribution_channel | String | `digital`, `physical`, `none` | Distribution filter |
| purchase_method | String | `online`, `storefront`, `none` | Purchase method |
| store_strata | Array | `e-commerce`, `mass_market`, `independent`, `direct_to_consumer`, `venue`, `non-traditional`, `none` | Store category |
| product_format | Array | `cd`, `cassette`, `vinyl`, `mxcd`, `digital`, `dvd`, `vhs`, `laser`, `none`, `unknown` | Physical format |
| release_type | Array | `album`, `ep`, `video`, `single`, `playlist`, `none`, `unknown` | Release type |

**Query Parameters - Geographic & Airplay:**

| Name | Type | Description |
|------|------|-------------|
| markets | Array | US/CA DMA markets to include |
| market_filter | Array | Filter consumption by specific markets |
| airplay_formats | Array | Airplay format IDs to include |
| airplay_format_filter | String | Filter airplay by single format |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | String | Luminate artist ID |
| isni | String | International Standard Name Identifier |
| artist_name | String | Primary name |
| artist_type | String | Classification (person, group) |
| alternate_names | Array | Other known names |
| country_of_origin | String | Origin country |
| gender | String | Gender |
| genres | Array | `{ domain, main_genre, genres[] }` |
| languages | Array | Languages used |
| music_type | String | Music category |
| external_ids | Object | Cross-platform IDs (Spotify, etc.) |
| relationships | Array | Related artist entities |
| discography | Array | Musical works (when requested) |
| metrics | Array | Consumption data (streams, sales, airplay, equivalents) |
| start_date | String | Data period start |
| end_date | String | Data period end |
| location | String | Territory queried |
