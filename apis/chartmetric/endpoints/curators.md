# Curators

Curator = the entity (person/brand) that manages playlists on a streaming platform.

## GET `/curator/:platform/lists` - Browse Curators

List and rank curators on a streaming platform.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer` |
| limit | Integer | no | Results per page (max: 100) |
| offset | Integer | no | Pagination offset |
| indie | Boolean | no | Filter for non-major-label curated |
| withSocialUrls | Boolean | no | Include social media URLs |

---

## GET `/curator/:platform/:id` - Curator Metadata

Metadata for a specific curator.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer` |
| id | String/Integer | yes | Chartmetric curator ID |

---

## GET `/curator/:platform/:id/playlists` - Curator's Playlists

All playlists managed by the curator.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| platform | String | yes | `spotify`, `applemusic`, `deezer` |
| id | String/Integer | yes | Chartmetric curator ID |
