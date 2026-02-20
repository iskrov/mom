# JamBase API - Quick Reference

All paths relative to `https://www.jambase.com/jb-api/v1`. All requests require `?apikey=KEY` and `User-Agent` header.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/events` | Search concerts & festivals |
| GET | `/events/id/{source}:{id}` | Get event by ID |
| GET | `/streams` | Search upcoming livestreams |
| GET | `/streams/id/{source}:{id}` | Get stream by ID |
| GET | `/artists` | Search artists (requires `artistName` or `genreSlug`) |
| GET | `/artists/id/{source}:{id}` | Get artist by ID (optionally with events) |
| GET | `/venues` | Search venues (requires `venueName` or geo param) |
| GET | `/venues/id/{source}:{id}` | Get venue by ID (optionally with events) |
| GET | `/geographies/cities` | Search cities |
| GET | `/geographies/metros` | List metro areas |
| GET | `/geographies/states` | List states/provinces |
| GET | `/geographies/countries` | List countries |
| GET | `/genres` | List all genres |
| GET | `/lookups/event-data-sources` | Event data sources |
| GET | `/lookups/stream-data-sources` | Stream data sources |
| GET | `/lookups/artist-data-sources` | Artist data sources |
| GET | `/lookups/venue-data-sources` | Venue data sources |

## Common Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | Integer | Page number (default: 1) |
| `perPage` | Integer | Results per page (default: 40, max: 100) |
| `expandExternalIdentifiers` | Boolean | Include Spotify/MusicBrainz/ticketing IDs |
| `expandArtistSameAs` | Boolean | Include artist social/web links |
| `expandPastEvents` | Boolean | Include historical events |
| `expandUpcomingEvents` | Boolean | Include upcoming events (artist/venue) |
| `excludeEventPerformers` | Boolean | Omit performer data from events |
| `dateModifiedFrom` | DateTime | Updated-since filter (GMT) |
| `datePublishedFrom` | DateTime | Published-since filter (GMT) |

## Geo Parameters (events + venues)

| Parameter | Type | Description |
|-----------|------|-------------|
| `geoLatitude` + `geoLongitude` | Number | Coordinate search |
| `geoRadiusAmount` | Number | Radius (default: 60, max: 5000) |
| `geoRadiusUnits` | String | `mi` (default) or `km` |
| `geoIp` | String | IPv4/IPv6 for geo lookup |
| `geoMetroId` | String | Metro ID (`jambase:N`) |
| `geoCityId` | String | City ID (`jambase:N`) |
| `geoStateIso` | String | State code (`US-NY`) |
| `geoCountryIso2` | String | Country code (`US`) |

## ID Format

All IDs use `source:id` format. Example: `jambase:228924`, `spotify:4Z8W4fKeB5YxbusRsdQl1z`

## Data Sources

**Events:** `axs`, `dice`, `etix`, `eventbrite`, `eventim-de`, `jambase`, `seated`, `see-tickets`, `see-tickets-uk`, `sofar-sounds`, `seatgeek`, `suitehop`, `ticketmaster`, `tixr`, `viagogo`

**Artists:** `axs`, `dice`, `etix`, `eventbrite`, `eventim-de`, `jambase`, `seated`, `seatgeek`, `spotify`, `ticketmaster`, `viagogo`, `musicbrainz`

**Venues:** `axs`, `dice`, `etix`, `eventbrite`, `eventim-de`, `jambase`, `seated`, `seatgeek`, `suitehop`, `ticketmaster`, `viagogo`

## Date Presets

`today`, `tomorrow`, `thisWeekend`, `nextWeekend`, `halloween`, `newYears`, `july4th`
