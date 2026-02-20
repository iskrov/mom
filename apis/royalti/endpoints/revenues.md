# Revenues & Expenses

## GET `/revenue/` - List Revenues

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| q | String | - | Search query |
| page | Integer | 1 | Page number |
| size | Integer | 10 | Items per page |
| sort | String | `transactionDate` | Sort field |
| order | String | `desc` | `asc` or `desc` |
| source | String | - | Filter by revenue source |
| artist | String | - | Filter by artist ID |
| asset | String | - | Filter by asset ID |
| product | String | - | Filter by product ID |
| currency | String | - | Filter by currency |
| dateFrom | String | - | Start date filter |
| dateTo | String | - | End date filter |
| include | String | - | `Artist`, `Asset`, `Product` (include related data) |

---

## GET `/revenue/{id}` - Get Revenue

**Path:** `id` - Revenue record ID

**Query:** `include` - `Artist`, `Asset`, `Product`, `Splits`

---

## POST `/revenue/` - Create Revenue

Create a revenue record manually.

---

## PUT `/revenue/{id}` - Update Revenue

---

## DELETE `/revenue/{id}` - Delete Revenue

---

## POST `/revenue/bulk` - Bulk Create

---

## DELETE `/revenue/bulk` - Bulk Delete

---

## Expenses

| Method | Path | Description |
|--------|------|-------------|
| GET | `/expense/` | List expenses |
| GET | `/expense/{id}` | Get expense by ID |
| POST | `/expense/` | Create expense |
| PUT | `/expense/{id}` | Update expense |
| POST | `/expense/bulk` | Bulk create |
| DELETE | `/expense/bulk` | Bulk delete |
