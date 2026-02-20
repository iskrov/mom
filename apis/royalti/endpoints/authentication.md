# Authentication

## POST `/auth/login` - Login

Returns a refresh token and list of workspaces the user belongs to.

**Rate limit:** 20 requests per 3 minutes per IP address.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | String | yes | User email |
| password | String | yes | User password |

**Response (200):**

| Field | Type | Description |
|-------|------|-------------|
| message | String | `"Successful"` |
| workspaces | Array | Available workspaces |
| workspaces[].workspaceId | String (UUID) | Workspace identifier |
| workspaces[].name | String | Workspace name |
| workspaces[].status | String | `active`, etc. |
| workspaces[].userType | Array | User type (e.g., `[["Artist"]]`) |
| workspaces[].role | String | User role (e.g., `admin`) |
| refresh_token | String (JWT) | Refresh token (valid 24 hours) |

---

## GET `/auth/authtoken` - Get Access Token

Exchange a refresh token for an access token scoped to a specific workspace.

**Headers:**

| Name | Value |
|------|-------|
| Authorization | `Bearer <REFRESH_TOKEN>` |

**Query Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| currentWorkspace | String (UUID) | yes | Workspace ID to generate token for |

**Response (200):**

```json
{
  "status": "success",
  "message": "Access token generated for My Workspace",
  "data": {
    "access_token": "eyJhbGci..."
  }
}
```

**Token lifetime:** 6 hours.

---

## API Key Authentication (Alternative)

API keys bypass the login flow. Use directly in Authorization header:

```
Authorization: Bearer RWAK_xxxxxxxxxxxxxxxx  (workspace key)
Authorization: Bearer RUAK_xxxxxxxxxxxxxxxx  (user key)
```

- `RWAK` keys = workspace-scoped, never expire (revocable)
- `RUAK` keys = user-scoped, never expire (revocable)

---

## Token Type Detection

The middleware detects token type by prefix:
1. `RWAK` prefix -> Workspace API Key (validated against DB)
2. `RUAK` prefix -> User API Key (validated against DB)
3. `GODK` prefix -> God Key (platform admin only)
4. JWT structure (header.payload.signature) -> JWT token (validated against Redis)

---

## Other Auth Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auth/logout` | Invalidate current token |
| POST | `/auth/forgotpassword` | Request password reset email |
| PATCH | `/auth/resetpassword?code=CODE` | Reset password with verification code |
| POST | `/auth/setpassword` | Set password for new/invited users |
| POST | `/auth/loginlink` | Send magic link login email |
| GET | `/auth/google` | Initiate Google OAuth |
| GET | `/auth/google/callback` | Google OAuth callback |
| GET | `/auth/linkedin` | Initiate LinkedIn OAuth |
| GET | `/auth/linkedin/callback` | LinkedIn OAuth callback |
| GET | `/auth/facebook` | Initiate Facebook OAuth |
| GET | `/auth/facebook/callback` | Facebook OAuth callback |
| GET | `/auth/social/providers` | List connected social providers |
| POST | `/auth/social/{provider}/link` | Link a social account |
| DELETE | `/auth/social/{provider}/unlink` | Unlink a social account |

## Error Responses

| Code | Description |
|------|-------------|
| 401 | `{"error": {"status": 401, "message": "JWT token expired"}}` |
| 403 | Forbidden - insufficient permissions or subscription limits |
