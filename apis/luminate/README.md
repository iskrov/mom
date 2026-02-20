# Luminate Music API

Industry-standard music consumption data (formerly Nielsen Music / MRC Data). Covers streaming, sales, airplay, and chart data across 63 territories. Includes all Billboard charts.

- **Base URL:** `https://api.luminatedata.com`
- **Docs:** https://docs.luminatedata.com/
- **Format:** JSON responses
- **Formerly known as:** Nielsen Music, MRC Data, Music Connect API

## Authentication

Three credentials required: API key, username, and password.

```bash
# Step 1: Get access token (valid 24 hours)
curl -X POST https://api.luminatedata.com/auth \
  -H "x-api-key: YOUR_API_KEY" \
  -H "content-type: application/x-www-form-urlencoded" \
  -d "username=YOUR_EMAIL&password=YOUR_PASSWORD"

# Step 2: Use on all subsequent requests
curl https://api.luminatedata.com/artists/ARTIST_ID \
  -H "x-api-key: YOUR_API_KEY" \
  -H "authorization: YOUR_ACCESS_TOKEN" \
  -H "Accept: application/vnd.luminate-data.svc-apibff.v1+json"
```

**Token lifetime:** 24 hours (86400 seconds)

## Data Model

Luminate uses a hierarchical entity model, from most granular to most aggregate:

```
musical_recording (ISRC)         ← individual recording
    └── song                     ← composition (may group multiple recordings)
musical_product (barcode/ICPN)   ← specific commercial SKU/format
    └── musical_release_group    ← album-level logical grouping
artist                           ← artist entity
```

**Key distinction:** A `musical_product` is a specific edition (CD, vinyl, digital) while a `musical_release_group` is the album as a whole.

## Consumption Data Categories

| Category | Description | Territories |
|----------|-------------|-------------|
| **Streams** | Audio + video streaming data | 63 territories |
| **Sales** | Physical + digital sales (song-level and product-level) | US, CA |
| **Airplay** | Radio spins + audience data | US, CA |
| **Equivalents** | Weighted formula combining streams + sales + digital song sales | US, CA (Album Eq), others (Stream Eq) |

## Streaming Breakouts (Filters)

Data can be sliced along three dimensions:

| Dimension | Values | Availability |
|-----------|--------|-------------|
| `content_type` | `audio`, `video` | US, CA, AA (worldwide) |
| `commercial_model` | `premium`, `ad_supported` | All 63 territories |
| `service_type` | `on_demand`, `programmed` | All 63 territories |

## Sales Breakouts (US/CA only)

| Dimension | Values |
|-----------|--------|
| `distribution_channel` | `digital`, `physical` |
| `purchase_method` | `online`, `storefront` |
| `store_strata` | `e-commerce`, `mass_market`, `independent`, `direct_to_consumer`, `venue`, `non-traditional` |
| `product_format` | `cd`, `cassette`, `vinyl`, `mxcd`, `digital`, `dvd`, `vhs`, `laser` |
| `release_type` | `album`, `single`, `ep`, `video`, `playlist` |

## Geographic Coverage

- **63 territories** using ISO 3166-1 alpha-2 codes (e.g., `US`, `GB`, `JP`)
- Special code `AA` = worldwide aggregate
- **Market-level data** (US/CA only): 241+ DMA markets (e.g., `1` = New York, `2` = Los Angeles)
- Use `market_id=-1` for national data, `all` for all markets

## Chart Data

- **200+ charts** including all Billboard charts
- **Chart owners:** `billboard`, `luminate`
- **Entity types:** `SONG`, `MRELG` (album/release group)
- **Depth:** Up to 200 ranked positions per chart
- **Chart week:** Friday-Thursday cycle, format `YYYY-Www`
- **Historical data:** Available from `2023-W01` onward

## Airplay Formats (US/CA only)

22 US formats + 8 Canada formats. Examples: Adult Contemporary (`ACMA`), Country (`CW`), Hot 100 (`HOH`), Mainstream Top 40 (`TFMA`). See [endpoints/data-filters.md](endpoints/data-filters.md) for full list.

## ID Systems

| ID Type | Used For | Format |
|---------|----------|--------|
| Luminate ID | All entities | Internal numeric |
| ISRC | Musical recordings, songs | Standard ISRC |
| ICPN | Musical products, release groups | International barcode |
| GRID | Musical products, release groups | Global Release ID |
| ISNI | Artists | Standard ISNI |

## Endpoint Categories

| Category | Endpoints | Description |
|----------|-----------|-------------|
| [Authentication](endpoints/authentication.md) | 1 | Token management |
| [Search](endpoints/search.md) | 1 | Cross-entity search |
| [Artists](endpoints/artists.md) | 1 | Artist metadata + consumption data |
| [Songs](endpoints/songs.md) | 1 | Song (composition) data |
| [Musical Recordings](endpoints/musical-recordings.md) | 1 | ISRC-level recording data |
| [Musical Products](endpoints/musical-products.md) | 1 | Barcode/SKU-level product data |
| [Musical Release Groups](endpoints/musical-release-groups.md) | 1 | Album-level data |
| [Charts](endpoints/charts.md) | 2 | Billboard + Luminate chart rankings |
| [Data Filters](endpoints/data-filters.md) | - | Reference for all filter values |

**Total: 9 endpoints** (fewer endpoints than Chartmetric, but each endpoint is highly parameterized with deep data)

See [quick-reference.md](quick-reference.md) for a compact endpoint table.
