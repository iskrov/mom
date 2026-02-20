# Artists

## GET `/artist/` - List Artists

Paginated, sortable, filterable artist list.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| q | String | - | Keyword search |
| artistName | String | - | Filter by name |
| externalId | String | - | Filter by external ID |
| page | Integer | 1 | Page number |
| size | Integer | 10 | Items per page |
| sort | String | `updatedAt` | Sort field |
| order | String | `desc` | `asc` or `desc` |
| statistics | Boolean | false | Include stats (royalties, counts) |
| catalog | Boolean | false | Include catalog info |
| user | String | - | Filter by user ID |
| attributes | String | - | Comma-separated field names to return |

**Sort fields:** `updatedAt`, `createdAt`, `artistName`, `externalId`, `assets`, `products`, `count`, `royalty`

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Artist identifier |
| artistName | String | Display name |
| realName | String | Real name |
| pseudonyms | String[] | Alternative names |
| signDate | Date | Date signed |
| label | String | Record label |
| publisher | String | Publisher |
| copyright | String | Copyright info |
| externalId | String | External system ID |
| artistImg | URL | Profile image |
| links | Object | Social/web URLs (key-value) |
| contributors | Object | Contributor details |
| genres | String[] | Music genres |
| instruments | String[] | Instruments |
| nationality | String | Country |
| gender | String | Gender |
| biography | String | Bio text |
| influences | String[] | Musical influences |
| activeYears | String | Years active |
| associatedActs | String[] | Related acts |
| birthDate | Date | Date of birth |
| birthPlace | String | Place of birth |
| chartHistory | Object[] | Chart performance records |
| socialMediaVerified | Object | Verified status per platform |
| website | URL | Official website |
| fanClubUrl | URL | Fan club URL |
| managementInfo | Object | Management contacts |
| bookingInfo | Object | Booking contacts |
| TenantId | Integer | Workspace ID |

---

## GET `/artist/{id}` - Get Artist

Returns artist with associated users and splits.

**Path:** `id` (UUID) - Artist ID

**Response includes:** `users` (associated users) and `split` (revenue split config)

---

## POST `/artist/` - Create Artist

**Required Body Fields:**

| Field | Type | Description |
|-------|------|-------------|
| artistName | String | Artist name |
| signDate | Date | Sign date (YYYY-MM-DD) |
| users | UUID[] | Associated user IDs |
| split | Object[] | `[{ user: UUID, share: Number }]` (must sum to 100) |
| externalId | String | External ID |
| contributors | Object[] | `[{ name, role }]` |
| links | Object | `{ website, twitter, instagram, facebook, youtube }` |

**Optional:** `label`, `copyright`, `publisher`

---

## GET `/artist/stats/{id}` - Artist Stats

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| assets | Integer | Number of tracks |
| products | Integer | Number of products |
| totalRoyalties | Number | Total earned |
| totalPaid | Number | Total paid out |
| totalDue | Number | Outstanding balance |

---

## GET `/artist/{id}/assets` - Artist Assets

**Query:** `page`, `size`, `type` (filter by asset type, default: `all`)

Returns array of assets with: `id`, `title`, `isrc`, `status` (draft/published/archived), `splitCount`, `count` (streams), `royalty`, nested `Products` and `Artists` arrays.

---

## GET `/artist/{id}/products` - Artist Products

**Query:** `page`, `size`, `type`

Returns array of products with: `id`, `upc`, `title`, `splitCount`, `count`, `royalty`, nested `Assets` (with track numbers) and `Artists` arrays.

---

## Other Artist Endpoints

| Method | Path | Description |
|--------|------|-------------|
| PUT | `/artist/{id}` | Update artist |
| DELETE | `/artist/{id}` | Delete artist |
| GET | `/artist/{id}/splits` | All default splits |
| GET | `/artist/{id}/splits/{type}` | Splits by type |
| POST | `/artist/{id}/splits` | Create default splits |
| PUT | `/artist/{id}/splits/{type}` | Update splits by type |
| DELETE | `/artist/{id}/splits/{type}` | Delete splits by type |
| POST | `/artist/bulk` | Bulk create |
| DELETE | `/artist/bulk` | Bulk delete |
| PUT | `/artist/bulk/splits` | Bulk update splits |
| POST | `/artist/merge` | Merge duplicate artists |
| GET | `/artist/download` | CSV export |
