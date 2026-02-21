# Tracks

## GET `/tracks` - Search Tracks

Search and filter tracks. Also used as the primary search endpoint with the `q` parameter.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| q | query | String | yes | Search keyword (searches title, username, description) |
| ids | query | String | no | Comma-separated track IDs (e.g., `1,2,3`) |
| genres | query | String | no | Comma-separated genre filter (e.g., `Pop,House`) |
| tags | query | String | no | Comma-separated tag filter |
| bpm[from] | query | Integer | no | Minimum BPM |
| bpm[to] | query | Integer | no | Maximum BPM |
| duration[from] | query | Integer | no | Minimum duration in milliseconds |
| duration[to] | query | Integer | no | Maximum duration in milliseconds |
| created_at[from] | query | String | no | Created after (ISO 8601 date) |
| created_at[to] | query | String | no | Created before (ISO 8601 date) |
| access | query | Array | no | Filter by access level: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0, deprecated) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | Array of Track objects |
| next_href | String | URL for next page of results |

**Track Object:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Track ID |
| title | String | Track title |
| description | String | Track description |
| kind | String | Resource type (`track`) |
| uri | String | API resource URI |
| permalink | String | URL slug |
| permalink_url | String | Full track URL on SoundCloud |
| artwork_url | String | Cover art URL |
| waveform_url | String | Waveform image URL |
| stream_url | String | Legacy stream URL |
| download_url | String | Download URL (if downloadable) |
| secret_uri | String | Secret sharing URI (private tracks) |
| user | MetaUser | Track uploader (see Users) |
| duration | Integer | Duration in milliseconds |
| bpm | Integer | Beats per minute |
| genre | String | Genre |
| tag_list | String | Space-separated tags |
| label_name | String | Record label name |
| isrc | String | International Standard Recording Code |
| key_signature | String | Musical key signature |
| release | String | Release identifier |
| release_day | Integer | Release day (1-31) |
| release_month | Integer | Release month (1-12) |
| release_year | Integer | Release year |
| created_at | DateTime | Upload timestamp |
| sharing | String | `public` or `private` |
| license | String | License type (see allowed values below) |
| embeddable_by | String | Who can embed: `all`, `me`, `none` |
| streamable | Boolean | Whether track is streamable |
| downloadable | Boolean | Whether track is downloadable |
| commentable | Boolean | Whether comments are enabled |
| playback_count | Integer | Number of plays |
| download_count | Integer | Number of downloads |
| favoritings_count | Integer | Number of likes/favorites |
| comment_count | Integer | Number of comments |
| reposts_count | Integer | Number of reposts |
| user_favorite | Boolean | Whether authenticated user has liked |
| user_playback_count | Integer | Authenticated user's play count |
| purchase_url | String | External purchase URL |
| purchase_title | String | Purchase link text |
| available_country_codes | String | Comma-separated country codes |
| access | String | Access level: `playable`, `preview`, `blocked`, or `null` |

**License allowed values:** `no-rights-reserved`, `all-rights-reserved`, `cc-by`, `cc-by-nc`, `cc-by-nd`, `cc-by-sa`, `cc-by-nc-nd`, `cc-by-nc-sa`

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 500 | Internal Server Error |

---

## POST `/tracks` - Upload Track

Upload a new audio track. Maximum file size: 500MB.

