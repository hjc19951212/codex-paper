# Common Paper for Codex

[中文说明](./README.zh-CN.md)

Codex-native Common Paper skill for querying agreements, tracking renewals, finding signers, and safely running contract actions with the Common Paper REST API.

Adapted from the open-source Claude Code skill at [CommonPaper/claude-skill](https://github.com/CommonPaper/claude-skill), with workflow, installation, and credential handling rewritten for Codex.

## Features

- Query Common Paper agreements in natural language through Codex
- Count, search, and summarize NDAs, CSAs, renewals, signers, and deal values
- Handle write operations with explicit confirmation gates
- Store and validate the API token locally for Codex use
- Use a bundled Python helper instead of ad hoc shell commands

## Structure

- `commonpaper/` — installable Codex skill folder
- `commonpaper/SKILL.md` — Codex workflow, safety rules, and usage guidance
- `commonpaper/scripts/commonpaper_api.py` — token storage, validation, and API request helper
- `commonpaper/references/api-cheatsheet.md` — endpoint, filter, and query quick reference

## Install

```bash
mkdir -p ~/.codex/skills
rsync -a ./commonpaper/ ~/.codex/skills/commonpaper/
```

Then invoke it in Codex with `$commonpaper`.

## Set Up Credentials

From the installed skill directory:

```bash
python3 scripts/commonpaper_api.py save-token
python3 scripts/commonpaper_api.py validate-token
```

The token is stored at `~/.codex/skills/commonpaper/cp-api-token` with user-only permissions.

## Example Commands

Count signed agreements:

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[status_eq]=signed' \
  --query 'page[size]=1'
```

Find contracts with a company:

```bash
python3 scripts/commonpaper_api.py request GET /agreements \
  --query 'filter[recipient_organization_cont]=Acme' \
  --query 'page[size]=25'
```

## Safety Notes

- Never paste the API token into chat output
- Prefer `save-token` over inline bearer tokens
- Confirm all write actions before execution
- Use JSON body files for `POST` and `PATCH` requests when possible

## License

MIT
