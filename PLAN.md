# Remix Radar — Implementation Plan

## 1. Opportunity Score — Design & Philosophy

### Purpose

A single 0–100 score answering: "Should we pursue clearance for this remix?"

The score is NOT a risk metric. It frames bootleg remixes as **upside opportunities** —
revenue capture, crossover marketing, and artist repositioning — rather than threats
to be taken down.

### Philosophy

- **One number, clear recommendation.** A&Rs need a decision, not a data dump.
- **Breakdown underneath.** Three sub-scores explain the "why" for anyone who wants to dig in.
- **Non-linear scaling.** The difference between 10K and 100K plays matters more than
  the difference between 1M and 2M. Log-scaling throughout.
- **Reward discovery.** A developing remixer with explosive growth remixing a superstar
  is the most valuable find. The score explicitly rewards this "stage gap."
- **Penalize stagnation.** Mid-level artists in steady/decline rarely move the needle.
  The score reflects this industry reality.

### Formula

```
Opportunity Score = (Demand x 0.40) + (Conversion x 0.35) + (Momentum x 0.25)
```

Thresholds:
- 80–100: STRONG — Pursue immediately
- 60–79:  MODERATE — Worth evaluating
- 40–59:  MARGINAL — Proceed with caution
- 0–39:   WEAK — Unlikely to justify clearance costs

---

### Component 1: Demand Score (0–100) — Weight: 40%

"Is the remix actually popping on SoundCloud?"

Pure SoundCloud engagement data. This is the ground truth — real people are
listening to this remix right now.

| Data Point | Source | Scaling | Notes |
|------------|--------|---------|-------|
| `playback_count` | SC `resolve` / `search` | Log: 10K=20, 50K=35, 100K=45, 500K=60, 1M=70, 5M+=90 | Primary volume signal |
| `engagement_rate` | SC derived: `likes / plays` | 0.5%=20, 1%=40, 2%=60, 3%+=80 | Quality of attention, not just volume |
| `daily_velocity` | SC derived: `plays / days_live` | 500/d=20, 1K=35, 2K=50, 5K=70, 10K+=90 | Is it still growing or stale? |
| `comment_count` | SC track | Bonus: >100 comments = +5 | Community engagement signal |
| `reposts_count` | SC track | Bonus: >50 reposts = +5 | Organic distribution signal |

Demand = weighted_avg(plays_score x 0.40, engagement_score x 0.30, velocity_score x 0.30)
         + comment_bonus + repost_bonus (capped at 100)

---

### Component 2: Conversion Score (0–100) — Weight: 35%

"Will SoundCloud traction translate to DSP revenue?"

Cross-platform data from Chartmetric. A remix can have 5M SC plays but if neither
artist has DSP presence, the conversion to Spotify/Apple revenue is uncertain.

| Data Point | Source | Scaling | Notes |
|------------|--------|---------|-------|
| Original artist `spotify_monthly_listeners` | CM `find_artist` (search result) | Log: 10K=15, 100K=30, 1M=50, 10M=70, 50M+=90 | Market ceiling — how big is the addressable audience? |
| Remix artist `spotify_monthly_listeners` | CM `find_artist` (search result) | Log: same scale | Proves the remixer can drive DSP traffic |
| Remix artist `spotify_followers_to_listeners_ratio` | CM `find_artist` (search result) | <0.05=20, 0.05-0.1=40, 0.1-0.2=60, 0.2+=80 | Loyalty signal — high ratio = fans actively follow, not just passive algo listeners |
| Geographic divergence | CM `get_where_people_listen` for both artists | Jaccard distance on top-10 cities | If remix artist reaches different cities than original, that's crossover value |
| Remix artist `tiktok_followers` | CM artist stats or search | Log: 10K=20, 100K=40, 1M=60, 5M+=80 | Viral distribution channel |

Conversion = weighted_avg(
    original_listeners_score x 0.30,
    remix_listeners_score x 0.25,
    loyalty_score x 0.15,
    geo_divergence_score x 0.15,
    tiktok_score x 0.15
)

---

### Component 3: Momentum Score (0–100) — Weight: 25%

"Is the timing right to act?"

Career trajectory data from Chartmetric. This is where we reward discovery
and penalize stagnation.

| Data Point | Source | Scaling | Notes |
|------------|--------|---------|-------|
| Remix artist `momentum` | CM `/artist/:id/career` | decline=15, gradual_decline=30, steady=45, growth=70, explosive_growth=95 | Primary momentum signal |
| Remix artist `momentum_score` | CM `/artist/:id/career` | Fine-tunes within category (0-100 within each band) | Granularity within momentum category |
| Stage gap | CM career for both artists | Maps career stages to 0-5 (undiscovered=0, legendary=5), then: gap = original - remix. gap>=3: +20, gap==2: +10, gap==1: +5, gap<=0: 0 | Rewards "developing artist remixes superstar" pattern |
| Mid-level + steady penalty | CM career for remix artist | If stage="mid-level" AND momentum in (steady, decline, gradual_decline): -15 | Industry reality: these deals rarely move the needle |

