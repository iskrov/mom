# Chartmetric API - Quick Reference

All paths relative to `https://api.chartmetric.com/api`

## Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/token` | Get access token from refresh token |

## Search

| Method | Path | Description |
|--------|------|-------------|
| GET | `/search` | Search artists, tracks, albums, playlists, curators, stations, cities |

## Artists

| Method | Path | Description |
|--------|------|-------------|
| GET | `/artist/:id` | Artist metadata |
| GET | `/artist/:id/albums` | Artist's albums |
| GET | `/artist/:id/tracks` | Artist's tracks |
| GET | `/artist/:id/urls` | Social/streaming profile URLs |
| GET | `/artist/:id/stat/:source` | Fan metrics by platform |
| GET | `/artist/:id/:type/:status/playlists` | Playlists featuring artist |
| GET | `/artist/:id/:type/charts` | Chart positions |
| GET | `/artist/:id/relatedartists` | Related/similar artists |
| GET | `/artist/:id/where-people-listen` | Spotify geographic listener data |
| GET | `/artist/:id/cpp` | Career Performance Profile |
| GET | `/artist/:id/tunefind` | TV/movie sync placements |
| GET | `/artist/:id/instagram-audience-stats` | Instagram audience demographics |
| GET | `/artist/:id/tiktok-audience-stats` | TikTok audience demographics |
| GET | `/artist/:id/tvmaze` | TV appearances |
| GET | `/artist/:type/:id/get-ids` | Cross-platform ID lookup |
| GET | `/artist/:type/list` | Filtered artist list by metrics |
| GET | `/artist/anr/by/playlists` | A&R discovery by playlist metrics |
| GET | `/artist/anr/by/social-index` | A&R discovery by social metrics |

## Tracks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/track/:id` | Track metadata |
| GET | `/track/:id/:platform/stats` | Platform-specific stats time series |
| GET | `/track/:id/:type/charts` | Chart positions |
| GET | `/track/:id/:platform/:status/playlists` | Playlists containing track |
| GET | `/track/:id/:platform/playlists/snapshot` | Playlist snapshot for a date |
| GET | `/track/:id/tunefind` | TV/movie sync placements |
| GET | `/track/:type/:id/get-ids` | Cross-platform ID lookup |

## Albums

| Method | Path | Description |
|--------|------|-------------|
| GET | `/album/:id` | Album metadata |
| GET | `/album/:id/tracks` | Album tracks |
| GET | `/album/:id/:platform/:stat` | Platform stats (e.g., spotify/followers) |
| GET | `/album/:id/:platform/:status/playlists` | Playlists featuring album |
| GET | `/album/:id/:type/charts` | Chart positions |
| GET | `/album/:type/:id/get-ids` | Cross-platform ID lookup |

## Playlists

| Method | Path | Description |
|--------|------|-------------|
| GET | `/playlist/:platform/:id` | Playlist metadata |
| GET | `/playlist/:platform/lists` | Browse playlists by platform |
| GET | `/playlist/:platform/:id/snapshot` | Track snapshot at a date |
| GET | `/playlist/:platform/:id/:span/tracks` | Current or past tracks |
| GET | `/playlist/:platform/:id/similarplaylists` | Similar playlists |

## Curators

| Method | Path | Description |
|--------|------|-------------|
| GET | `/curator/:platform/lists` | Browse curators by platform |
| GET | `/curator/:platform/:id` | Curator metadata |
| GET | `/curator/:platform/:id/playlists` | Curator's playlists |

## Charts - Platform Charts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/charts/spotify` | Spotify top 200 (viral/regional) |
| GET | `/charts/spotify/freshfind` | Spotify Fresh Finds |
| GET | `/charts/applemusic/tracks` | Apple Music track charts |
| GET | `/charts/applemusic/albums` | Apple Music album charts |
| GET | `/charts/applemusic/videos` | Apple Music video charts |
| GET | `/charts/itunes/tracks` | iTunes track charts |
| GET | `/charts/itunes/albums` | iTunes album charts |
| GET | `/charts/itunes/videos` | iTunes video charts |
| GET | `/charts/youtube/trends` | YouTube trending |
| GET | `/charts/youtube/videos` | YouTube top videos |
| GET | `/charts/youtube/artists` | YouTube top artists |
| GET | `/charts/youtube/tracks` | YouTube top tracks |
| GET | `/charts/amazon/tracks` | Amazon track charts |
| GET | `/charts/amazon/albums` | Amazon album charts |
| GET | `/charts/shazam` | Shazam top 200 |
| GET | `/charts/shazam/:country/cities` | Available Shazam cities |
| GET | `/charts/soundcloud` | SoundCloud charts |
| GET | `/charts/beatport` | Beatport charts |
| GET | `/charts/deezer` | Deezer top 100 |
| GET | `/charts/qq` | QQ Music charts |
| GET | `/charts/tiktok/:chart_type` | TikTok charts (tracks/videos/users) |
| GET | `/charts/airplay/:chart_type` | Radio airplay charts |
| GET | `/charts/twitch/users` | Twitch user charts |

## Charts - CM Scores

| Method | Path | Description |
|--------|------|-------------|
| GET | `/charts/track/:id/:type/cm-score` | Track's CM score by chart type |
| GET | `/charts/artist/:id/:type/cm-score` | Artist's CM score by chart type |
| GET | `/charts/album/:id/:type/cm-score` | Album's CM score by chart type |

## Radio

| Method | Path | Description |
|--------|------|-------------|
| GET | `/radio/:type/:id/airplays` | Radio airplay data |

## Cities

| Method | Path | Description |
|--------|------|-------------|
| GET | `/cities` | List all tracked cities |
| GET | `/city/:id/:source/top-artists` | Top artists in a city |
| GET | `/city/:id/:source/top-tracks` | Top tracks in a city |
