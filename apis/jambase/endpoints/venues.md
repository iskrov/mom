# Venues

## GET `/venues` - Search Venues

**Requirement:** Must include `venueName` or at least one geo parameter.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | Integer | 1 | Page number |
| perPage | Integer | 40 | Results per page (max: 100) |
| venueName | String | - | Venue name keyword(s), pipe-delimited |
| venueHasUpcomingEvents | Boolean | - | Only venues with upcoming events |
| dateModifiedFrom | DateTime | - | Updated-since filter |
| datePublishedFrom | DateTime | - | Published-since filter |
| expandExternalIdentifiers | Boolean | false | Include external IDs |

**Geo Parameters (same as events):**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| geoLatitude | Number | - | Latitude (-90 to 90) |
| geoLongitude | Number | - | Longitude (-180 to 180) |
| geoRadiusAmount | Number | 60 | Radius (min: 1, max: 5000) |
| geoRadiusUnits | String | `mi` | `mi` or `km` |
| geoIp | String | - | IP address for geo lookup |
| geoMetroId | String | - | Metro ID |
| geoCityId | String | - | City ID |
| geoStateIso | String | - | State code (e.g., `US-NY`) |
| geoCountryIso2 | String | - | 2-letter country code |
| geoCountryIso3 | String | - | 3-letter country code |

**MusicVenue object:**

| Field | Type | Description |
|-------|------|-------------|
| @type | String | `"MusicVenue"` |
| name | String | Venue name |
| identifier | String | `source:id` |
| url | String | JamBase venue page |
| image | String | Venue image URL |
| maximumAttendeeCapacity | Number | Venue capacity |
| address | PostalAddress | Full address (see below) |
| geo | GeoCoordinates | `{ latitude, longitude }` |
| x-isPermanentlyClosed | Boolean | Permanently closed |
| x-numUpcomingEvents | Number | Count of upcoming events |
| x-externalIdentifiers | Array | Cross-platform IDs |
| events | Array | Events (when expanded) |
| datePublished | String | First published |
| dateModified | String | Last updated |

**PostalAddress object:**

| Field | Type | Description |
|-------|------|-------------|
| @type | String | `"PostalAddress"` |
| streetAddress | String | Street address |
| x-streetAddress2 | String | Unit/suite |
| addressLocality | String | City name |
| postalCode | String | Postal/ZIP code |
| addressRegion | Object | State/province (name, identifier, iso) |
| addressCountry | Object | Country (name, identifier, iso2, iso3) |
| x-timezone | String | tz database timezone (e.g., `America/New_York`) |
| x-jamBaseMetroId | Number | JamBase metro area ID |
| x-jamBaseCityId | Number | JamBase city ID |

---

## GET `/venues/id/{venueDataSource}:{venueId}` - Get Venue

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| venueDataSource | String | yes | Source slug |
| venueId | String | yes | Venue ID |

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| expandUpcomingEvents | Boolean | false | Include upcoming events |
| excludeEventPerformers | Boolean | false | Suppress performer data |
| expandExternalIdentifiers | Boolean | false | Include cross-platform IDs |
| expandArtistSameAs | Boolean | false | Include artist links |

---

## Venue Data Sources

`axs`, `dice`, `etix`, `eventbrite`, `eventim-de`, `jambase`, `seated`, `seatgeek`, `suitehop`, `ticketmaster`, `viagogo`
