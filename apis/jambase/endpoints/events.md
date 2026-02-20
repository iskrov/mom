# Events

## GET `/events` - Search Events

Search concerts and festivals by location, date, artist, genre, and more. Returns an array of `Concert` and `Festival` objects.

**Query Parameters - Pagination:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | Integer | 1 | Page number |
| perPage | Integer | 40 | Results per page (min: 1, max: 100) |

**Query Parameters - Event Filters:**

| Name | Type | Description |
|------|------|-------------|
| eventType | String | `concerts` or `festivals` |
| artistId | String | Artist ID(s), pipe-delimited. Format: `source:id`. Example: `jambase:228924` |
| artistName | String | Artist name keyword(s), pipe-delimited |
| genreSlug | String | Genre(s), pipe-delimited. See [genres.md](genres.md) for values |
| venueId | String | Venue ID(s), pipe-delimited. Format: `source:id` |
| venueName | String | Venue name keyword(s), pipe-delimited |
| eventDataSource | String | Filter by ticketing source (see data sources below) |

**Query Parameters - Date Filters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| eventDateFrom | String | today | Start date (`YYYY-MM-DD`) |
| eventDateTo | String | - | End date (`YYYY-MM-DD`) |
| eventDatePreset | String | - | Overrides date range. Values: `today`, `tomorrow`, `thisWeekend`, `nextWeekend`, `halloween`, `newYears`, `july4th` |

**Query Parameters - Geography:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| geoLatitude | Number | - | Latitude (-90 to 90) |
| geoLongitude | Number | - | Longitude (-180 to 180) |
| geoRadiusAmount | Number | 60 | Radius (min: 1, max: 5000) |
| geoRadiusUnits | String | `mi` | `mi` or `km` |
| geoIp | String | - | IP address for geo lookup |
| geoMetroId | String | - | Metro ID (`jambase:N`) |
| geoCityId | String | - | City ID (`jambase:N`) |
| geoStateIso | String | - | State/province code (`US-NY`). US, CA, AU supported |
| geoCountryIso2 | String | - | 2-letter country code |
| geoCountryIso3 | String | - | 3-letter country code |

**Query Parameters - Data Enrichment:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| expandExternalIdentifiers | Boolean | false | Include Spotify/MusicBrainz/ticketing IDs (requires key enhancement) |
| expandArtistSameAs | Boolean | false | Include artist social/web links |
| expandPastEvents | Boolean | false | Include past events (requires `artistId` or `venueId`) |
| excludeEventPerformers | Boolean | false | Suppress performer data |
| dateModifiedFrom | DateTime | - | Updated-since filter (GMT) |
| datePublishedFrom | DateTime | - | Published-since filter (GMT) |

**Response:**

```json
{
  "success": true,
  "pagination": {
    "page": 1,
    "perPage": 40,
    "totalItems": 1250,
    "totalPages": 32,
    "nextPage": "https://...",
    "previousPage": null
  },
  "events": [...]
}
```

**Concert object:**

| Field | Type | Description |
|-------|------|-------------|
| @type | String | `"Concert"` |
| name | String | Event title |
| identifier | String | `jambase:NNNNN` |
| url | String | JamBase event page URL |
| image | String | Event image URL |
| eventStatus | String | `scheduled`, `postponed`, `rescheduled`, `cancelled` |
| startDate | String | ISO 8601 datetime (venue local time) |
| endDate | String | ISO 8601 datetime |
| doorTime | String | ISO 8601 datetime |
| previousStartDate | String | Original date (if rescheduled) |
| location | MusicVenue | Venue object (see [venues.md](venues.md)) |
| performer | Array | Array of MusicGroup/Person objects |
| offers | Array | Ticket offers (see below) |
| eventAttendanceMode | String | `mixed`, `offline`, `online` |
| isAccessibleForFree | Boolean | Free event |
| x-promoImage | String | Promotional image URL |
| x-customTitle | String | Override event name |
| x-subtitle | String | Supplementary title |
| x-headlinerInSupport | Boolean | Headliner is supporting act |
| x-streamIds | String[] | Associated stream IDs |
| x-externalIdentifiers | Array | Cross-platform IDs (when expanded) |
| sameAs | Array | External link URLs |
| datePublished | String | First published (ISO 8601) |
| dateModified | String | Last updated (ISO 8601) |

**Festival object** - same as Concert plus:

| Field | Type | Description |
|-------|------|-------------|
| @type | String | `"Festival"` |
| endDate | String | Multi-day end date (required) |
| x-lineupDisplayOption | String | `full` or `daybyday` |

**Offer (ticket) object:**

| Field | Type | Description |
|-------|------|-------------|
| identifier | String | Offer ID |
| url | String | Purchase link |
| category | String | Primary vs secondary ticket |
| seller | Object | `{ name, identifier }` |
| validFrom | String | When offer becomes available |
| priceSpecification.minPrice | Number | Minimum price |
| priceSpecification.maxPrice | Number | Maximum price |
| priceSpecification.price | Number | Single price or min |
| priceSpecification.priceCurrency | String | ISO 4217 currency code |

---

## GET `/events/id/{eventDataSource}:{eventId}` - Get Event

Retrieve a specific event by its ID from any supported data source.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| eventDataSource | String | yes | Source slug (e.g., `jambase`, `ticketmaster`, `viagogo`) |
| eventId | String | yes | Event ID from that source |

**Query Parameters:** `expandExternalIdentifiers`, `expandArtistSameAs`

**Example:** `GET /events/id/jambase:10323546?apikey=KEY`

---

## Event Data Sources

`axs`, `dice`, `etix`, `eventbrite`, `eventim-de`, `jambase`, `seated`, `see-tickets`, `see-tickets-uk`, `sofar-sounds`, `seatgeek`, `suitehop`, `ticketmaster`, `tixr`, `viagogo`
