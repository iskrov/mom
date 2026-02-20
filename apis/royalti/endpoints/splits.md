# Splits (Revenue Distribution)

Revenue splits define how royalty income is divided among users for a specific asset or product.

## GET `/split/` - List Splits

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | Integer | 1 | Page number |
| size | Integer | 10 | Items per page |
| include | String | - | `count` to include total count |
| asset | UUID | - | Filter by asset |
| product | UUID | - | Filter by product |
| type | String | - | Filter by revenue split type |
| user | UUID | - | Filter by user |
| q | String | - | Search query |
| sort | String | - | Sort field |
| order | String | - | `asc` or `desc` |

---

## GET `/split/{id}` - Get Split

**Path:** `id` (UUID)

---

## POST `/split/` - Create Split

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| asset | UUID | conditional | Asset ID (required if no product) |
| product | UUID | conditional | Product ID (required if no asset) |
| split | Object[] | yes | `[{ user: UUID, share: Number }]` - must total 100% |
| type | String | no | Revenue type (e.g., `Publishing`, `YouTube`, `Live`) |
| name | String | no | Split name/description |
| startDate | Date | no | Start date (INCLUSIVE) |
| endDate | Date | no | End date (EXCLUSIVE) |
| conditions | Array | no | Conditional split rules (see below) |
| contract | String | no | Contract details |
| ContractId | String | no | Contract ID |
| memo | String | no | Notes |

**Temporal split rules:**
- `startDate` is inclusive (split active from this date)
- `endDate` is exclusive (split ends before this date)
- Adjacent splits: next split can start on previous split's `endDate`
- Omit both dates for permanent/indefinite splits
- Overlapping temporal splits for same asset/product/type are prevented

**Conditions object:**

| Field | Type | Description |
|-------|------|-------------|
| mode | String | Condition mode |
| memo | String | Description |
| territories | Array | Territory filter objects |
| dsps | Array | DSP filter objects |
| usageTypes | Array | Usage type filter objects |
| customDimension | String | Custom dimension key |
| customValues | Array | Custom dimension values |

---

## Other Split Endpoints

| Method | Path | Description |
|--------|------|-------------|
| PUT | `/split/{id}` | Update split |
| DELETE | `/split/{id}` | Delete split |
| DELETE | `/split/bulk` | Bulk delete splits |
| POST | `/split/default` | Create default splits |
| POST | `/split/match` | Match splits to royalty data |
| DELETE | `/split/catalog/bulk` | Bulk delete catalog splits |
