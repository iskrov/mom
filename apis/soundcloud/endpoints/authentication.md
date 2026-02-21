# Authentication

## GET `/connect`

Initiate OAuth 2.1 authorization. Redirects the user to SoundCloud's authorization page.

**Parameters:**

| Name | In | Type | Required | Description |
|------|------|------|----------|-------------|
| client_id | query | String | yes | Your application client ID |
| redirect_uri | query | String | yes | Registered redirect URI |
| response_type | query | String | yes | `code`, `token`, or `code_and_token` |
| scope | query | String | yes | Requested permission scope |
| state | query | String | no | CSRF protection state parameter |
| code_challenge | query | String | yes (PKCE) | S256 hash of code verifier |
| code_challenge_method | query | String | yes (PKCE) | Must be `S256` |

**Responses:**

| Code | Description |
|------|-------------|
| 302 | Redirect to authorization page |
| 401 | Unauthorized - invalid client_id |

---

## POST `/oauth2/token`

Exchange authorization code, refresh token, or client credentials for an access token.

**Request Body** (`application/x-www-form-urlencoded`):

### Authorization Code Grant

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| grant_type | String | yes | `authorization_code` |
| authorization_code | String | yes | Code received from `/connect` redirect |
| client_id | String | yes | Your application client ID |
| client_secret | String | yes | Your application secret |
| redirect_uri | String | yes | Must match the redirect URI used in `/connect` |
| code_verifier | String | yes (PKCE) | Original code verifier for PKCE |

### Refresh Token Grant

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| grant_type | String | yes | `refresh_token` |
| refresh_token | String | yes | Refresh token from previous token response |
| client_id | String | yes | Your application client ID |
| client_secret | String | yes | Your application secret |
| redirect_uri | String | yes | Registered redirect URI |

### Client Credentials Grant

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| grant_type | String | yes | `client_credentials` |

Also requires HTTP Basic Auth header: `Authorization: Basic base64(client_id:client_secret)`

**Rate limit:** 50 tokens per 12h per app, 30 tokens per 1h per IP address.

### Password Grant (Deprecated)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| grant_type | String | yes | `password` |
| username | String | yes | User's email or username |
| password | String | yes | User's password |
| client_id | String | yes | Your application client ID |
| client_secret | String | yes | Your application secret |
| redirect_uri | String | yes | Registered redirect URI |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| access_token | String | OAuth access token (~1 hour validity) |
| token_type | String | `Bearer` |
| expires_in | Integer | Seconds until token expiration (typically 3600) |
| refresh_token | String | Single-use token for refreshing access (optional) |
| scope | String | Granted permission scope |

**Error Response:**

| Field | Type | Description |
|-------|------|-------------|
| error | String | Error type identifier |
| error_description | String | Human-readable error message |

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Token issued successfully |
| 400 | Bad Request - invalid grant_type or parameters |
| 401 | Unauthorized - invalid client credentials |

**Usage:**

```bash
# Authorization Code Flow
curl -X POST https://secure.soundcloud.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=YOUR_REDIRECT_URI" \
  -d "code=AUTH_CODE" \
  -d "code_verifier=YOUR_CODE_VERIFIER"

# Client Credentials Flow
curl -X POST https://secure.soundcloud.com/oauth/token \
  -H "Authorization: Basic $(echo -n 'CLIENT_ID:CLIENT_SECRET' | base64)" \
  -d "grant_type=client_credentials"

# Refresh Token
curl -X POST https://secure.soundcloud.com/oauth/token \
  -d "grant_type=refresh_token" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=YOUR_REDIRECT_URI" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"
```

**Notes:**
- Each refresh token is single-use; a new refresh token is returned with each access token
- Tokens expire in approximately 1 hour
- All clients are treated as confidential, requiring `client_secret`
- PKCE (code_challenge/code_verifier) is mandatory for Authorization Code flow

---

## POST `https://secure.soundcloud.com/sign-out`

Revoke an access token (sign out).

**Request Body** (`application/json`):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| access_token | String | yes | The access token to revoke |

**Responses:**

| Code | Description |
|------|-------------|
| 200 | Token successfully revoked |
| 401 | Unauthorized - invalid token |
