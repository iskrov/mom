# Authentication

## POST `/token`

Get an access token using your refresh token. Access tokens expire after 1 hour.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refreshtoken | String | yes | Your Chartmetric refresh token (assigned on signup) |

**Response:**

| Field | Type | Description |
|-------|------|-------------|
| token | String | Access token (valid 1 hour) |
| expires_in | Integer | Seconds until expiration |
| scope | String | Token scope |

**Usage:**

```bash
# Step 1: Get access token
curl -X POST https://api.chartmetric.com/api/token \
  -H "Content-Type: application/json" \
  -d '{"refreshtoken": "YOUR_REFRESH_TOKEN"}'

# Step 2: Use access token on all subsequent requests
curl -H "Authorization: Bearer ACCESS_TOKEN" \
  https://api.chartmetric.com/api/artist/2316
```

**Notes:**
- Refresh tokens do not expire but should be kept secret
- Access tokens must be refreshed every hour
- All other endpoints require `Authorization: Bearer <token>` header
