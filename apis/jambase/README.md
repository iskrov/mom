# JamBase API

Live music event database covering concerts, festivals, streams, artists, and venues. Schema.org-compliant JSON responses with custom extensions.

- **Base URL:** `https://www.jambase.com/jb-api/v1`
- **Mock Server:** `https://stoplight.io/mocks/jambase/jambase-api/118239274`
- **Docs:** https://apidocs.jambase.com
- **Format:** JSON (Schema.org-based)
- **API Version:** 1.0.0
- **Contact:** developer@jambase.com

## Authentication

API key passed as query parameter on every request.

```bash
curl "https://www.jambase.com/jb-api/v1/events?apikey=YOUR_API_KEY"
```

- Keys obtained by contacting JamBase: https://www.jambase.com/concert-api#contact
- `User-Agent` header is **required** on all requests
- Key expiration tracked via `x-jb-api-key-expires-on` response header

## Rate Limits

| Plan | Limit |
|------|-------|
| Standard | 3,600 calls/hour (~1/sec) |
| Extended | 36,000 calls/hour (paid) |

- Track remaining via `x-jb-api-requests-remaining` response header
- HTTP 429 = rate limited (`"code": "rate_limit_exceeded"`)
- HTTP 403 = expired key (`"code": "api_key_expired"`)

## Data Coverage

| Entity | Scale |
|--------|-------|
| Artists/bands | 400,000+ |
| Venues | 170,000+ |
| Upcoming events | 100,000+ |
| Historical events | 3,000,000+ (since 1999) |
| Countries | US, CA, AU, DE + more |

## Data Model

All entities inherit from a Schema.org `Thing` base and use `x-` prefixed custom extensions.

```
Event (base)
  ├── Concert  (type: "Concert")
  ├── Festival (type: "Festival", multi-day, lineup display)
  └── Stream   (type: "Stream", live broadcasts)

MusicGroup / Person (artist entities)
  ├── genre[], member[], memberOf[]
  ├── foundingLocation, foundingDate
  └── x-externalIdentifiers (Spotify, MusicBrainz, etc.)

MusicVenue
  ├── address (PostalAddress with timezone, metro/city IDs)
  ├── geo (GeoCoordinates - lat/lng)
  └── maximumAttendeeCapacity

Offer (ticket data per event)
  ├── seller, url (purchase link)
  └── priceSpecification (min/max price, currency)
```

## Key Features

- **Multi-source data**: 15+ ticketing sources (Ticketmaster, SeatGeek, AXS, Dice, Eventbrite, Viagogo, etc.)
- **Rich geo search**: by lat/lng + radius, IP address, metro, city, state, country
- **Cross-platform IDs**: Spotify, MusicBrainz, ticketing platform IDs via `expandExternalIdentifiers`
- **Date presets**: `today`, `tomorrow`, `thisWeekend`, `nextWeekend`, `halloween`, `newYears`, `july4th`
- **Historical data**: past events accessible via `expandPastEvents`
- **Livestream support**: dedicated stream endpoints with broadcast-of-event linking

## Genres

`bluegrass`, `blues`, `christian`, `classical`, `country-music`, `edm`, `folk`, `hip-hop-rap`, `indie`, `jamband`, `jazz`, `latin`, `metal`, `pop`, `punk`, `reggae`, `rhythm-and-blues-soul`, `rock`

## Endpoint Categories

| Category | Endpoints | Description |
|----------|-----------|-------------|
| [Events](endpoints/events.md) | 2 | Search concerts/festivals + get by ID |
| [Streams](endpoints/streams.md) | 2 | Search livestreams + get by ID |
| [Artists](endpoints/artists.md) | 2 | Search artists + get by ID (with events) |
| [Venues](endpoints/venues.md) | 2 | Search venues + get by ID (with events) |
| [Geographies](endpoints/geographies.md) | 4 | Cities, metros, states, countries |
| [Genres](endpoints/genres.md) | 1 | List all genres |
| [Lookups](endpoints/lookups.md) | 4 | Available data sources per entity type |

**Total: 17 endpoints**

See [quick-reference.md](quick-reference.md) for a compact endpoint table.
