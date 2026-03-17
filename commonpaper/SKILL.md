---
name: commonpaper
description: Query and manage Common Paper agreements from Codex through the Common Paper REST API. Use when the user asks about Common Paper, contracts, agreements, NDAs, CSAs, renewals, signers, deal values, agreement links, or wants to create, void, reassign, or resend agreements. Also use when the user mentions Common Paper directly or asks contract questions that require searching their Common Paper account.
---

# Common Paper

## Overview

Use this skill to answer Common Paper contract questions and to execute Common Paper agreement actions from Codex. Prefer the bundled script over ad hoc `curl` because it handles token storage, request encoding, and safer defaults.

## Security Rules

Follow these rules on every task:

1. Never print, echo, or summarize the full API token in chat output.
2. Never pass the API token as a literal CLI argument.
3. Save or read the token only through `scripts/commonpaper_api.py`.
4. Confirm all write operations before sending them.
5. Sanitize user-provided filters before turning them into API query values.

## Quick Start

If the token is not set yet, run this in a TTY so the token stays hidden while typing:

```bash
python3 scripts/commonpaper_api.py save-token
```

Validate the stored token:

```bash
python3 scripts/commonpaper_api.py validate-token
```

Show the paths this skill uses:

```bash
python3 scripts/commonpaper_api.py show-paths
```

By default the token lives at `$CODEX_HOME/skills/commonpaper/cp-api-token`. If the skill is being tested outside the installed location, set `COMMONPAPER_SKILL_HOME` to the installed skill directory before running commands.

## Read Workflow

For read-only questions:

1. Validate or load the saved token.
2. Map the user request to `GET /agreements`, `GET /templates`, `GET /users`, or an agreement detail endpoint.
3. Push filtering to the API first.
4. Use `page[size]=1` and `meta.pagination.records` for counts.
5. Paginate only when the user explicitly needs a full list.
6. Present `display_status` instead of internal `status` when showing results.

Example: count signed agreements.

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[status_eq]=signed' \
  --query 'page[size]=1'
```

Example: find agreements with a company.

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[recipient_organization_cont]=Acme' \
  --query 'page[size]=25'
```

Search both `recipient_organization` and `sender_organization` when the user says “with Company X”, because either side may be the counterparty.

## Write Workflow

For create, void, reassign, resend, or other state-changing actions:

1. Resolve missing IDs first with read endpoints.
2. Confirm the exact action and target with the user.
3. Build the request body in a JSON file instead of inline shell text.
4. Execute the write with `scripts/commonpaper_api.py request ... --body-file ...`.
5. Summarize the outcome and include the agreement link when available.

For agreement creation:

1. Look up the sender with `GET /users`.
2. Look up the template with `GET /templates`.
3. Confirm owner email, template, recipient email, recipient name, and agreement type.
4. Send `POST /agreements`.

Example pattern:

```bash
python3 scripts/commonpaper_api.py request POST /agreements --body-file /absolute/path/to/body.json
```

Always confirm before calling:

- `PATCH /agreements/{id}/void`
- `PATCH /agreements/{id}/reassign`
- `PATCH /agreements/{id}/resend_email`

## Response Rules

- Use readable summaries or short tables.
- Include agreement type, counterparty, `display_status`, effective date, and end date for lists.
- Include signer name, email, title, and organization for signer lookups.
- Sort date-driven answers chronologically.
- Include `links.agreement_url` when it helps the user open the agreement quickly.

## References

- Read `references/api-cheatsheet.md` for endpoints, filters, statuses, and common query patterns.
- Use `scripts/commonpaper_api.py --help` for the exact command surface.
