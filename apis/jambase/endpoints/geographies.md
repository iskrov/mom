# Geographies

## GET `/geographies/cities` - Search Cities

**Requirement:** Must include `geoCityName` or at least one geo parameter.

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| page | Integer | 1 | Page number |
| perPage | Integer | 40 | Results per page (max: 100) |
| geoCityName | String | - | City name search |
| cityHasUpcomingEvents | Boolean | - | Only cities with upcoming events |
| geoCountryIso2 | String | - | Country filter |
| geoCountryIso3 | String | - | Country filter (3-letter) |
| geoIp | String | - | IP for geo lookup |
| geoLatitude | Number | - | Latitude |
| geoLongitude | Number | - | Longitude |
| geoMetroId | String | - | Metro ID |
| geoRadiusAmount | Number | 60 | Radius |
| geoRadiusUnits | String | `mi` | `mi` or `km` |
| geoStateIso | String | - | State code |

---

## GET `/geographies/metros` - List Metro Areas

**Query Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| metroHasUpcomingEvents | Boolean | - | Only metros with events |
| cityHasUpcomingEvents | Boolean | - | Only metros whose cities have events |
| expandMetroCities | Boolean | false | Include cities within each metro |

---

## GET `/geographies/states` - List States/Provinces

Returns US states, Canadian provinces, and Australian states/territories.

**Query Parameters:**

| Name | Type | Description |
|------|------|-------------|
| stateHasUpcomingEvents | Boolean | Only states with events |

**Supported regions (78 total):** All 50 US states + DC + territories (PR, GU, VI, AS, MP), all Canadian provinces/territories, all Australian states/territories.

---

## GET `/geographies/countries` - List Countries

**Query Parameters:**

| Name | Type | Description |
|------|------|-------------|
| countryHasUpcomingEvents | Boolean | Only countries with events |
