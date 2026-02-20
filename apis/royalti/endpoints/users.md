# Users

## GET `/user/` - List Users

List workspace users.

---

## GET `/user/{id}` - Get User

**Path:** `id` (UUID)

---

## GET `/user/{id}/stats` - User Stats

Statistics for a specific user.

---

## GET `/user/{id}/monthly` - User Monthly Stats

Monthly count and royalty share data.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| period | String | `last12months` | `all`, `last12months`, `ytd`, or `custom` |
| startDate | String | - | Custom start date (YYYY-MM-DD, overrides period) |
| endDate | String | - | Custom end date (YYYY-MM-DD, overrides period) |

---

## GET `/user/{id}/artists` - User's Artists

---

## GET `/user/{id}/assets` - User's Assets

---

## GET `/user/{id}/products` - User's Products

---

## Other User Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/user/` | Create user |
| PUT | `/user/{id}` | Update user |
| DELETE | `/user/{id}` | Delete user |
| POST | `/user/bulk` | Bulk create |
| DELETE | `/user/bulk` | Bulk delete |
| GET | `/user/invites` | List workspace invites |
| POST | `/user/invites/{id}/cancel` | Cancel invite |
| POST | `/user/invites/{id}/resend` | Resend invite |
| POST | `/user/{id}/tenant` | Add user to tenant |
| GET | `/user/download` | Download user data |