Momentum = remix_momentum_base + stage_gap_bonus + midlevel_penalty (clamped 0-100)

Where remix_momentum_base blends the category mapping with momentum_score for
sub-category positioning.

---

### Data Points Summary — All APIs

| API | Endpoint | Fields Used | Component |
|-----|----------|-------------|-----------|
| SoundCloud | `resolve`, `search/tracks` | playback_count, likes_count, reposts_count, comment_count, created_at | Demand |
| SoundCloud | derived | engagement_rate, daily_velocity, days_live | Demand |
| Chartmetric | `search` (artists) | sp_monthly_listeners, sp_followers, cm_artist_score, tiktok_followers | Conversion |
| Chartmetric | `search` (artists) | spotify_followers_to_listeners_ratio | Conversion |
| Chartmetric | `/artist/:id/where-people-listen` | cities (top 10 for each artist) | Conversion (geo divergence) |
| Chartmetric | `/artist/:id/career` | stage, stage_score, momentum, momentum_score | Momentum |
| Chartmetric | `search` (tracks), `/track/:id` | isrc, name, artist_names | Pipeline (ISRC resolution) |
| Chartmetric | `/artist/chartmetric/:id/get-ids` | spotify_artist_id, itunes_artist_id, deezer_artist_id | Pipeline (cross-platform) |
| Luminate | `/songs/:isrc`, `/musical_recordings/:isrc` | consumption metrics | Revenue calibration (when available) |
| Royalti.io | `/royalty/dsp`, `/royalty/country` | RatePer1K, revenue by platform/territory | Revenue model refinement |
| JamBase | `/artists/id/:id` | upcoming events, venue capacity | Report enrichment (not in score) |

---

## 2. Functions to Build — Shared Components

These are the reusable building blocks needed across all five user journey options.

### Layer 2: Per-Track Analysis Engine

Functions that take a single SoundCloud track and produce a full evaluation.

```
models.py — new functions:
    compute_demand_score(sc_metrics) -> int
    compute_conversion_score(original_cm, remix_cm, original_geo, remix_geo) -> int
    compute_momentum_score(original_career, remix_career) -> int
    compute_opportunity_score(demand, conversion, momentum) -> dict
    generate_recommendation(score, revenue, geo_data) -> str

pipeline.py — refactored functions:
    enrich_artist(cm, name) -> dict
        Reusable enrichment for ANY artist (original or remix).
        Currently only runs for original artist.
        Returns: cm_id, search_result, metadata, career, geo, platform_ids

    analyze_track(sc, cm, sc_url_or_track) -> dict
        Full per-track analysis producing a standardized TrackReport.
        Calls: sc.resolve -> parse_title -> enrich_artist (x2) -> score -> revenue
        Returns: TrackReport dict (see below)
```

### TrackReport — Standard Output Schema

Every user journey option produces one or more of these:

```
TrackReport:
    sc_track:           raw SC track object
    sc_metrics:         plays, likes, reposts, comments, engagement_rate, velocity, days_live
    parsed_title:       original_artist, original_song, remix_artist
    original_artist:    cm_id, name, sp_followers, sp_monthly_listeners, career, geo, platform_ids
    remix_artist:       cm_id, name, sp_followers, sp_monthly_listeners, career, geo, platform_ids
    original_isrc:      ISRC from Chartmetric track search (if found)
    luminate_data:      consumption data (if available)
    opportunity_score:  overall (0-100), demand, conversion, momentum
    revenue:            conservative/mid/optimistic projections
    viability:          clears_threshold, recommendation text
    geo_insight:        top crossover cities, overlap percentage
```

### Layer 2b: Remix Artist Enrichment

```
platforms/chartmetric.py — new method:
    get_artist_career(cm_id) -> dict
        Calls /artist/:id/career
        Returns: stage, stage_score, momentum, momentum_score

pipeline.py:
    enrich_artist() already works for original artist.
    Call it again for remix artist.
    Add career endpoint call to enrichment flow.
```

### Layer 3: Scoring & Revenue

```
models.py — new functions:
    compute_demand_score(sc_metrics) -> int (0-100)
    compute_conversion_score(original_cm, remix_cm, original_geo, remix_geo) -> int (0-100)
    compute_momentum_score(original_career, remix_career) -> int (0-100)
    compute_opportunity_score(demand, conversion, momentum) -> dict
        Returns: {overall, demand, conversion, momentum, label, recommendation}
    compute_geo_divergence(cities_a, cities_b) -> float (0-1)
        Jaccard distance on top-10 city sets
```

