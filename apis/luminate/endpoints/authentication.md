# Authentication

## POST `/auth`

Get an access token. Tokens are valid for 24 hours.

**Request Headers:**

| Name | Value | Required |
|------|-------|----------|
| content-type | `application/x-www-form-urlencoded` | yes |
| x-api-key | Your API key | yes |
| accept | `application/json` | yes |

**Request Body (form-encoded):**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | String | yes | Account email address |
| password | String | yes | Account password |

**Response (200):**

```json
{
  "access_token": "eyJhbGci...",
  "expires_in": 86400
}
```

**Error Response (401):**

```json
{
  "error": {
    "errors": [{"error_code": "00018", "error_type": "Unauthorized", "message": "API key invalid or not provided."}],
    "code": 401,
    "message": "Unauthorized"
  }
}
```

**Usage on all subsequent requests:**

```bash
curl https://api.luminatedata.com/artists/ARTIST_ID \
  -H "x-api-key: YOUR_API_KEY" \
  -H "authorization: YOUR_ACCESS_TOKEN" \
  -H "Accept: application/vnd.luminate-data.svc-apibff.v1+json"
```

**Notes:**
- All three headers (`x-api-key`, `authorization`, `Accept`) are required on every data request
- The `Accept` header must be exactly: `application/vnd.luminate-data.svc-apibff.v1+json`
- Contact api-support@luminatedata.com for access issues
