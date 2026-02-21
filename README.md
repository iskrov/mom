# Remix Radar — Measure of Music 2026 Hackathon

Data-driven A&R tool for identifying high-performing unofficial SoundCloud remixes, projecting revenue potential from DSP releases, and providing go/no-go recommendations.

## Project Documents

| Document | Description |
|----------|-------------|
| [idea_remix_radar.md](idea_remix_radar.md) | Product roadmap, workflows, use cases, and team tasks |
| [mom_hackathon_guide.md](mom_hackathon_guide.md) | Hackathon rules, mandatory check-ins, judging criteria, Chartmetric requirement |

## Pipeline & Scripts

The Remix Radar pipeline evaluates any SoundCloud track through five steps:

1. **SoundCloud** — Resolve URL, fetch engagement metrics (plays, likes, reposts, engagement rate), parse remix title
2. **Chartmetric** — Find original artist, enrich with Spotify followers/listeners, "Where People Listen" geo data, cross-platform IDs
3. **Cross-platform IDs** — Resolve Chartmetric → Spotify, iTunes, Deezer; fetch ISRC for the original song
4. **Luminate** — Benchmark original song consumption (when service available)
5. **Revenue Projection** — 3-tier model (conservative / mid / optimistic) and viability assessment vs $50K threshold

### Running the Pipeline

```bash
# From project root
python -m scripts.pipeline "https://soundcloud.com/artist/track"

# Default test URL (Blinding Lights remix) if no argument given
python -m scripts.pipeline
```

**Requirements:** `.env` in project root with `CHARTMETRIC_REFRESH_TOKEN`, `LUMINATE_API_KEY`, `LUMINATE_EMAIL`, `LUMINATE_PASSWORD`. See [Conventions](#conventions) for setup.

### Scripts Layout

```
scripts/
  config.py              # Credentials, auth tokens, revenue thresholds
  models.py              # Title parser, revenue projection, viability assessment
  pipeline.py            # Main orchestrator (run via python -m scripts.pipeline)
  __main__.py            # Entry point for python -m scripts
  platforms/             # Per-platform API clients
    soundcloud.py        # SoundCloudClient — resolve, search, metrics, ISRC
    chartmetric.py       # ChartmetricClient — artist search, geo, cross-platform IDs
    luminate.py          # LuminateClient — ISRC lookups, consumption data
```

### Using the Clients in Code

```python
from scripts.platforms import SoundCloudClient, ChartmetricClient

sc = SoundCloudClient()
track = sc.resolve("https://soundcloud.com/...")
metrics = sc.compute_metrics(track)

cm = ChartmetricClient()
artist = cm.find_artist("The Weeknd")  # smart name-variant matching
geo = cm.get_where_people_listen(artist["id"])
```

---

## Available API Providers

| Provider | Category | Docs |
|----------|----------|------|
| [Chartmetric](apis/chartmetric/README.md) | Music analytics (streaming, social, charts, radio) | [Endpoints](apis/chartmetric/endpoints/) |
| [Luminate](apis/luminate/README.md) | Industry consumption data (streams, sales, airplay, Billboard charts) | [Endpoints](apis/luminate/endpoints/) |
| [Royalti.io](apis/royalti/README.md) | Royalty management (catalog, splits, payments, DDEX distribution) | [Endpoints](apis/royalti/endpoints/) |
| [JamBase](apis/jambase/README.md) | Live music events (concerts, festivals, venues, ticketing) | [Endpoints](apis/jambase/endpoints/) |
| [SoundCloud](apis/soundcloud/README.md) | Audio platform (streaming, uploads, social, playlists) | [Endpoints](apis/soundcloud/endpoints/) |

## Provider Comparison

| Aspect | Chartmetric | Luminate | Royalti.io | JamBase | SoundCloud |
|--------|-------------|---------|------------|---------|------------|
| Focus | Market analytics | Industry consumption | Royalty management | Live events | Audio platform |
| Endpoints | ~65 | 9 | ~160 | 17 | ~62 |
| Streaming metrics | Playlist reach, trends | Raw consumption data | Revenue per stream | - | Stream URLs (MP3, HLS, Opus) |
| Charts | Platform charts | Billboard (200+) | - | - | - |
| Social media | Yes | No | No | No | Yes (follows, reposts, likes) |
| Sales data | No | Yes | Yes (via royalties) | No | No |
| Revenue/royalty | No | No | Full accounting | No | No |
| Live events | No | No | No | Yes (3M+ events) | No |
| Venues | No | No | No | Yes (170K+) | No |
| Ticketing | No | No | No | Yes (15+ sources) | No |
| Geo search | City-level | 63 territories + DMA | No | Lat/lng, IP, metros | No |
| Content distribution | No | No | DDEX | No | Upload (500MB, 9 formats) |
| Track catalog | No | No | Yes | No | Yes (300M+ tracks) |
| Playlists | Read-only analytics | No | No | No | Full CRUD |
| Comments | No | No | No | No | Yes |

## Repository Structure

```
apis/                     # API provider reference docs
  <provider-name>/
    README.md             # Provider overview, auth, rate limits
    quick-reference.md    # Compact table of all endpoints
    endpoints/
      <category>.md       # Detailed endpoint docs per category

scripts/                  # Remix Radar pipeline (see Pipeline & Scripts above)
  config.py               # Shared config and auth
  models.py               # Title parser, revenue model
  pipeline.py             # Main orchestrator
  platforms/              # SoundCloud, Chartmetric, Luminate clients
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

### Pipeline Setup

Create a `.env` file in the project root (copy from `.env.example` if available) with:

- `CHARTMETRIC_REFRESH_TOKEN` — from Chartmetric dashboard
- `LUMINATE_API_KEY`, `LUMINATE_EMAIL`, `LUMINATE_PASSWORD` — Luminate credentials
