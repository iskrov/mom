# Artists

## GET `/artist/:id` - Metadata

Artist metadata and cross-platform identifiers.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Chartmetric artist ID |
| name | String | Artist name |
| image_url | String | Profile image URL |
| isni | String | ISNI identifier |
| code2 | String | 2-letter country code |
| hometown_city | String | Hometown |
| current_city | String | Current city |
| tags | Array | Genre tags |
| description | String | Artist bio |
| sp_followers | Integer | Spotify followers |
| sp_popularity | Integer | Spotify popularity (0-100) |
| sp_monthly_listeners | Integer | Spotify monthly listeners |
| deezer_fans | Integer | Deezer fans |
| cm_artist_rank | Integer | Chartmetric ranking |
| spotify_artist_ids | Array | Spotify IDs |
| itunes_artist_ids | Array | iTunes/Apple Music IDs |
| deezer_artist_ids | Array | Deezer IDs |
| amazon_artist_ids | Array | Amazon Music IDs |

---

## GET `/artist/:id/albums` - Albums

All albums by the artist.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

---

## GET `/artist/:id/tracks` - Tracks

All tracks by the artist.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

---

## GET `/artist/:id/urls` - Profile URLs

Social media and streaming platform URLs linked to the artist.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

**Response:** URLs for Spotify, Apple Music, YouTube, Instagram, Twitter, TikTok, SoundCloud, Genius, etc.

---

## GET `/artist/:id/stat/:source` - Fan Metrics

Time-series fan/follower metrics for a specific platform.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |
| source | String | yes | Platform source |
| since | String | no | Start date (ISO) |
| until | String | no | End date (ISO), default: today |
| field | String | no | Specific metric field |

**`source` values:** `spotify`, `youtube_channel`, `youtube_artist`, `instagram`, `twitter`, `tiktok`, `soundcloud`, `deezer`, `wikipedia`, `genius`, `shazam`, `bandsintown`, `songkick`

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| value | Number | Metric value |
| timestp | Date | Timestamp |

---

## GET `/artist/:id/:type/:status/playlists` - Playlists

Playlists currently or previously featuring the artist.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |
| type | String | yes | Platform: `spotify`, `applemusic`, `deezer`, `amazon`, `youtube` |
| status | String | yes | `current` or `past` |
| since | String | no | Start date (default: 180 days ago) |
| until | String | no | End date (default: today) |
| limit | Integer | no | Results per page (default: 10) |
| offset | Integer | no | Pagination offset |
| indie | Boolean | no | Filter by indie curation |
| editorial | Boolean | no | Platform editorial playlists (default: true) |

Additional Spotify-specific filters: `majorCurator`, `newMusicFriday`, `thisIs`, `fullyPersonalized`, `radio`, `brand`, `audiobook`

Additional Apple Music filters: `editorialBrand`, `personalized`, `musicBrand`, `nonMusicBrand`, `personalityArtist`

Additional Deezer filters: `deezerPartner`, `hundredPercent`, `chart`

---

## GET `/artist/:id/:type/charts` - Chart Positions

Historical chart data for the artist.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |
| type | String | yes | Chart type |
| since | String | no | Start date (default: 180 days ago) |
| until | String | no | End date (default: today, max 365 days range) |

---

## GET `/artist/:id/relatedartists` - Related Artists

Similar/related artists.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |
| limit | Integer | no | Number of results |

---

## GET `/artist/:id/where-people-listen` - Geographic Listeners

Spotify's "Where People Listen" geographic data.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |
| since | String | no | Start date |

---

## GET `/artist/:id/cpp` - Career Performance Profile

Historical CPP rank/score data.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |
| cpp_stat | String | no | Specific CPP metric |
| since | String | no | Start date |
| until | String | no | End date |

---

## GET `/artist/:id/tunefind` - Sync Placements

TV/movie sync placement data from Tunefind.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

---

## GET `/artist/:id/instagram-audience-stats` - Instagram Audience

Instagram audience demographics and stats.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

---

## GET `/artist/:id/tiktok-audience-stats` - TikTok Audience

TikTok audience demographics and stats.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

---

## GET `/artist/:id/tvmaze` - TV Appearances

TV appearance data from TVmaze.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric artist ID |

---

## GET `/artist/:type/:id/get-ids` - Cross-Platform IDs

Look up all platform IDs from one known ID.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | String | yes | ID type: `chartmetric`, `spotify`, `itunes`, `deezer`, `amazon` |
| id | String | yes | The known ID value |

**Response:** `cm_artist`, `artist_name`, `spotify_artist_id`, `itunes_artist_id`, `deezer_artist_id`, `amazon_artist_id`

---

## GET `/artist/:type/list` - Filtered Artist List

Browse artists filtered by metric thresholds.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | String | yes | Filter metric field |
| min | Integer | no | Minimum threshold |
| max | Integer | no | Maximum threshold |
| offset | Integer | no | Pagination offset |

---

## GET `/artist/anr/by/playlists` - A&R by Playlists

Discover rising artists ranked by playlist momentum.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| sortBy | String | yes | `followers_total_reach_diff_week`, `followers_total_reach_diff_week_percent` |
| streamingType | String | yes | `spotify` |
| limit | Integer | no | Results (default: 10) |

**Response includes:** rank, playlist count, total reach, weekly reach growth, popularity, follower counts, listener counts, genre tags, recent releases

---

## GET `/artist/anr/by/social-index` - A&R by Social Index

Discover rising artists ranked by cross-platform social metrics.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| sortBy | String | yes | Sort metric (see below) |
| offset | Integer | no | Default: 0 |
| limit | Integer | no | Default: 10 |
| code2 | String | no | Country filter (2-letter code) |
| tagIds | Integer | no | Genre filter |
| maxSpotifyFollowers | Integer | no | Max followers filter |
| sortOrderDesc | Boolean | no | Descending (default: true) |
| recentReleaseWithin | Integer | no | Days since first release |
| latestReleaseWithin | Integer | no | Days since latest release |

**`sortBy` values:** `spotify_popularity`, `spotify_followers`, `spotify_monthly_listeners`, `twitter_followers`, `instagram_followers`, `wiki_views`, `soundcloud_followers`, `tiktok_followers`, `youtube_channel_views`
