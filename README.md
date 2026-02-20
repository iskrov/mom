# Music Data APIs - Hackathon Reference

A structured reference of music industry data APIs for our hackathon project.

## Available API Providers

| Provider | Category | Docs |
|----------|----------|------|
| [Chartmetric](apis/chartmetric/README.md) | Music analytics (streaming, social, charts, radio) | [Endpoints](apis/chartmetric/endpoints/) |
| [Luminate](apis/luminate/README.md) | Industry consumption data (streams, sales, airplay, Billboard charts) | [Endpoints](apis/luminate/endpoints/) |
| [Royalti.io](apis/royalti/README.md) | Royalty management (catalog, splits, payments, DDEX distribution) | [Endpoints](apis/royalti/endpoints/) |
| [JamBase](apis/jambase/README.md) | Live music events (concerts, festivals, venues, ticketing) | [Endpoints](apis/jambase/endpoints/) |

## Provider Comparison

| Aspect | Chartmetric | Luminate | Royalti.io | JamBase |
|--------|-------------|---------|------------|---------|
| Focus | Market analytics | Industry consumption | Royalty management | Live events |
| Endpoints | ~65 | 9 | ~160 | 17 |
| Streaming metrics | Playlist reach, trends | Raw consumption data | Revenue per stream | - |
| Charts | Platform charts | Billboard (200+) | - | - |
| Social media | Yes | No | No | No |
| Sales data | No | Yes | Yes (via royalties) | No |
| Revenue/royalty | No | No | Full accounting | No |
| Live events | No | No | No | Yes (3M+ events) |
| Venues | No | No | No | Yes (170K+) |
| Ticketing | No | No | No | Yes (15+ sources) |
| Geo search | City-level | 63 territories + DMA | No | Lat/lng, IP, metros |
| Content distribution | No | No | DDEX | No |

## Repository Structure

```
apis/
  <provider-name>/
    README.md              # Provider overview, auth, rate limits
    quick-reference.md     # Compact table of all endpoints
    endpoints/
      <category>.md        # Detailed endpoint docs per category
```

## Adding a New API Provider

1. Create `apis/<provider-name>/`
2. Add a `README.md` with: base URL, auth method, rate limits, data overview
3. Add `quick-reference.md` with a compact endpoint table
4. Create `endpoints/` folder with one `.md` per category
5. Update this root README table

## Conventions

- All endpoint paths are relative to the provider's base URL
- Parameters marked with **required** must be included
- Date parameters use ISO format `YYYY-MM-DD` unless noted
- Response fields listed are the key fields, not exhaustive
