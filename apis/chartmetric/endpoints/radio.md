# Radio

## GET `/radio/:type/:id/airplays` - Airplay Data

Radio airplay/spin data. Also see [charts.md](charts.md) for radio airplay chart endpoints.

**Parameters:**

| Name | Type | Required | Description |
|------|------|----------|-------------|
| type | String | yes | Entity type (e.g., `track`, `artist`) |
| id | Integer | yes | Chartmetric entity ID |

**Notes:**
- Radio data covers terrestrial and satellite radio stations
- Airplay chart data is also available via `/charts/airplay/:chart_type`
