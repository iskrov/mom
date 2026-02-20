# Royalti.io API

Music royalty management platform for tracking royalties, managing catalogs, processing payments, and distributing content via DDEX. Designed for labels, distributors, and artists.

- **Base URL:** `https://api.royalti.io`
- **Dev URL:** `https://api-dev.royalti.io`
- **Docs:** https://apidocs.royalti.io/introduction
- **Format:** JSON requests and responses, HTTPS only (TLSv1.2+)
- **API Version:** 2.6.0

## Authentication

JWT-based system with multiple token types:

| Token Type | Prefix | Lifetime | Use Case |
|------------|--------|----------|----------|
| JWT Access Token | (none) | 6 hours | Standard API calls |
| JWT Refresh Token | (none) | 24 hours | Exchange for access tokens |
| Workspace API Key | `RWAK` | Never expires | Server-to-server integrations |
| User API Key | `RUAK` | Never expires | User-scoped API access |

```bash
# Step 1: Login to get refresh token + workspace list
curl -X POST https://api.royalti.io/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "you@example.com", "password": "yourpassword"}'

# Step 2: Exchange refresh token for access token (select workspace)
curl https://api.royalti.io/auth/authtoken?currentWorkspace=WORKSPACE_UUID \
  -H "Authorization: Bearer REFRESH_TOKEN"

# Step 3: Use access token on all requests
curl https://api.royalti.io/artist/ \
  -H "Authorization: Bearer ACCESS_TOKEN"

# Alternative: Use API key directly (no login needed)
curl https://api.royalti.io/artist/ \
  -H "Authorization: Bearer RWAK_xxxxxxxxxxxxxxxx"
```

## Rate Limits

- Login endpoint: **20 requests per 3 minutes per IP**
- Other endpoints: fair usage / throttling (specific limits not published)

## Core Data Model

```
Artist
  ├── Asset (track/recording, identified by ISRC)
  │     └── Split (revenue share per user)
  └── Product (album/single/EP, identified by UPC)
        ├── Assets (tracklist)
        └── Split (revenue share per user)

Release (content submission workflow)
  └── Tracks (release-specific track entries)

Royalty Data (imported from aggregators/DSPs)
  ├── grouped by: artist, asset, product, country, DSP, sale type, month
  └── metrics: count (streams/sales), royalty amount, rate per 1K
```

## What This API Provides (Music-Focused)

| Category | Data Available |
|----------|----------------|
| **Catalog Management** | Artists, assets (tracks), products (albums), releases, metadata (ISRC, UPC, genres, contributors) |
| **Royalty Analytics** | Revenue by artist, track, product, country, DSP, sale type, time period |
| **Financial** | Amounts due, paid, gross/net earnings, transaction history, monthly breakdowns |
| **Revenue Splits** | Configurable splits per asset/product, temporal splits, conditional splits |
| **Content Distribution** | DDEX integration, release workflow (draft->review->publish), media management |
| **Payments** | Payment processing, VertoFX international payments, multi-currency |

## Endpoint Categories

| Category | Endpoints | Description |
|----------|-----------|-------------|
| [Authentication](endpoints/authentication.md) | 15+ | Login, tokens, OAuth, password management |
| [Artists](endpoints/artists.md) | 18 | Artist CRUD, stats, assets, products, splits |
| [Assets](endpoints/assets.md) | 17 | Track/recording CRUD, stats, media, splits |
| [Products](endpoints/products.md) | 16 | Album/single CRUD, stats, media, splits |
| [Releases](endpoints/releases.md) | 15 | Content submission workflow, tracks, media |
| [Royalty Analysis](endpoints/royalty-analysis.md) | 10 | Revenue analytics by multiple dimensions |
| [Accounting](endpoints/accounting.md) | 8 | Financial summaries, transactions, balances |
| [Splits](endpoints/splits.md) | 8 | Revenue split configuration and management |
| [Revenues](endpoints/revenues.md) | 6 | Revenue record management |
| [Users](endpoints/users.md) | 12 | User management, stats, invitations |
| [DDEX](endpoints/ddex.md) | 19 | DDEX content distribution integration |
| [Payments](endpoints/payments.md) | 14 | Payment processing and requests |

**Total: ~160 endpoints** (largest API of the three providers)

See [quick-reference.md](quick-reference.md) for a compact endpoint table.
