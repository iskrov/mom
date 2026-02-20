# Charts

Multi-platform chart data. Some platforms only update on specific days.

## Day-of-Week Availability

| Platform | Available Days | Notes |
|----------|---------------|-------|
| Spotify | Daily | Regional + viral charts |
| Apple Music | Daily | Tracks, albums, videos |
| iTunes | Daily | Tracks, albums, videos |
| YouTube | Thursdays only | Trends, videos, artists, tracks |
| Shazam | Daily | With optional city-level data |
| SoundCloud | Fridays only | Top + trending |
| Beatport | Fridays only | Electronic music focus |
| QQ Music | Thursdays only | Chinese market |
| TikTok | Variable | Tracks, videos, users |
| Deezer | Daily | Top 100 |
| Amazon | Daily | Tracks + albums, 23 genre filters |

---

## Spotify

### GET `/charts/spotify` - Top 200

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| date | String | yes | - | ISO date YYYY-MM-DD |
| country_code | String | no | - | 2-letter country code |
| type | String | no | "regional" | `viral` or `regional` |
| interval | String | no | "daily" | `daily` |
| offset | Integer | no | 0 | Pagination offset |

### GET `/charts/spotify/freshfind` - Fresh Finds

| Name | Type | Required | Description |
|------|------|----------|-------------|
| date | String | yes | ISO date (must be a Thursday) |

---

## Apple Music

### GET `/charts/applemusic/tracks` - Track Charts

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| date | String | yes | - | ISO date |
| country_code | String | no | - | 2-letter country code |
| genre | String | no | "All Genres" | Genre filter |
| type | String | no | "daily" | Chart type |
| offset | Integer | no | 0 | Pagination |

### GET `/charts/applemusic/albums` - Album Charts

Same parameters as tracks (without `type`)

### GET `/charts/applemusic/videos` - Video Charts

Same parameters as albums

---

## iTunes

### GET `/charts/itunes/tracks` - Track Charts

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| date | String | yes | - | ISO date |
| country_code | String | no | "US" | Country code |
| genre | String | no | "All Genres" | Genre filter |
| offset | Integer | no | 0 | Pagination |

### GET `/charts/itunes/albums` - Album Charts

Same parameters as tracks

### GET `/charts/itunes/videos` - Video Charts

Same parameters (without `genre`)

---

## YouTube

All YouTube endpoints return data only on Thursdays. Dates are auto-adjusted.

### GET `/charts/youtube/trends` - Trending

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| date | String | yes | - | ISO date (adjusted to Thursday) |
| country_code | String | no | "US" | Country code |
| offset | Integer | no | 0 | Pagination |

### GET `/charts/youtube/videos` - Top Videos

Same parameters as trends

### GET `/charts/youtube/artists` - Top Artists

Same parameters as trends

### GET `/charts/youtube/tracks` - Top Tracks

Same parameters as trends

---

## Amazon Music

### GET `/charts/amazon/tracks` - Track Charts

| Name | Type | Required | Description |
|------|------|----------|-------------|
| date | String | yes | ISO date |
| type | String | yes | `popular_track` or `new_track` |
| genre | String | yes | Genre filter (see list below) |

### GET `/charts/amazon/albums` - Album Charts

| Name | Type | Required | Description |
|------|------|----------|-------------|
| date | String | yes | ISO date |
| type | String | yes | `popular_album` or `new_album` |
| genre | String | yes | Genre filter |

**Amazon genres:** Pop, Rock, Hip-Hop/Rap, R&B, Country, Electronic/Dance, Latin, Jazz, Classical, Blues, Folk, Reggae, Soul, Gospel, New Age, World, Children's Music, Soundtracks, Comedy, Spoken Word, Holiday, Alternative, Indie

---

## Shazam

### GET `/charts/shazam` - Top 200

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| date | String | yes | - | ISO date |
| country_code | String | no | - | Country code |
| offset | Integer | no | 0 | Pagination |
| city | String | no | - | City name for city-level data |

### GET `/charts/shazam/:country_code/cities` - Available Cities

Returns list of cities available for Shazam city-level filtering.

| Name | Type | Required | Description |
|------|------|----------|-------------|
| country_code | String | yes | 2-letter country code (path param) |

---

## SoundCloud

### GET `/charts/soundcloud` - Charts

| Name | Type | Required | Description |
|------|------|----------|-------------|
| date | String | yes | ISO date (adjusted to Friday) |
| country_code | String | no | Country code |
| kind | String | no | `top` or `trending` |
| genre | String | no | Genre filter |

---

## Beatport

### GET `/charts/beatport` - Charts

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| date | String | yes | - | ISO date (adjusted to Friday) |
| genre | String | no | "top-100" | Genre filter |
| offset | Integer | no | 0 | Pagination |

---

## Deezer

### GET `/charts/deezer` - Top 100

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| date | String | yes | - | ISO date |
| country_code | String | no | "US" | Country code |

---

## QQ Music

### GET `/charts/qq` - Charts

| Name | Type | Required | Description |
|------|------|----------|-------------|
| date | String | yes | ISO date (adjusted to Thursday) |

---

## TikTok

### GET `/charts/tiktok/:chart_type` - TikTok Charts

| Name | Type | Required | Description |
|------|------|----------|-------------|
| chart_type | String | yes | `tracks`, `videos`, or `users` |
| date | String | yes | ISO date |
| interval | String | no | Time interval |
| limit | Integer | no | Results per page |

---

## Radio Airplay

### GET `/charts/airplay/:chart_type` - Airplay Charts

| Name | Type | Required | Description |
|------|------|----------|-------------|
| chart_type | String | yes | Chart type |

---

## Twitch

### GET `/charts/twitch/users` - User Charts

Twitch user ranking data.

---

## CM Scores

Chartmetric's proprietary scoring for entity performance on specific chart types.

**`chart_type` values:** `spotify-top`, `spotify-viral`, `applemusic-genre`, `applemusic-daily`, `applemusic-albums`, `itunes`, `itunes-albums`, `shazam`

### GET `/charts/track/:id/:chart_type/cm-score`

| Name | Type | Required | Description |
|------|------|----------|-------------|
| id | Integer | yes | Chartmetric track ID |
| chart_type | String | yes | Chart type (see values above) |
| since | String | no | Start date (ISO) |
| until | String | no | End date (default: today) |

### GET `/charts/artist/:id/:chart_type/cm-score`

Same parameters with artist ID

### GET `/charts/album/:id/:chart_type/cm-score`

Same parameters with album ID
