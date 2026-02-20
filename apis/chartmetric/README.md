# Chartmetric API

Music analytics platform tracking 9M+ artists across streaming, social media, charts, and radio.

- **Base URL:** `https://api.chartmetric.com/api`
- **Docs:** https://api.chartmetric.com/apidoc/
- **API Version:** 1.3.0
- **Format:** JSON responses, form-encoded requests

## Authentication

Two-token system:

1. **Refresh token** - assigned on signup, used to get access tokens
2. **Access token** - valid for 1 hour, required on all requests

```bash
# Get access token
curl -X POST https://api.chartmetric.com/api/token \
  -d '{"refreshtoken": "YOUR_REFRESH_TOKEN"}'

# Use access token in requests
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  https://api.chartmetric.com/api/artist/2316
```

## Rate Limits

Sliding window algorithm, per-second evaluation. Limits vary by plan.

Response headers:
- `X-RateLimit-Limit` - requests allowed per period
- `X-RateLimit-Remaining` - remaining requests
- `X-RateLimit-Reset` - unix timestamp for limit reset

**Constraints:**
- Offset parameter cannot exceed 10,000
- Not designed for real-time live applications
- Data is cached daily for most endpoints

## Platforms Covered

| Platform | Streaming | Charts | Social | Audience Stats |
|----------|-----------|--------|--------|----------------|
| Spotify | yes | yes | - | yes (listeners) |
| Apple Music | yes | yes | - | - |
| iTunes | - | yes | - | - |
| YouTube | yes | yes | - | yes |
| TikTok | - | yes | - | yes |
| Instagram | - | - | yes | yes |
| Deezer | yes | yes | - | - |
| Amazon Music | yes | yes | - | - |
| Shazam | - | yes | - | - |
| SoundCloud | - | yes | yes | - |
| Beatport | - | yes | - | - |
| QQ Music | - | yes | - | - |
| Twitch | - | yes | - | - |
| Twitter/X | - | - | yes | - |
| Wikipedia | - | - | yes | - |

## Proprietary Metrics

- **CPP (Career Performance Profile)** - career stage score
- **CM Score** - Chartmetric ranking score per chart type
- **Recent Momentum Score** - current growth rate
- **Network Strength Score** - industry connection breadth

## Endpoint Categories

| Category | Endpoints | Description |
|----------|-----------|-------------|
| [Authentication](endpoints/authentication.md) | 1 | Token management |
| [Search](endpoints/search.md) | 1 | Cross-entity search |
| [Artists](endpoints/artists.md) | 15 | Artist metadata, stats, playlists, audience |
| [Tracks](endpoints/tracks.md) | 7 | Track metadata, charts, playlists |
| [Albums](endpoints/albums.md) | 6 | Album metadata, charts, playlists |
| [Playlists](endpoints/playlists.md) | 5 | Playlist metadata, tracks, similar |
| [Curators](endpoints/curators.md) | 3 | Curator profiles and playlists |
| [Charts](endpoints/charts.md) | 23 | Multi-platform chart data |
| [Radio](endpoints/radio.md) | 1+ | Airplay data |
| [Cities](endpoints/cities.md) | 3 | Geographic music data |

**Total: ~65 endpoints**

See [quick-reference.md](quick-reference.md) for a compact endpoint table.
