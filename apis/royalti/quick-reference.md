# Royalti.io API - Quick Reference

All paths relative to `https://api.royalti.io`. All endpoints require `Authorization: Bearer <token>`.

## Authentication

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/login` | Login, get refresh token + workspace list |
| GET | `/auth/authtoken?currentWorkspace=ID` | Exchange refresh token for access token |
| POST | `/auth/logout` | Invalidate token |
| POST | `/auth/forgotpassword` | Request password reset |
| PATCH | `/auth/resetpassword` | Reset password with code |
| POST | `/auth/setpassword` | Set password (new users) |
| POST | `/auth/loginlink` | Send magic link |
| GET | `/auth/google` | Initiate Google OAuth |
| GET | `/auth/linkedin` | Initiate LinkedIn OAuth |
| GET | `/auth/facebook` | Initiate Facebook OAuth |
| GET | `/auth/social/providers` | List connected social providers |
| POST | `/auth/social/{provider}/link` | Link social provider |
| DELETE | `/auth/social/{provider}/unlink` | Unlink social provider |

## Artists

| Method | Path | Description |
|--------|------|-------------|
| GET | `/artist/` | List/search artists (paginated, sortable) |
| GET | `/artist/{id}` | Get artist by ID |
| POST | `/artist/` | Create artist |
| PUT | `/artist/{id}` | Update artist |
| DELETE | `/artist/{id}` | Delete artist |
| GET | `/artist/stats/{id}` | Artist financial/catalog stats |
| GET | `/artist/{id}/assets` | Artist's tracks/recordings |
| GET | `/artist/{id}/products` | Artist's albums/singles |
| GET | `/artist/{id}/splits` | All default splits for artist |
| GET | `/artist/{id}/splits/{type}` | Default splits by type |
| POST | `/artist/{id}/splits` | Create default splits |
| PUT | `/artist/{id}/splits/{type}` | Update default splits |
| DELETE | `/artist/{id}/splits/{type}` | Delete default splits |
| POST | `/artist/bulk` | Create artists in bulk |
| DELETE | `/artist/bulk` | Delete artists in bulk |
| PUT | `/artist/bulk/splits` | Update splits in bulk |
| POST | `/artist/merge` | Merge artists |
| GET | `/artist/download` | Download artists CSV |

## Assets (Tracks/Recordings)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/asset` | List/search assets (paginated, sortable) |
| GET | `/asset/{id}` | Get asset by ID |
| POST | `/asset` | Create asset |
| PUT | `/asset/{id}` | Update asset |
| DELETE | `/asset/{id}` | Delete asset |
| GET | `/asset/{id}/stats` | Asset statistics |
| GET | `/asset/{id}/works` | Get works for a recording |
| POST | `/asset/{id}/media` | Upload media for asset |
| DELETE | `/asset/{id}/media` | Delete media for asset |
| PUT | `/asset/{id}/artists` | Update asset artists |
| PUT | `/asset/{id}/default-split` | Set default split |
| POST | `/asset/bulk` | Create assets in bulk |
| DELETE | `/asset/bulk` | Delete assets in bulk |
| PUT | `/asset/bulk/splits` | Set bulk splits |
| DELETE | `/asset/bulk/splits` | Delete bulk splits |
| PUT | `/asset/bulk/default-split` | Set default split for multiple |
| GET | `/asset/download` | Download assets CSV |

## Products (Albums/Singles)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/product/` | List/search products (paginated, sortable) |
| GET | `/product/{id}` | Get product by ID |
| POST | `/product/` | Create product |
| PUT | `/product/{id}` | Update product |
| DELETE | `/product/{id}` | Delete product |
| GET | `/product/{id}/stats` | Product financial stats |
| POST | `/product/{id}/media` | Upload product media |
| DELETE | `/product/{id}/media` | Delete product media |
| PUT | `/product/{id}/artists` | Update product artists |
| PUT | `/product/{id}/assets` | Update product tracklist |
| PUT | `/product/{id}/default-split` | Set default split from artist |
| POST | `/product/bulk` | Create products in bulk |
| DELETE | `/product/bulk` | Delete products in bulk |
| PUT | `/product/bulk/splits` | Update bulk splits |
| DELETE | `/product/bulk/splits` | Delete splits from bulk |
| GET | `/product/download` | Download products CSV |
| GET | `/product/{id}/metadata` | Download product metadata |