**Request Body** (`multipart/form-data`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| track[title] | String | yes | Track title |
| track[asset_data] | Binary | yes | Audio file |
| track[permalink] | String | no | Custom URL slug |
| track[sharing] | String | no | `public` (default) or `private` |
| track[embeddable_by] | String | no | `all`, `me`, or `none` |
| track[purchase_url] | String | no | External purchase URL |
| track[description] | String | no | Track description |
| track[genre] | String | no | Genre |
| track[tag_list] | String | no | Space-separated tags |
| track[label_name] | String | no | Record label |
| track[release] | String | no | Release identifier |
| track[release_date] | String | no | Release date (`yyyy-mm-dd`) |
| track[streamable] | Boolean | no | Allow streaming (default: `true`) |
| track[downloadable] | Boolean | no | Allow downloads (default: `true`) |
| track[license] | String | no | License type (see allowed values above) |
| track[commentable] | Boolean | no | Allow comments (default: `true`) |
| track[isrc] | String | no | ISRC code |
| track[artwork_data] | Binary | no | Artwork image (PRO users only) |

**Supported audio formats:** AIFF, WAVE, FLAC, OGG, MP2, MP3, AAC, AMR, WMA

**Response:** Track object (same schema as above)

**Status Codes:**

| Code | Description |
|------|-------------|
| 201 | Track created and queued for encoding |
| 400 | Bad Request - missing required fields |
| 401 | Unauthorized |

**Usage:**

```bash
curl -X POST https://api.soundcloud.com/tracks \
  -H "Authorization: OAuth ACCESS_TOKEN" \
  -F "track[title]=My Track" \
  -F "track[asset_data]=@/path/to/audio.mp3"
```

---

## GET `/tracks/:track_id` - Track Details

Get metadata for a specific track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |
| secret_token | query | String | no | Secret token for private tracks |

**Response:** Track object (full schema above)

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## PUT `/tracks/:track_id` - Update Track

Update track metadata or artwork. Audio file cannot be replaced.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |

**Request Body** (`application/json` or `multipart/form-data`):

All fields from the upload schema except `track[asset_data]` are accepted. Additionally:

| Field | Type | Description |
|-------|------|-------------|
| track[artwork_data] | Binary | Replacement artwork image (multipart only) |

**Response:** Updated Track object

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |

**Note:** It is not possible to update the actual audio file. Only metadata and artwork can be changed.

---

## DELETE `/tracks/:track_id` - Delete Track

Delete a track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 404 | Not Found |

---

## GET `/tracks/:track_id/streams` - Stream URLs

Get streaming URLs for a track in various formats.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |
| secret_token | query | String | no | Secret token for private tracks |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| http_mp3_128_url | String | Direct HTTP MP3 128kbps stream URL |
| hls_mp3_128_url | String | HLS MP3 128kbps stream URL |
| hls_opus_64_url | String | HLS Opus 64kbps stream URL |
| preview_mp3_128_url | String | Preview MP3 128kbps URL (for preview-only tracks) |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

**Notes:**
- Not every track is streamable off-platform. Access level may be `preview` or `blocked`.
- Play requests count toward the 15,000/24h rate limit.

---

## GET `/tracks/:track_id/comments` - List Comments

Get comments on a track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Comment collection

| Field | Type | Description |
|-------|------|-------------|
| collection | Array | Comment objects |
| next_href | String | URL for next page |

**Comment Object:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Comment ID |
| kind | String | `comment` |
| body | String | Comment text |
| created_at | DateTime | Comment timestamp |
| uri | String | API resource URI |
| timestamp | String | Position in track (milliseconds from start), or null |
| track_id | Integer | Track ID |
| user_id | Integer | Commenter user ID |
| user | User | Commenter user object (limited fields) |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## POST `/tracks/:track_id/comments` - Post Comment

Post a comment on a track. Requires authentication.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |

**Request Body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| comment.body | String | yes | Comment text |
| comment.timestamp | String/Number | no | Position in track (milliseconds from start) |

**Response:** Created Comment object

**Status Codes:**

| Code | Description |
|------|-------------|
| 201 | Comment created |
| 422 | Unprocessable Entity - comments disabled by creator |
| 429 | Too Many Requests |

**Usage:**

```bash
curl -X POST https://api.soundcloud.com/tracks/12345/comments \
  -H "Authorization: OAuth ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"comment": {"body": "Great track!", "timestamp": 30000}}'
```

---

## GET `/tracks/:track_id/favoriters` - Track Likers

Get users who liked/favorited a track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0) |

**Response:** Paginated User collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/tracks/:track_id/reposters` - Track Reposters

Get users who reposted a track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |
| limit | query | Integer | no | Results per page (1-200, default 50) |

**Response:** Array of MetaUser objects

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |

---

## GET `/tracks/:track_id/related` - Related Tracks

Get tracks related/similar to a given track.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| track_id | path | Integer | yes | Track ID |
| access | query | Array | no | Filter: `playable`, `preview`, `blocked` |
| limit | query | Integer | no | Results per page (1-200, default 50) |
| offset | query | Integer | no | Pagination offset (default 0) |
| linked_partitioning | query | Boolean | no | Enable cursor-based pagination |

**Response:** Paginated Track collection

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |
| 404 | Not Found |
