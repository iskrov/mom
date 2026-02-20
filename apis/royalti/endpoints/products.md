# Products (Albums / Singles / EPs)

A product is a commercial release identified by UPC. Format is auto-determined by track count (Single, EP, Album, LP).

## GET `/product/` - List Products

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| q | String | - | Search query |
| artist | String | - | Filter by artist ID(s), comma-separated |
| type | String | - | Filter by type |
| asset | String | - | Filter by asset ID |
| user | String | - | Filter by user ID |
| role | String | - | Filter by role |
| statistics | Boolean | false | Include count/royalty stats |
| splits | Boolean | false | Include splits info |
| sort | String | `updatedAt` | Sort field |
| order | String | `desc` | `asc` or `desc` |
| attributes | String | - | Comma-separated fields |
| page | Integer | 1 | Page number |
| size | Integer | 10 | Items per page |

**Sort fields:** `updatedAt`, `createdAt`, `title`, `upc`, `releaseDate`, `catalogNumber`, `displayArtist`. With `statistics=true`: also `splits`, `assets`, `count`, `royalty`

**Response includes:** `id`, `title`, `upc`, `displayArtist`, `type`, `format`, `label`, `releaseDate`, `takedownDate`, `status`, `distribution`, `mainGenre`, `subGenre`, `explicit`, nested `Artists` and `ProductAssets` arrays.

---

## GET `/product/{id}` - Get Product

Full product with artists, assets (tracklist), splits, media, and metadata.

---

## POST `/product/` - Create Product

**Required:** `title` (1-255 chars)

**Optional Fields:**

| Field | Type | Description |
|-------|------|-------------|
| upc | String | UPC (12 digits, auto-generated if omitted) |
| catalogNumber | String | Catalog number |
| externalId | String | External ID |
| displayArtist | String | Display artist name |
| type | String | `Audio`, `Video`, `Ringtone` (default: `Audio`) |
| format | String | Auto-determined: `Single`, `EP`, `Album`, `LP` |
| version | String | Version label |
| explicit | String | `explicit` or `clean` |
| releaseDate | Date | Release date |
| takedownDate | Date | Takedown date |
| originalReleaseDate | Date | For reissues |
| mainGenre | String | Primary genre |
| subGenre | String | Sub-genre |
| status | String | `Live`, `Taken Down`, `Scheduled`, `Pending`, `Error` (default: `Pending`) |
| distribution | Object | Distribution settings |
| language | String | ISO 639-1 code |
| label | String | Record label |
| c_line_year | Integer | Copyright line year (1900-2100) |
| p_line_year | Integer | Phonogram line year (1900-2100) |
| totalTracks | Integer | Track count |
| totalDiscs | Integer | Disc count |
| packageType | String | Package type |
| edition | String | Edition |
| reissue | Boolean | Is reissue (default: false) |
| recordingLocation | String | Studio |
| masteringLocation | String | Mastering studio |
| producer | String[] | Producers |
| engineer | String[] | Engineers |
| contributors | Object[] | `[{ name, role, share? }]` |
| artists | Array | UUIDs or `[{ id, type }]` |
| assets | Array | `[{ asset: UUID, number: trackNumber }]` |
| chartHistory | Object[] | `[{ chart, position, date }]` |

---

## GET `/product/{id}/stats` - Product Stats

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| totalRoyalties | Number | Total earned |
| totalPaid | Number | Paid out |
| totalDue | Number | Outstanding |
| totalStreams | Integer | Total streams |
| totalSales | Integer | Total sales |
| assetCount | Integer | Tracks in product |

---

## Other Product Endpoints

| Method | Path | Description |
|--------|------|-------------|
| PUT | `/product/{id}` | Update product |
| DELETE | `/product/{id}` | Delete product |
| POST | `/product/{id}/media` | Upload media |
| DELETE | `/product/{id}/media` | Delete media |
| PUT | `/product/{id}/artists` | Update artists |
| PUT | `/product/{id}/assets` | Update tracklist |
| PUT | `/product/{id}/default-split` | Set default split |
| POST | `/product/bulk` | Bulk create |
| DELETE | `/product/bulk` | Bulk delete |
| PUT | `/product/bulk/splits` | Bulk update splits |
| DELETE | `/product/bulk/splits` | Bulk delete splits |
| GET | `/product/download` | CSV export |
| GET | `/product/{id}/metadata` | Download metadata |
