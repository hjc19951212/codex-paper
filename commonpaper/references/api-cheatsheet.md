# Common Paper API Cheatsheet

## Core Endpoints

- `GET /agreements`: primary endpoint for counts, searches, renewals, signer lookups, and summaries
- `GET /agreements/{id}`: agreement detail
- `PATCH /agreements/{id}/void`: void an agreement
- `PATCH /agreements/{id}/reassign`: reassign a recipient
- `PATCH /agreements/{id}/resend_email`: resend a signature email
- `GET /agreements/{id}/history`: agreement history
- `GET /agreements/{id}/download_pdf`: download the signed PDF
- `GET /agreements/{id}/shareable_link`: fetch a shareable link
- `GET /templates`: list templates before creation
- `GET /users`: resolve sender information before creation

## Create Agreement Shape

`POST /agreements` does not use JSON:API. Use this body shape:

```json
{
  "owner_email": "owner@company.com",
  "template_id": "template-uuid",
  "agreement": {
    "agreement_type": "NDA",
    "sender_signer_name": "Jane Smith",
    "sender_signer_title": "CEO",
    "sender_signer_email": "jane@company.com",
    "recipient_email": "recipient@example.com",
    "recipient_name": "John Doe"
  }
}
```

## Query Rules

- Use `page[size]=1` and read `meta.pagination.records` for counts.
- Use `display_status` instead of `status` when presenting results.
- Search both `recipient_organization` and `sender_organization` for “contracts with X”.
- Treat “active/current” agreements as signed and not expired.
- Paginate only when the user explicitly wants a complete list.

## Common Filters

- `filter[status_eq]=signed`
- `filter[agreement_type_eq]=NDA`
- `filter[recipient_organization_cont]=Acme`
- `filter[sender_organization_cont]=Acme`
- `filter[end_date_gteq]=2026-03-17`
- `filter[end_date_lteq]=2026-06-15`
- `filter[expired_eq]=false`
- `page[size]=25`

## Useful Statuses

- `signed`: fully executed
- `draft`: not yet sent
- `in_progress`: active negotiation
- `waiting_for_sender_signature`: awaiting sender signature
- `waiting_for_recipient_signature`: awaiting recipient signature
- `voided_by_sender`: voided
- `declined_by_recipient`: declined

## Common Task Patterns

### Count signed agreements

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[status_eq]=signed' \
  --query 'page[size]=1'
```

Read `meta.pagination.records`.

### Find contracts with a company

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[recipient_organization_cont]=Microsoft' \
  --query 'page[size]=25'
```

Repeat with `sender_organization_cont` if needed.

### Upcoming renewals

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[status_eq]=signed' \
  --query 'filter[end_date_gteq]=2026-03-17' \
  --query 'page[size]=100'
```

Sort by `attributes.end_date`.

### Largest CSA by value

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[agreement_type_eq]=CSA' \
  --query 'filter[status_eq]=signed' \
  --query 'page[size]=100'
```

Sort client-side by `attributes.ai_gmv`.
