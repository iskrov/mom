# Me (Authenticated User)

All endpoints require a valid OAuth access token via `Authorization: OAuth ACCESS_TOKEN` header.

## GET `/me`

Get the authenticated user's profile.

**Parameters:** None

**Response:** CompleteUser object

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | User ID |
| username | String | Display name |
| full_name | String | Full name |
| first_name | String | First name |
| last_name | String | Last name |
| avatar_url | String | Profile image URL |
| permalink | String | URL slug |
| permalink_url | String | Full profile URL |
| uri | String | API resource URI |
| kind | String | Resource type (`user`) |
| city | String | City |
| country | String | Country |
| description | String | Bio/description |
| discogs_name | String | Discogs username |
| locale | String | User locale |
| website | String | Website URL |
| website_title | String | Website display title |
| plan | String | Subscription plan |
| created_at | DateTime | Account creation timestamp |
| last_modified | DateTime | Last profile update |
| followers_count | Integer | Number of followers |
| followings_count | Integer | Number of users followed |
| track_count | Integer | Number of public tracks |
| playlist_count | Integer | Number of public playlists |
| reposts_count | Integer | Number of reposts |
| public_favorites_count | Integer | Number of public likes |
| primary_email_confirmed | Boolean | Whether primary email is confirmed |
| private_tracks_count | Integer | Number of private tracks |
| private_playlists_count | Integer | Number of private playlists |
| quota.unlimited_upload_quota | Boolean | Whether upload quota is unlimited |
| quota.upload_seconds_used | Integer | Seconds of audio uploaded |
| subscriptions | Array | Active subscription details |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/activities`

Get the authenticated user's activity feed.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Activities collection (paginated)

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | Activity objects |
| next_href | String | URL for next page of results |
| future_href | String | URL for polling new activities |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/activities/all/own`

Get the authenticated user's own recent activities.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Activities collection (same schema as `/me/activities`)

---

## GET `/me/activities/tracks`

Get track-related activities for the authenticated user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Activities collection (same schema as `/me/activities`)

---

## GET `/me/connections`

Get the authenticated user's connected social accounts.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (deprecated, default 0) |

**Response:** Array of Connection objects

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Connection ID |
| kind | String | `connection` |
| created_at | DateTime | Connection creation timestamp |
| display_name | String | Display name on connected service |
| service | String | Service name (e.g., `facebook`, `twitter`) |
| type | String | Connection type |
| uri | String | API resource URI |
| post_publish | Boolean | Auto-post on publish |
| post_favorite | Boolean | Auto-post on favorite |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/connections/:connection_id`

Get a specific social connection.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| connection_id | path | Integer | yes | Connection ID |

**Response:** Single Connection object (same schema as above)

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/me/likes/tracks`

Get tracks liked by the authenticated user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | Track objects |
| next_href | String | URL for next page |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/favorites/ids` (Deprecated)

Get IDs of tracks favorited by the authenticated user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Not Found |

---

## GET `/me/followings`

Get users followed by the authenticated user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0) |

**Response:** Paginated User collection

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | User objects (see MetaUser schema below) |
| next_href | String | URL for next page |

**MetaUser fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | User ID |
| kind | String | Resource type |
| avatar_url | String | Profile image URL |
| permalink | String | URL slug |
| permalink_url | String | Full profile URL |
| uri | String | API resource URI |
| username | String | Display name |
| created_at | DateTime | Account creation timestamp |
| last_modified | DateTime | Last update timestamp |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/followings/tracks`

Get recent tracks from users the authenticated user follows.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0) |

**Response:** Paginated Track collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/followings/:user_id` (Deprecated)

Check if the authenticated user follows a specific user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | Target user ID |

**Response:** User object

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Following exists |
| 401 | Unauthorized |
| 404 | Not following this user |

---

## PUT `/me/followings/:user_id`

Follow a user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID to follow |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Already following |
| 201 | Successfully followed |
| 401 | Unauthorized |
| 404 | User not found |

---

## DELETE `/me/followings/:user_id`

Unfollow a user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID to unfollow |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Successfully unfollowed |
| 401 | Unauthorized |
| 404 | User not found |
| 422 | Unprocessable Entity |

---

## GET `/me/followers`

Get the authenticated user's followers.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Paginated User collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/followers/:follower_id` (Deprecated)

Get a specific follower.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| follower_id | path | Integer | yes | Follower user ID |

**Response:** User object

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/playlists`

Get the authenticated user's playlists.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Array of Playlist objects

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/me/playlists/:playlist_id` (Deprecated)

Get a specific playlist owned by the authenticated user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| playlist_id | path | Integer | yes | Playlist ID |

**Response:** Playlist object

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |

---

## GET `/me/tracks`

Get the authenticated user's tracks.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/me/tracks/:track_id` (Deprecated)

Get a specific track owned by the authenticated user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |

**Response:** Track object

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
