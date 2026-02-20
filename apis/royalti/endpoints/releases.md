# Releases (Content Distribution Workflow)

Releases follow a workflow: `draft` -> `submitted` -> `under_review` -> `approved`/`rejected` -> `completed`. On approval, assets and products are auto-created.

## GET `/releases` - List Releases

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| status | String | - | Filter: `draft`, `submitted`, `under_review`, `approved`, `rejected`, `completed` |
| format | String | - | Filter: `Single`, `EP`, `Album`, `LP`, `Video` |
| type | String | - | Filter: `Audio`, `Video` |
| search | String | - | Search in title, displayArtist, description |
| owner | UUID | - | Filter by owner user ID |
| page | Integer | 1 | Page number |
| limit | Integer | 20 | Items per page |

**Response (Release object):**

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Release ID |
| title | String | Release title |
| displayArtist | String | Display artist name |
| artists | Array | `[{ id, artistName, type: "primary"/"featuring" }]` |
| tracks | Array | Track objects (see below) |
| format | String | Single, EP, Album, LP, Video |
| type | String | Audio, Video |
| version | String | Version label |
| label | String | Record label |
| copyright | String | Copyright |
| mainGenre | String[] | Main genres |
| subGenre | String[] | Sub-genres |
| contributors | String[] | Contributors |
| description | String | Description |
| metadata | Object | Additional metadata |
| media | Object[] | Media files |
| explicit | String | `explicit`, `clean`, or null |
| releaseDate | DateTime | Release date |
| preReleaseDate | DateTime | Pre-release date |
| status | String | Current workflow status |
| autoCreationStatus | String | `pending`, `success`, `failed` |
| createdProductId | UUID | Product created on approval |
| createdAssetIds | UUID[] | Assets created on approval |
| owner | Object | `{ id, firstName, lastName, email }` |

**Track object:**

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Track ID |
| trackNumber | Integer | Position |
| title | String | Track title |
| version | String | Version |
| isrc | String | ISRC |
| iswc | String | ISWC |
| duration | Float | Seconds |
| lyrics | String | Lyrics |
| language | String | Language code |
| displayArtist | String | Display artist |
| artists | Array | Artist references |
| mainGenre | String[] | Genres |
| subGenre | String[] | Sub-genres |
| contributors | Object | `{ role: [names] }` |
| media | Array | Media files (cloudId, cloudUrl, type, name, isLink, metadata) |
| assetId | UUID | Linked existing asset (if any) |

---

## POST `/releases` - Create Release

**Required Fields:**

| Field | Type | Description |
|-------|------|-------------|
| title | String | Release title |
| displayArtist | String | Display artist name |
| artists | Object | `{ "artistUUID": "primary", "artistUUID2": "featuring" }` |

**Optional Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| format | String | `Single` | Single, EP, Album, LP, Video |
| type | String | `Audio` | Audio, Video |
| version | String | null | Version label |
| label | String | null | Record label |
| copyright | String | null | Copyright |
| mainGenre | String[] | - | Main genres |
| subGenre | String[] | - | Sub-genres |
| contributors | Object[] | - | `[{ role, name, isni }]` |
| description | String | null | Description |
| metadata | Object | - | Free-form (e.g., `{ upc, catalogNumber }`) |
| explicit | String | null | `explicit` or `clean` |
| releaseDate | Date | - | Release date |
| preReleaseDate | Date | null | Pre-release date |
| ownerId | UUID | null | Override owner (admin only) |
| tracks | Array | - | Track objects (see below) |

**Track input fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | String | yes | Track title |
| displayArtist | String | yes | Display artist |
| version | String | no | Version |
| isrc | String | no | ISRC |
| iswc | String | no | ISWC |
| duration | Number | no | Seconds |
| lyrics | String | no | Lyrics |
| language | String | no | Default: `"en"` |
| artists | Object | no | `{ UUID: "primary"/"featuring" }` |

---

## GET `/releases/stats` - Release Statistics

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| total | Integer | Total releases |
| totalPublished | Integer | Published/completed |
| totalDrafts | Integer | Drafts |
| totalRejected | Integer | Rejected |
| totalPending | Integer | Pending/submitted |
| totalScheduled | Integer | Scheduled |

---

## Workflow Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/releases/{id}/submit` | Submit for review |
| POST | `/releases/{id}/review` | Review (admin only) |
| POST | `/releases/{id}/revert` | Revert status (admin only) |
| POST | `/releases/{id}/feedback` | Add feedback |

## Media Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/releases/{id}/media` | Upload media files |
| POST | `/releases/{id}/media-links` | Submit media via URLs |
| POST | `/releases/{id}/tracks/{trackId}/media` | Upload track-specific media |

## Track Management

| Method | Path | Description |
|--------|------|-------------|
| POST | `/releases/{id}/tracks` | Add track |
| PUT | `/releases/{id}/tracks/{trackId}` | Update track |
| DELETE | `/releases/{id}/tracks/{trackId}` | Delete track |
| PUT | `/releases/{id}/tracks/reorder` | Reorder tracks |
| POST | `/releases/{id}/link-asset` | Link existing asset |
