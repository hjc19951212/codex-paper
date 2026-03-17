# Common Paper Codex Skill

Codex version of the Common Paper contract skill, adapted from the open-source Claude Code skill at `CommonPaper/claude-skill`.

## What it does

- Query Common Paper agreements in natural language through Codex
- Count, search, and summarize NDAs, CSAs, renewals, signers, and deal values
- Perform Common Paper write actions after confirmation
- Store and validate the API token locally for Codex use

## Repo Layout

- `commonpaper/`: installable Codex skill
- `commonpaper/SKILL.md`: Codex-facing workflow and safety rules
- `commonpaper/scripts/commonpaper_api.py`: token + API helper
- `commonpaper/references/api-cheatsheet.md`: endpoint and filter quick reference

## Install Locally

```bash
mkdir -p ~/.codex/skills
rsync -a ./commonpaper/ ~/.codex/skills/commonpaper/
```

Then use the skill in Codex with `$commonpaper`.

## Token Setup

Run this in the installed skill directory:

```bash
python3 scripts/commonpaper_api.py save-token
python3 scripts/commonpaper_api.py validate-token
```

The token is stored at `~/.codex/skills/commonpaper/cp-api-token` with user-only permissions.

## Source

This repository adapts the ideas and API coverage of [CommonPaper/claude-skill](https://github.com/CommonPaper/claude-skill) for the Codex skill format.
