# Users

## GET `/users` - Search Users

Search for users by keyword.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| q | query | String | yes | Search keyword (searches username, description) |
| ids | query | String | no | Comma-separated user IDs |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0, deprecated) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated User collection

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | Array of User objects |
| next_href | String | URL for next page of results |

**User Object:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | User ID |
| username | String | Display name |
| full_name | String | Full name |
| first_name | String | First name |
| last_name | String | Last name |
| kind | String | Resource type (`user`) |
| avatar_url | String | Profile image URL |
| permalink | String | URL slug |
| permalink_url | String | Full profile URL on SoundCloud |
| uri | String | API resource URI |
| city | String | City |
| country | String | Country |
| description | String | Bio/description |
| discogs_name | String | Discogs username |
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
| subscriptions | Array | Subscription details |

**MetaUser Object** (compact user representation used in nested responses):

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
| 400 | Bad Request |
| 401 | Unauthorized |

---

## GET `/users/:user_id` - User Profile

Get detailed profile for a specific user. Returns CompleteUser when authenticated.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |

**Response:** CompleteUser object

Returns all User fields (above) plus:

| Field | Type | Description |
|-------|------|-------------|
| locale | String | User locale |
| primary_email_confirmed | Boolean | Whether primary email is confirmed |
| private_tracks_count | Integer | Number of private tracks (own profile only) |
| private_playlists_count | Integer | Number of private playlists (own profile only) |
| quota.unlimited_upload_quota | Boolean | Unlimited upload (own profile only) |
| quota.upload_seconds_used | Integer | Seconds of audio uploaded (own profile only) |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/users/:user_id/comments` - User Comments

Get comments posted by a user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0) |

**Response:** Paginated Comment collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/users/:user_id/favorites` (Deprecated)

Get tracks favorited by a user. Use `/users/:user_id/likes/tracks` instead.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/users/:user_id/followers` - User Followers

Get a user's followers.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Paginated User collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/users/:user_id/followings` - User Followings

Get users followed by a specific user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Paginated User collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/users/:user_id/followings/:following_id` (Deprecated)

Check if a user follows a specific other user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| following_id | path | Integer | yes | Following user ID |

**Response:** CompleteUser object

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Following exists |
| 401 | Unauthorized |
| 404 | Not following |

---

## GET `/users/:user_id/playlists` - User Playlists

Get a user's public playlists.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Playlist collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/users/:user_id/tracks` - User Tracks

Get a user's public tracks.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

## GET `/users/:user_id/web-profiles` - Web Profiles

Get a user's external website/social links.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Array of WebProfile objects

**WebProfile Object:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Web profile ID |
| kind | String | Resource type |
| created_at | DateTime | Creation timestamp |
| service | String | Service name (e.g., `twitter`, `instagram`, `facebook`) |
| title | String | Display title |
| url | String | Profile URL on external service |
| username | String | Username on external service |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/users/:user_id/likes/tracks` - User Liked Tracks

Get tracks liked by a specific user.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| user_id | path | Integer | yes | User ID |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
