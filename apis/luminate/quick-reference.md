# Luminate Music API - Quick Reference

All paths relative to `https://api.luminatedata.com`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth` | Get access token (24h lifetime) |
| POST | `/search` | Search across all music entity types |
| GET | `/artists/{id}` | Artist metadata, discography, consumption data |
| GET | `/songs/{id}` | Song metadata + consumption data |
| GET | `/musical_recordings/{id}` | Recording (ISRC) metadata + consumption data |
| GET | `/musical_products/{id}` | Product (barcode) metadata + consumption data |
| GET | `/musical_release_groups/{id}` | Album metadata + consumption data |
| GET | `/charts` | List all available charts |
| GET | `/charts/{id}` | Chart rankings for a specific week |

## Common Query Parameters (shared across data endpoints)

| Parameter | Values | Description |
|-----------|--------|-------------|
| `id_type` | `luminate`, `isrc`, `icpn`, `grid`, `isni` | ID type (varies by endpoint) |
| `location` | ISO 3166-1 alpha-2 (e.g., `US`) | Territory for consumption data |
| `start_date` | `YYYY-MM-DD` | Aggregation start date |
| `end_date` | `YYYY-MM-DD` | Aggregation end date |
| `chart_week` | `YYYY-Www` | Chart week (Fri-Thu) |
| `metadata_level` | `max`, `min` | Metadata verbosity |
| `external_ids` | `true`, `false` | Include cross-platform IDs |
| `relationships` | varies by entity | Include related entities |
| `metrics` | `none`, `all`, `streams`, `sales`, `airplay`, `equivalents` | Consumption metrics |
| `atd` | same as metrics | Activity-to-date (historical) |
| `aggregate_interval` | `total`, `day`, `week`, `chart_week` | Time aggregation |
| `breakouts` | `none`, `all`, `commercial_model`, `service_type`, `content_type`, ... | Data segmentation |

## Streaming Filters

| Parameter | Values |
|-----------|--------|
| `content_type` | `audio`, `video` |
| `commercial_model` | `premium`, `ad_supported` |
| `service_type` | `on_demand`, `programmed` |

## Sales Filters (US/CA only)

| Parameter | Values |
|-----------|--------|
| `distribution_channel` | `digital`, `physical` |
| `purchase_method` | `online`, `storefront` |
| `store_strata` | `e-commerce`, `mass_market`, `independent`, `direct_to_consumer`, `venue`, `non-traditional` |
| `product_format` | `cd`, `cassette`, `vinyl`, `mxcd`, `digital`, `dvd`, `vhs`, `laser` |
| `release_type` | `album`, `single`, `ep`, `video`, `playlist` |

## Chart Metric Names

`Total`, `Album Sales`, `Song Sales`, `Audio Streams`, `Video Streams`, `Audio Ad Supported Streams`, `Audio Premium Streams`, `Video Ad Supported Streams`, `Video Premium Streams`, `Streams (Album Equivalents)`, `Song Sales (Album Equivalents)`
