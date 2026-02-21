# SoundCloud API - Quick Reference

All paths relative to `https://api.soundcloud.com`

## Authentication

| Method | Path | Description |
|--------|------|-------------|
| GET | `/connect` | Initiate OAuth authorization |
| POST | `/oauth2/token` | Exchange code/credentials for access token |
| POST | `https://secure.soundcloud.com/sign-out` | Revoke access token |

## Me (Authenticated User)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/me` | Current user profile |
| GET | `/me/activities` | User activities feed |
| GET | `/me/activities/all/own` | User's own recent activities |
| GET | `/me/activities/tracks` | Track-related activities |
| GET | `/me/connections` | Connected social accounts |
| GET | `/me/connections/:connection_id` | Specific social connection |
| GET | `/me/likes/tracks` | Liked tracks |
| GET | `/me/favorites/ids` | Favorited track IDs (deprecated) |
| GET | `/me/followings` | Users followed by current user |
| GET | `/me/followings/tracks` | Recent tracks from followed users |
| GET | `/me/followings/:user_id` | Check specific following (deprecated) |
| PUT | `/me/followings/:user_id` | Follow a user |
| DELETE | `/me/followings/:user_id` | Unfollow a user |
| GET | `/me/followers` | Current user's followers |
| GET | `/me/followers/:follower_id` | Specific follower (deprecated) |
| GET | `/me/playlists` | Current user's playlists |
| GET | `/me/playlists/:playlist_id` | Specific playlist (deprecated) |
| GET | `/me/tracks` | Current user's tracks |
| GET | `/me/tracks/:track_id` | Specific track (deprecated) |

## Tracks

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tracks` | Search/list tracks |
| POST | `/tracks` | Upload a new track |
| GET | `/tracks/:track_id` | Get track details |
| PUT | `/tracks/:track_id` | Update track metadata |
| DELETE | `/tracks/:track_id` | Delete a track |
| GET | `/tracks/:track_id/streams` | Get stream URLs (MP3, HLS, Opus) |
| GET | `/tracks/:track_id/comments` | Get track comments |
| POST | `/tracks/:track_id/comments` | Post a comment on a track |
| GET | `/tracks/:track_id/favoriters` | Users who liked the track |
| GET | `/tracks/:track_id/reposters` | Users who reposted the track |
| GET | `/tracks/:track_id/related` | Get related/similar tracks |

## Playlists

| Method | Path | Description |
|--------|------|-------------|
| GET | `/playlists` | Search/list playlists |
| POST | `/playlists` | Create a new playlist |
| GET | `/playlists/:playlist_id` | Get playlist details |
| PUT | `/playlists/:playlist_id` | Update playlist |
| DELETE | `/playlists/:playlist_id` | Delete a playlist |
| GET | `/playlists/:playlist_id/tracks` | Get playlist tracks |
| GET | `/playlists/:playlist_id/reposters` | Users who reposted the playlist |

## Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users` | Search/list users |
| GET | `/users/:user_id` | Get user profile |
| GET | `/users/:user_id/comments` | User's comments |
| GET | `/users/:user_id/favorites` | User's favorites (deprecated) |
| GET | `/users/:user_id/followers` | User's followers |
| GET | `/users/:user_id/followings` | Users followed by this user |
| GET | `/users/:user_id/followings/:following_id` | Specific following (deprecated) |
| GET | `/users/:user_id/playlists` | User's playlists |
| GET | `/users/:user_id/tracks` | User's tracks |
| GET | `/users/:user_id/web-profiles` | User's external profile links |
| GET | `/users/:user_id/likes/tracks` | User's liked tracks |

## Likes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/likes/tracks/:track_id` | Like a track |
| DELETE | `/likes/tracks/:track_id` | Unlike a track |
| POST | `/likes/playlists/:playlist_id` | Like a playlist |
| DELETE | `/likes/playlists/:playlist_id` | Unlike a playlist |

## Reposts

| Method | Path | Description |
|--------|------|-------------|
| POST | `/reposts/tracks/:track_id` | Repost a track |
| DELETE | `/reposts/tracks/:track_id` | Remove track repost |
| POST | `/reposts/playlists/:playlist_id` | Repost a playlist |
| DELETE | `/reposts/playlists/:playlist_id` | Remove playlist repost |

## Search & Resolve

| Method | Path | Description |
|--------|------|-------------|
| GET | `/tracks` | Search tracks (with `q` parameter) |
| GET | `/users` | Search users (with `q` parameter) |
| GET | `/playlists` | Search playlists (with `q` parameter) |
| GET | `/resolve` | Resolve SoundCloud URL to API resource |
