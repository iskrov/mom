# Data Filters Reference

Complete reference for all filter values used across Luminate endpoints.

## Streaming Filters

Available on all data endpoints.

### content_type (US, CA, AA only)

| Value | Description |
|-------|-------------|
| `audio` | Audio-only streams |
| `video` | Video streams |
| `none` | Exclude filter |

### commercial_model

| Value | Description |
|-------|-------------|
| `premium` | Paid subscription streams |
| `ad_supported` | Free/ad-supported streams |
| `none` | Exclude filter |

### service_type

| Value | Description |
|-------|-------------|
| `on_demand` | User-initiated playback |
| `programmed` | Algorithmic/radio-style playback |
| `none` | Exclude filter |

## Sales Filters (US/CA only)

### sales_type

| Value | Description |
|-------|-------------|
| `song_sales` | Individual song purchases |
| `product_sales` | Album/product purchases |
| `all` | Both types |

### distribution_channel

| Value | Description |
|-------|-------------|
| `digital` | Digital sales |
| `physical` | Physical sales |
| `none` | Exclude filter |

### purchase_method

| Value | Description |
|-------|-------------|
| `online` | Online purchases |
| `storefront` | In-store purchases |
| `none` | Exclude filter |

### store_strata

| Value | Description |
|-------|-------------|
| `e-commerce` | Online retailers |
| `mass_market` | Big box / mass market |
| `independent` | Independent retailers |
| `direct_to_consumer` | Direct artist/label sales |
| `venue` | Concert/venue sales |
| `non-traditional` | Non-traditional channels |
| `none` | Exclude filter |

### product_format

| Value | Description |
|-------|-------------|
| `cd` | Compact disc |
| `cassette` | Cassette tape |
| `vinyl` | Vinyl record |
| `mxcd` | Mixed CD |
| `digital` | Digital download |
| `dvd` | DVD |
| `vhs` | VHS tape |
| `laser` | LaserDisc |
| `none` | Exclude filter |
| `unknown` | Unknown format |

### release_type (artists endpoint only)

| Value | Description |
|-------|-------------|
| `album` | Full album |
| `single` | Single release |
| `ep` | Extended play |
| `video` | Video release |
| `playlist` | Playlist release |
| `none` | Exclude filter |
| `unknown` | Unknown type |

## Breakouts

Request segmented data by passing `breakouts` parameter. Multiple values can be combined.

| Value | Description | Applies to |
|-------|-------------|------------|
| `none` | No breakouts | All |
| `all` | All available breakouts | All |
| `commercial_model` | Split by premium/ad-supported | Streams |
| `service_type` | Split by on-demand/programmed | Streams |
| `content_type` | Split by audio/video | Streams (US, CA, AA) |
| `distribution_channel` | Split by digital/physical | Sales |
| `store_strata` | Split by store type | Sales |
| `purchase_method` | Split by online/storefront | Sales |
| `product_format` | Split by physical format | Sales |
| `release_type` | Split by release type | Artists only |

## Airplay Format IDs (US/CA only)

Available on: `/songs`, `/musical_release_groups`, `/artists`

### US Formats

| ID | Format |
|----|--------|
| `ACMA` | Adult Contemporary |
| `ACAH` | Adult Hits |
| `RBAD` | Adult R&B |
| `ACTF` | Adult Top 40 |
| `MR` | Alternative |
| `GAAC` | Christian AC |
| `GA` | Christian Full Panel |
| `OL` | Classic Hits |
| `CR` | Classic Rock |
| `CG` | College Radio |
| `CW` | Country |
| `TFDC` | Dance |
| `GP` | Gospel |
| `HOH` | Hot 100 |
| `SP` | Latin |
| `RBMA` | Mainstream R&B/Hip-Hop |
| `AO` | Mainstream Rock |
| `TFMA` | Mainstream Top 40 |
| `SPRM` | Regional Mexican |
| `TFRH` | Rhythmic |
| `SJ` | Smooth Jazz |
| `AA` | Triple A |

### Canada Formats

| ID | Format |
|----|--------|
| `CMAC` | Canada AC (Mainstream) |
| `CAAF` | Canada All Format |
| `CT` | Canada CHR/Top 40 |
| `CC` | Canada Country |
| `CHTT` | Canada Hot AC |
| `CAAR` | Canada Mainstream Rock |
| `CAMR` | Canada Modern Rock |
| `CA` | Canada Rock |

### Special

| ID | Description |
|----|-------------|
| `all` | All formats for the specified location |

## Location IDs

63 territories using ISO 3166-1 alpha-2 codes. Special code `AA` = worldwide aggregate.

**Data availability by location:**
- **All 63 territories:** Streaming data (commercial_model, service_type)
- **US, CA, AA only:** content_type filter
- **US, CA only:** Sales data, airplay data, market-level data, equivalents

## Market IDs (US/CA only)

241+ DMA markets. Format: numeric IDs.

| ID | Market |
|----|--------|
| `all` | All markets for location |
| `-1` | National |
| `1` | New York, NY |
| `2` | Los Angeles, CA |
| `3` | Chicago, IL |
| `4` | Philadelphia, PA |
| `5` | San Francisco, CA |
| `6` | Boston, MA |
| `7` | Dallas-Fort Worth, TX |
| ... | (241 total US markets + CA markets) |
| `999` | Others |

Full list at https://docs.luminatedata.com/docs/market-ids
