# DDEX Integration

DDEX (Digital Data Exchange) endpoints for content distribution to DSPs.

## Messages

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ddex/messages` | List DDEX messages |
| GET | `/ddex/messages/{id}` | Get message details |
| GET | `/ddex/messages/{id}/download` | Get signed download URL |
| GET | `/ddex/messages/{id}/deliveries` | Delivery logs for a message |
| GET | `/ddex/messages/{id}/status` | Delivery status for a message |
| POST | `/ddex/messages/{id}/deliver` | Queue message delivery |
| POST | `/ddex/messages/{id}/retry` | Retry failed delivery |
| POST | `/ddex/messages/validate` | Validate a DDEX message |
| POST | `/ddex/messages/deliver/bulk` | Queue delivery for multiple messages |

## ERN Generation

| Method | Path | Description |
|--------|------|-------------|
| POST | `/ddex/ern/generate` | Generate ERN for a product |
| POST | `/ddex/ern/generate/batch` | Generate ERN in batch |
| POST | `/ddex/mead/generate` | Queue MEAD generation |
| PUT | `/ddex/mead/metadata` | Update MEAD metadata for entity |

## Providers

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ddex/providers` | List global DDEX providers |
| GET | `/ddex/providers/{id}` | Get provider details |
| GET | `/ddex/providers/{id}/stats` | Provider stats for tenant |
| POST | `/ddex/providers/test` | Test connection to all providers |
| POST | `/ddex/providers/{id}/test` | Test connection to one provider |

## Tenant Provider Configuration

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ddex/tenant-providers` | List tenant provider configs |
| POST | `/ddex/tenant-providers` | Create config |
| PUT | `/ddex/tenant-providers/{id}` | Update config |
| DELETE | `/ddex/tenant-providers/{id}` | Delete config |

## Queue Jobs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ddex/queue` | List queue jobs |
| GET | `/ddex/queue/{id}` | Get queue job |
| GET | `/ddex/queue/{id}/logs` | Get job logs |

## Monitoring

| Method | Path | Description |
|--------|------|-------------|
| GET | `/ddex/dashboard` | Monitoring dashboard |
