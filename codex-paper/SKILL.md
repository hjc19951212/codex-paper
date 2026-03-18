---
name: codex-paper
description: Study, read, analyze, and build reusable learning materials for research papers in PDF form. Use when the user wants to understand a paper deeply from a local PDF path, a direct PDF URL, or an arXiv URL, and wants generated notes, Q&A, code demos, extracted figures, or a local web UI to browse a paper library.
---

# Codex Paper

## Overview

Use this skill to turn a research paper into a reusable study workspace under `~/codex-papers/`. It combines deterministic helpers for downloading and parsing PDFs with a reasoning workflow that writes summaries, insights, Q&A, demos, and an interactive HTML explainer.

## Quick Start

Install dependencies once:

```bash
bash scripts/ensure_deps.sh
```

Prepare a paper workspace from a local PDF, PDF URL, or arXiv URL:

```bash
python3 scripts/prepare_paper.py "https://arxiv.org/abs/1706.03762"
```

Start the local web library:

```bash
bash scripts/start_webui.sh
```

The library defaults to `~/codex-papers/` and the web UI defaults to `http://localhost:5815`.

## Workflow

### 1. Normalize Input

Accept:

- a local PDF path
- a direct PDF URL
- an arXiv abstract URL

Use `scripts/prepare_paper.py` to:

- download if needed
- parse the PDF
- create a paper slug
- create `~/codex-papers/papers/{paper-slug}/`
- copy `paper.pdf`
- write initial `meta.json`
- ensure `~/codex-papers/index.json` exists

### 2. Assess the Paper

Before writing any study materials, infer:

- difficulty: beginner, intermediate, advanced, or highly theoretical
- paper nature: theoretical, architecture, empirical, system, or survey
- methodological complexity: simple pipeline, multi-stage, novel architecture, or math-heavy

Use this assessment to decide depth and which optional files to include.

### 3. Generate Tags

Infer exactly 2 semantic tags:

- one for problem/domain
- one for method/core idea

Keep each tag short and concrete. Avoid generic tags like `paper`, `research`, `ai`, or `ml`.

Persist them in:

- `meta.json`
- `~/codex-papers/index.json`

### 4. Generate Core Materials

Always create:

- `README.md`
- `summary.md`
- `insights.md`
- `qa.md`

Generate all materials in the user’s language.

`insights.md` is the most important file. It should explain the core idea plainly, why it works, the conceptual shift, trade-offs, limitations, and practical implications.

`qa.md` should contain 15 questions:

- 5 basic
- 5 intermediate
- 5 advanced

### 5. Generate Optional Materials

When they add value, also create:

- `method.md`
- `mental-model.md`
- `reflection.md`

Use `method.md` for architecture breakdowns, pseudocode, implementation pitfalls, and reproduction risks.

### 6. Generate Demonstrations

Always create at least one runnable demo in:

```text
~/codex-papers/papers/{paper-slug}/code/
```

Prefer clarity over completeness. Good options:

- a simplified reference implementation
- a small visualization
- an interactive notebook

### 7. Generate Interactive Explorer

Create a single-file `index.html` inside the paper folder.

Requirements:

- one self-contained HTML file
- all CSS and JS inline
- no external fetches
- use only real values from the paper
- every control must visibly change something

### 8. Extract Images

Use:

```bash
python3 scripts/extract-images.py /absolute/path/to/paper.pdf /absolute/path/to/images
```

If needed, rename key outputs descriptively such as `architecture.png` or `results_table.png`.

### 9. Update the Global Index

Never overwrite the whole index without reading it first.

The index lives at:

```text
~/codex-papers/index.json
```

Append or update one entry with:

- `id`
- `title`
- `slug`
- `authors`
- `abstract`
- `date`
- `tags`
- `githubLinks`
- `codeLinks`

### 10. Deepen the Study Loop

After the first pass, invite follow-up exploration:

- deeper math breakdown
- implementation analysis
- comparison with another paper
- critique or extension ideas

Store follow-up files in the same paper folder, for example:

- `deep-dive-attention.md`
- `comparison-with-transformers.md`
- `extension-ideas.md`

## Web UI

Use `bash scripts/start_webui.sh` to build and run the bundled Nuxt web UI from `assets/webui/`.

The web UI reads the paper library from `CODEX_PAPER_LIBRARY` when set, otherwise `~/codex-papers/`.

## References

- Read `references/workspace-layout.md` for the canonical folder structure and file expectations.
- Use `scripts/prepare_paper.py --help` for deterministic setup behavior.
