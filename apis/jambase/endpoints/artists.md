# Artists

## GET `/artists` - Search Artists

**Requirement:** Must include at least one of `artistName` or `genreSlug`.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | Integer | 1 | Page number |
| perPage | Integer | 40 | Results per page (max: 100) |
| artistName | String | - | **Required** (or genreSlug). Name keyword(s) |
| genreSlug | String | - | **Required** (or artistName). Genre(s), pipe-delimited |
| artistHasUpcomingEvents | Boolean | - | Only artists with upcoming events |
| dateModifiedFrom | DateTime | - | Updated-since filter |
| datePublishedFrom | DateTime | - | Published-since filter |
| expandExternalIdentifiers | Boolean | false | Include Spotify/MusicBrainz IDs |

**MusicGroup / Person object:**

| Field | Type | Description |
|-------|------|-------------|
| @type | String | `"MusicGroup"` or `"Person"` |
| name | String | Artist/band name |
| identifier | String | `source:id` format |
| url | String | JamBase artist page |
| image | String | Artist image URL |
| genre | String[] | Genre slugs |
| foundingLocation | Object | Hometown (city, state, country) |
| foundingDate | String | Year first performed (ISO 8601) |
| member | Array | Band members (array of Person objects) |
| memberOf | Array | Bands this musician belongs to |
| sameAs | Array | External links (see URL types below) |
| x-bandOrMusician | String | `band` or `musician` |
| x-numUpcomingEvents | Number | Count of upcoming events |
| x-externalIdentifiers | Array | Cross-platform IDs (when expanded) |
| datePublished | String | First published |
| dateModified | String | Last updated |

**URL link types in `sameAs`:**

`officialSite`, `facebook`, `twitter`, `instagram`, `youtube`, `musicbrainz`, `spotify`, `androidApp`, `iosApp`

---

## GET `/artists/id/{artistDataSource}:{artistId}` - Get Artist

Retrieve a specific artist with optional event expansion.

**Path Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| artistDataSource | String | yes | Source slug |
| artistId | String | yes | Artist ID |

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| expandUpcomingEvents | Boolean | false | Include upcoming concerts/festivals |
| expandUpcomingStreams | Boolean | false | Include upcoming streams |
| expandPastEvents | Boolean | false | Include historical events (requires key enhancement) |
| excludeEventPerformers | Boolean | false | Suppress performer data in events |
| expandExternalIdentifiers | Boolean | false | Include cross-platform IDs |

**With events expanded**, the artist object includes an `events` array of Concert/Festival/Stream objects.

---

## Artist Data Sources

`axs`, `dice`, `etix`, `eventbrite`, `eventim-de`, `jambase`, `seated`, `seatgeek`, `spotify`, `ticketmaster`, `viagogo`, `musicbrainz`

**External Identifier examples:**
- Spotify: `spotify:4Z8W4fKeB5YxbusRsdQl1z`
- MusicBrainz: `musicbrainz:a74b1b7f-71a5-4011-9441-d0b5e4122711`
- Ticketmaster: `ticketmaster:K8vZ917GdV0`
