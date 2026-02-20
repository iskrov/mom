# Assets (Tracks / Recordings)

An asset is a track or recording, identified by ISRC.

## GET `/asset` - List Assets

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| search | String | - | Search term |
| type | String | - | Filter by type (`Audio`, `Video`, `Ringtone`, `YouTube`) |
| artist | String | - | Filter by artist UUID(s) |
| product | String | - | Filter by product ID |
| statistics | Boolean | false | Include count/royalty stats |
| splits | Boolean | false | Include splits data |
| sort | String | `createdAt` | Sort field |
| order | String | `desc` | `asc` or `desc` |
| attributes | String | - | Comma-separated fields to return |
| page | Integer | 1 | Page number |
| size | Integer | 10 | Items per page |

**Sort fields:** `updatedAt`, `createdAt`, `title`, `isrc`, `displayArtist`, `type`. With `statistics=true`: also `splits`, `products`, `count`, `royalty`

---

## GET `/asset/{id}` - Get Asset

**Path:** `id` (UUID)

---

## POST `/asset` - Create Asset

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| title | String | Track title |
| mainArtist | String[] | Main artist display names |
| displayArtist | String | Display artist (max 510 chars) |

**Optional Fields - Core Metadata:**

| Field | Type | Description |
|-------|------|-------------|
| type | String | `Audio`, `Video`, `Ringtone`, `YouTube` (default: `Audio`) |
| otherArtist | String[] | Featured artist names |
| version | String | Version (e.g., "Remix", "Live") |
| isrc | String | ISRC (pattern: `^[A-Z]{2}[A-Z0-9]{3}[0-9]{2}[0-9]{5}$`). Auto-generated if omitted |
| iswc | String | ISWC (pattern: `^T-\d{9}-\d$`) |
| lyrics | String | Full lyrics |
| mainGenre | String[] | Primary genres |
| subGenre | String[] | Sub-genres |
| contributors | Object | `{ producers: [], mixers: [], songwriters: [], ... }` |
| externalId | String | External system ID |
| explicit | String | `explicit` or `clean` |
| label | String | Record label |
| copyright | String | Copyright info |
| publisher | String | Publisher |
| copyrightOwner | String | Copyright owner |
| language | String | Language code |
| mood | String[] | Mood tags |
| tempo | Number | BPM |
| key | String | Musical key (e.g., `"C Major"`) |
| productionYear | Integer | Year of production |
| recordingLocation | String | Studio/location |
| recordingDate | Date | Recording date |
| alternativeTitles | String[] | Alt titles |
| chartPositions | Object[] | `[{ chart, position, date }]` |
| awards | Object[] | `[{ name, year }]` |
| socialMediaHandles | Object | `{ twitter: "@handle", ... }` |

**Optional Fields - DDEX:**

| Field | Type | Description |
|-------|------|-------------|
| enableDDEX | Boolean | Enable DDEX for this asset |
| ddexMetadata | Object | DDEX-specific metadata |
| technicalResourceDetails | Object | `{ fileFormat, audioCodec, bitrate, sampleRate, duration }` |
| soundRecordingDetails | Object | `{ recordingDate, recordingLocation, language }` |
| musicalWorkReference | Object | `{ workId, iswc }` |
| focusTrack | Boolean | MEAD focus track flag |
| danceStyle | String[] | MEAD dance styles |
| rhythmStyle | String[] | MEAD rhythm styles |
| instrumentation | String[] | MEAD instrumentation |

**Optional Fields - Relationships:**

| Field | Type | Description |
|-------|------|-------------|
| artists | Array | UUIDs or `[{ id, type: "primary"/"featuring" }]` |
| split | Object[] | `[{ user: UUID, share: Number }]` (must sum to 100) |

---

## GET `/asset/{id}/stats` - Asset Statistics

Returns statistics about the asset's royalty performance.

---

## Other Asset Endpoints

| Method | Path | Description |
|--------|------|-------------|
| PUT | `/asset/{id}` | Update asset |
| DELETE | `/asset/{id}` | Delete asset |
| GET | `/asset/{id}/works` | Works for a recording |
| POST | `/asset/{id}/media` | Upload media |
| DELETE | `/asset/{id}/media` | Delete media |
| PUT | `/asset/{id}/artists` | Update artists |
| PUT | `/asset/{id}/default-split` | Set default split |
| POST | `/asset/bulk` | Bulk create |
| DELETE | `/asset/bulk` | Bulk delete |
| PUT | `/asset/bulk/splits` | Set bulk splits |
| DELETE | `/asset/bulk/splits` | Delete bulk splits |
| PUT | `/asset/bulk/default-split` | Set default split for multiple |
| GET | `/asset/download` | CSV export |
