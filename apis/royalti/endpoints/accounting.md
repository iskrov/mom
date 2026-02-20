# Accounting

Financial summaries, balances, and transaction history.

## GET `/accounting/getcurrentdue` - Current Due Per User

List users with their current outstanding balances (excludes tenant owner).

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| q | String | - | Search users by name |
| page | Integer | 1 | Page number |
| size | Integer | 10 | Items per page |
| sort | String | `due` | Sort field: `gross`, `net`, `paid`, `due`, `lastCalculatedAt` |
| order | String | `DESC` | `ASC` or `DESC` |

---

## GET `/accounting/gettotaldue` - Total Due Amount

Total amount due across all tenant users.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| method | String | `auto` | `cache` (fast, 10-50ms), `bigquery` (comprehensive, 500-2000ms), `auto` (tries cache first) |

---

## GET `/accounting/{id}/stats` - User Accounting Stats

Detailed accounting for a specific user.

**Path:** `id` - TenantUser ID

**Query Parameters:**

| Name | Type | Description |
|------|------|-------------|
| include | String | `royalty` to include detailed royalty summary |
| forceRefresh | Boolean | Force recalculation (ignore cache) |

---

## POST `/accounting/refresh` - Refresh Accounting (Sync)

Synchronously recalculate all accounting data.

---

## POST `/accounting/refresh/async` - Refresh Accounting (Async)

Trigger async accounting pipeline. Returns immediately.

---

## GET `/accounting/transactions` - Tenant Transactions

All transactions: payments, revenues, expenses, payment requests.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | Integer | 1 | Page number |
| size | Integer | 10 | Items per page |
| start | String | - | Start date (YYYY-MM-DD) |
| end | String | - | End date (YYYY-MM-DD) |

---

## GET `/accounting/transactions/monthly` - Monthly Breakdown

Transactions aggregated by month with type breakdown (payment, revenue, expense) and net amount.

**Query Parameters:**

| Name | Type | Description |
|------|------|-------------|
| start | String | Start date (YYYY-MM-DD) |
| stop | String | End date (YYYY-MM-DD). Note: parameter is named `stop`, not `end` |

---

## GET `/accounting/transactions/summary` - All-Time Summary

Aggregated totals: total payments, revenues, expenses, and net amount. No parameters - returns all-time summary.
