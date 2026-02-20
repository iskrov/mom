# Streams (Livestreams)

## GET `/streams` - Search Streams

Search upcoming livestreams by date, artist, genre, and data source.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | Integer | 1 | Page number |
| perPage | Integer | 40 | Results per page (max: 100) |
| eventDatePreset | String | - | Date preset: `today`, `tomorrow`, `thisWeekend`, etc. |
| eventDateFrom | String | today | Start date (`YYYY-MM-DD`) |
| eventDateTo | String | - | End date (`YYYY-MM-DD`) |
| streamDataSource | String | - | Filter by stream platform |
| dateModifiedFrom | DateTime | - | Updated-since filter |
| datePublishedFrom | DateTime | - | Published-since filter |
| expandExternalIdentifiers | Boolean | false | Include external IDs |
| expandArtistSameAs | Boolean | false | Include artist links |

**Stream object:**

| Field | Type | Description |
|-------|------|-------------|
| @type | String | `"Stream"` |
| name | String | Stream title |
| identifier | String | `source:id` |
| url | String | Stream page URL |
| eventStatus | String | `scheduled`, `postponed`, `rescheduled`, `cancelled` |
| startDate | String | ISO 8601 datetime |
| isLiveBroadcast | Boolean | Is this a live broadcast |
| location | MusicVenue | Venue (if applicable) |
| performer | Array | Artist lineup |
| broadcastOfEvent | Array | Linked Concert/Festival being broadcast |
| x-customTitle | String | Override title |
| offers | Array | Ticket/access offers |

---

## GET `/streams/id/{streamDataSource}:{streamId}` - Get Stream

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| streamDataSource | String | yes | Source slug |
| streamId | String | yes | Stream ID |

**Query Parameters:** `expandExternalIdentifiers`, `expandArtistSameAs`
