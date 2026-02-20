# Royalty Analysis

All royalty endpoints return data with period-over-period comparison. They share a common set of filter parameters.

## Common Query Parameters

| Name | Type | Description |
|------|------|-------------|
| start | String | Start date (YYYY-MM-DD) |
| end | String | End date (YYYY-MM-DD) |
| artists | String | Comma-separated artist IDs |
| user | String | User ID |
| country | String | Comma-separated country values |
| dsp | String | Comma-separated DSP names |
| type | String | Comma-separated sale types |
| aggregator | String | Comma-separated aggregator values |
| table_name | String | Comma-separated data source tables |
| upc | String | Comma-separated UPC codes |
| isrc | String | Comma-separated ISRC codes |
| periodFilterType | String | `accounting` or `sale` |
| page | Integer | Page number (not on summary) |
| size | Integer | Items per page (not on summary) |

**Note:** Each "grouped by" endpoint omits the parameter it groups on (e.g., `/royalty/artist` omits `artists`, `/royalty/country` omits `country`).

---

## GET `/royalty/` - Summary

Overall royalty totals with period comparison.

**Additional param:** `includePreviousPeriod` - include previous period data

**Response (flat object, not paginated):**

| Field | Type | Description |
|-------|------|-------------|
| Downloads | Integer | Total downloads |
| Downloads_Royalty | Number | Revenue from downloads |
| Streams | Integer | Total streams |
| Streams_Royalty | Number | Revenue from streams |
| Royalty | Number | Total royalty amount |
| Count | Integer | Total play/sale count |
| RoyaltyPercentage | String | % change vs previous period |
| CountPercentage | String | % change vs previous period |
| RatePer1K | Number | Revenue per 1,000 streams |
| PreviousRoyalty | Number | Previous period royalty |
| PreviousCount | Integer | Previous period count |

---

## GET `/royalty/accountingperiod` - By Accounting Month

**Paginated.** Each result item:

| Field | Type | Description |
|-------|------|-------------|
| Month | String | `YYYY-MM` format |
| Royalty | Number | Monthly royalty |
| Count | Integer | Monthly count |
| RoyaltyPercentage | Number | % change |
| CountPercentage | Number | % change |
| RatePer1K | Number | Rate per 1K |
| PreviousRoyalty | Number | Previous period |
| PreviousCount | Integer | Previous period |

---

## GET `/royalty/month` - By Sale Month

Same structure as accounting period, but grouped by when sales actually occurred.

---

## GET `/royalty/artist` - By Artist

Each result: `Track_Artist` (name), `Royalty`, `Count`, `RoyaltyPercentage`, `CountPercentage`, `RatePer1K`, `PreviousRoyalty`, `PreviousCount`

---

## GET `/royalty/asset` - By Asset/Track

Each result: `id`, `Track_Title`, `displayArtist`, `version`, `type`, `Royalty`, `Count`, `RoyaltyPercentage`, `CountPercentage`, `RatePer1K`, `PreviousRoyalty`, `PreviousCount`

---

## GET `/royalty/country` - By Country

Each result: `Country`, `Royalty`, `Count`, `RoyaltyPercentage`, `CountPercentage`, `RatePer1K`, `PreviousRoyalty`, `PreviousCount`

---

## GET `/royalty/dsp` - By DSP/Provider

Each result: `DSP`, `Royalty`, `Count`, `RoyaltyPercentage`, `CountPercentage`, `RatePer1K`, `PreviousRoyalty`, `PreviousCount`

---

## GET `/royalty/product` - By Product

Each result: `id`, `Release_Name`, `displayArtist`, `type`, `Royalty`, `Count`, `RoyaltyPercentage`, `CountPercentage`, `RatePer1K`, `PreviousRoyalty`, `PreviousCount`

---

## GET `/royalty/saletype` - By Sale Type

Each result: `Sale_Type` (Stream, Download, etc.), `Royalty`, `Count`, `RoyaltyPercentage`, `CountPercentage`, `RatePer1K`, `PreviousRoyalty`, `PreviousCount`

---

## GET `/royalty/aggregator` - By Aggregator

Grouped by data source aggregator.

---

## GET `/royalty/source` - By Table Source

Grouped by raw data source table.

---

## Pagination Wrapper (all grouped endpoints)

```json
{
  "results": [...],
  "totalItems": 100,
  "totalPages": 10,
  "currentPage": 1,
  "filteredItems": 10
}
```