## Releases (Content Distribution Workflow)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/releases` | List releases (paginated, filterable by status/format) |
| GET | `/releases/{id}` | Get release by ID |
| POST | `/releases` | Create release (starts as draft) |
| PUT | `/releases/{id}` | Update release |
| DELETE | `/releases/{id}` | Delete release |
| GET | `/releases/stats` | Release statistics (counts by status) |
| POST | `/releases/{id}/submit` | Submit release for review |
| POST | `/releases/{id}/review` | Review release (admin) |
| POST | `/releases/{id}/revert` | Revert release status (admin) |
| POST | `/releases/{id}/feedback` | Add feedback to release |
| POST | `/releases/{id}/media` | Upload media files |
| POST | `/releases/{id}/media-links` | Submit media via URL links |
| POST | `/releases/{id}/tracks` | Add track to release |
| PUT | `/releases/{id}/tracks/{trackId}` | Update track |
| DELETE | `/releases/{id}/tracks/{trackId}` | Delete track |
| PUT | `/releases/{id}/tracks/reorder` | Reorder tracks |
| POST | `/releases/{id}/tracks/{trackId}/media` | Upload track media |
| POST | `/releases/{id}/link-asset` | Link existing asset to release |

## Royalty Analysis

| Method | Path | Description |
|--------|------|-------------|
| GET | `/royalty/` | Royalties summary (totals, streams, downloads) |
| GET | `/royalty/accountingperiod` | Royalties grouped by accounting period |
| GET | `/royalty/month` | Royalties grouped by sale month |
| GET | `/royalty/aggregator` | Royalties grouped by aggregator |
| GET | `/royalty/artist` | Royalties grouped by artist |
| GET | `/royalty/asset` | Royalties grouped by asset/track |
| GET | `/royalty/country` | Royalties grouped by country |
| GET | `/royalty/dsp` | Royalties grouped by DSP/provider |
| GET | `/royalty/product` | Royalties grouped by product |
| GET | `/royalty/saletype` | Royalties grouped by sale type |
| GET | `/royalty/source` | Royalties grouped by data source |

## Accounting

| Method | Path | Description |
|--------|------|-------------|
| GET | `/accounting/getcurrentdue` | Current due per user |
| GET | `/accounting/gettotaldue` | Total due across all users |
| GET | `/accounting/{id}/stats` | User accounting statistics |
| POST | `/accounting/refresh` | Refresh accounting data (sync) |
| POST | `/accounting/refresh/async` | Refresh accounting (async pipeline) |
| GET | `/accounting/transactions` | Tenant transactions |
| GET | `/accounting/transactions/monthly` | Monthly transaction breakdown |
| GET | `/accounting/transactions/summary` | All-time transaction summary |

## Splits

| Method | Path | Description |
|--------|------|-------------|
| GET | `/split/` | List splits (paginated, filterable) |
| GET | `/split/{id}` | Get split by ID |
| POST | `/split/` | Create split |
| PUT | `/split/{id}` | Update split |
| DELETE | `/split/{id}` | Delete split |
| DELETE | `/split/bulk` | Bulk delete splits |
| POST | `/split/default` | Create default splits |
| POST | `/split/match` | Match splits to royalty data |
| DELETE | `/split/catalog/bulk` | Bulk delete catalog splits |

## Revenues & Expenses

| Method | Path | Description |
|--------|------|-------------|
| GET | `/revenue/` | List revenues |
| GET | `/revenue/{id}` | Get revenue by ID |
| POST | `/revenue/` | Create revenue |
| PUT | `/revenue/{id}` | Update revenue |
| DELETE | `/revenue/{id}` | Delete revenue |
| POST | `/revenue/bulk` | Create bulk revenues |
| DELETE | `/revenue/bulk` | Delete bulk revenues |
| GET | `/expense/` | List expenses |
| GET | `/expense/{id}` | Get expense by ID |
| POST | `/expense/` | Create expense |
| PUT | `/expense/{id}` | Update expense |
| POST | `/expense/bulk` | Create bulk expenses |
| DELETE | `/expense/bulk` | Delete bulk expenses |

## Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/user/` | List users |
| GET | `/user/{id}` | Get user by ID |
| POST | `/user/` | Create user |
| PUT | `/user/{id}` | Update user |
| DELETE | `/user/{id}` | Delete user |
| GET | `/user/{id}/stats` | User statistics |
| GET | `/user/{id}/monthly` | User monthly stats |
| GET | `/user/{id}/artists` | User's artists |
| GET | `/user/{id}/assets` | User's assets |
| GET | `/user/{id}/products` | User's products |
| POST | `/user/bulk` | Create users in bulk |
| DELETE | `/user/bulk` | Delete users in bulk |

## Royalty Sources

| Method | Path | Description |
|--------|------|-------------|
| GET | `/sources` | List tenant royalty sources |
| GET | `/sources/{id}` | Get tenant source by ID |
| POST | `/sources` | Add tenant source |
| PUT | `/sources/{id}` | Update tenant source |
| POST | `/sources/{id}/activate` | Activate source |
| POST | `/sources/{id}/deactivate` | Deactivate source |
