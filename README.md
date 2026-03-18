# Codex Paper

[中文说明](./README.zh-CN.md)

`codex-paper` is a Codex-native research paper study skill adapted from [`alaliqing/claude-paper`](https://github.com/alaliqing/claude-paper).

It helps Codex:

- accept a local PDF, direct PDF URL, or arXiv URL
- prepare a reusable paper workspace under `~/codex-papers/`
- parse metadata and extract figures
- generate study materials such as `summary.md`, `insights.md`, `qa.md`, demos, and an interactive `index.html`
- launch a bundled local web UI for browsing the paper library

## Included Skill

- `codex-paper/` — installable Codex skill folder
- `codex-paper/SKILL.md` — workflow for paper study and deep dives
- `codex-paper/scripts/prepare_paper.py` — workspace bootstrapper
- `codex-paper/scripts/start_webui.sh` — local Nuxt web UI launcher
- `codex-paper/assets/webui/` — bundled paper library viewer

## Install

```bash
mkdir -p ~/.codex/skills
rsync -a ./codex-paper/ ~/.codex/skills/codex-paper/
```

Then use it with `$codex-paper`.

## First Run

```bash
cd ~/.codex/skills/codex-paper
bash scripts/ensure_deps.sh
```

## Prepare a Paper

```bash
python3 scripts/prepare_paper.py ~/Downloads/paper.pdf
python3 scripts/prepare_paper.py https://arxiv.org/abs/1706.03762
```

## Start the Web UI

```bash
bash scripts/start_webui.sh
```

Default address:

- `http://localhost:5815`

Default library root:

- `~/codex-papers`

## Upstream Inspiration

This project reworks the original Claude plugin into a Codex skill by removing plugin-only wrappers and keeping the reusable workflow, PDF helpers, and local viewer.
