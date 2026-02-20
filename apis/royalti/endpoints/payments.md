# Payments

## Payments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/payment/` | List payments |
| GET | `/payment/{id}` | Get payment by ID |
| POST | `/payment/` | Create payment |
| PUT | `/payment/{id}` | Update payment |
| DELETE | `/payment/{id}` | Delete payment |
| POST | `/payment/bulk` | Bulk create payments |
| DELETE | `/payment/bulk` | Bulk delete payments |

## Payment Requests

| Method | Path | Description |
|--------|------|-------------|
| GET | `/payment-request/` | List payment requests |
| GET | `/payment-request/{id}` | Get payment request |
| POST | `/payment-request/` | New payment request |
| PUT | `/payment-request/{id}` | Update payment request |
| DELETE | `/payment-request/{id}` | Delete payment request |
| POST | `/payment-request/{id}/approve` | Approve request |
| POST | `/payment-request/{id}/decline` | Decline request |
| DELETE | `/payment-request/bulk` | Bulk delete requests |

## Payment Settings

| Method | Path | Description |
|--------|------|-------------|
| GET | `/payment-setting/` | List payment settings |
| GET | `/payment-setting/{id}` | Get payment setting |
| POST | `/payment-setting/` | Create payment setting |
| PUT | `/payment-setting/{id}` | Update payment setting |
| DELETE | `/payment-setting/{id}` | Delete payment setting |
| DELETE | `/payment-setting/bulk` | Bulk delete settings |

## VertoFX International Payments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/vertofx/` | List VertoFx integrations |
| GET | `/vertofx/{id}` | Get integration info |
| POST | `/vertofx/` | Add VertoFx integration |
| PUT | `/vertofx/{id}` | Update integration |
| DELETE | `/vertofx/{id}` | Delete integration |
| GET | `/vertofx/beneficiaries` | List beneficiaries |
| GET | `/vertofx/beneficiaries/{id}` | Get beneficiary details |
| POST | `/vertofx/beneficiaries` | Create beneficiary |
| PUT | `/vertofx/beneficiaries/{id}` | Update beneficiary |
| DELETE | `/vertofx/beneficiaries/{id}` | Delete beneficiary |
| POST | `/vertofx/beneficiaries/{id}/link` | Link to user |
| DELETE | `/vertofx/beneficiaries/{id}/unlink` | Unlink from user |
| GET | `/vertofx/wallets` | Get wallets |
| GET | `/vertofx/purpose-codes` | Get purpose codes |
| GET | `/vertofx/payment-requests` | List Verto payment requests |
| GET | `/vertofx/payment-requests/{id}` | Get request details |
| POST | `/vertofx/payment-requests` | Create payment request |
| POST | `/vertofx/payment-requests/v2` | Create payment request (v2) |