### Layer 4: Output & Reporting

```
reporting.py — new module:
    format_track_report(report) -> str
        Human-readable single-track report (what pipeline.py currently prints)
    format_summary_table(reports) -> str
        Ranked table of multiple TrackReports for Options 1-4
    export_detail_sheet(report) -> dict
        Structured data for UI rendering or CSV/JSON export
    generate_licensing_pitch(report) -> str
        Formatted text for rights negotiation
```

---

## 3. Functions to Build — Per User Journey Option

### Option 5: Individual SC Link (priority: HIGH — demo path)

```
Already works. Additions needed:
    - enrich_artist() for REMIX artist (not just original)
    - get_artist_career() for both artists
    - compute_opportunity_score()
    - generate_recommendation() with geo insight text
    - format_track_report() with score display

Entry point: python -m scripts.pipeline "https://soundcloud.com/..."
```

### Option 3: Song Search (priority: HIGH)

```
New function in pipeline.py:
    search_song_remixes(song_name, artist_name=None, limit=20) -> list[TrackReport]
        1. sc.search_remixes(song_name, artist=artist_name)
        2. For each result: analyze_track()
        3. Sort by opportunity_score descending
        4. Return ranked list

Entry point: python -m scripts.pipeline --song "Blinding Lights" --artist "The Weeknd"
```

### Option 2: Artist Search (priority: MEDIUM)

```
New function in pipeline.py:
    search_artist_remixes(artist_name, limit_songs=10, limit_remixes=10) -> list[TrackReport]
        1. cm.find_artist(artist_name)
        2. Get artist's top tracks from Chartmetric (or search SC for "{artist}" tracks)
        3. For each track: search_song_remixes(track_name, artist_name)
        4. Flatten, deduplicate, sort by opportunity_score
        5. Return ranked list

Entry point: python -m scripts.pipeline --artist "The Weeknd"

Depends on: Chartmetric artist tracks endpoint or SC user tracks
```

### Option 4: Filtered Discovery (priority: MEDIUM)

```
New function in pipeline.py:
    discover_remixes(genre=None, min_plays=None, created_after=None, limit=50) -> list[TrackReport]
        1. sc.search_tracks("remix", genre=genre, created_after=created_after, limit=limit)
        2. Filter by min_plays
        3. For each result: analyze_track()
        4. Sort by opportunity_score descending

Entry point: python -m scripts.pipeline --discover --genre "Deep House" --min-plays 50000

Future: Add Chartmetric career_stage and region filters via CM A&R endpoints
```

### Option 1: Catalog Bulk Upload (priority: LOW)

```
New module: catalog.py
    parse_catalog_file(filepath) -> list[dict]
        Accepts CSV or XML
        Extracts: song_title, artist_name, isrc (if available)
        Returns list of {title, artist, isrc}

    process_catalog(filepath, limit_remixes=5) -> list[TrackReport]
        1. parse_catalog_file()
        2. For each song: search_song_remixes()
        3. Flatten, deduplicate, sort by opportunity_score
        4. Return ranked list + summary stats

Entry point: python -m scripts.pipeline --catalog catalog.csv
```

---

## 4. CLI Interface Plan

Unified entry point via pipeline.py with argparse:

```
python -m scripts.pipeline URL                           # Option 5 (current)
python -m scripts.pipeline --song "Title" [--artist "X"] # Option 3
python -m scripts.pipeline --artist "Name"               # Option 2
python -m scripts.pipeline --discover [--genre G] [--min-plays N]  # Option 4
python -m scripts.pipeline --catalog file.csv            # Option 1
```

All options produce TrackReport(s) and use the same scoring/reporting layer.

---

## 5. Build Order

1. `get_artist_career()` in chartmetric.py
2. `enrich_artist()` refactor in pipeline.py (reusable for both artists)
3. Scoring functions in models.py (demand, conversion, momentum, opportunity)
4. `compute_geo_divergence()` in models.py
5. Update pipeline.py Option 5 with dual-artist enrichment + scoring
6. `reporting.py` — format_track_report, format_summary_table
7. `search_song_remixes()` — Option 3
8. CLI argparse — unified entry point
9. `search_artist_remixes()` — Option 2
10. `discover_remixes()` — Option 4
11. `catalog.py` — Option 1

Steps 1–6 complete the demo path (Option 5 with full scoring).
Steps 7–8 unlock Option 3 (most likely second demo scenario).
Steps 9–11 are stretch goals.
