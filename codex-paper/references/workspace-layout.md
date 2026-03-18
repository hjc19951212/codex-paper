# Codex Paper Workspace Layout

The canonical library root is:

```text
~/codex-papers/
```

The paper workspace layout is:

```text
~/codex-papers/
├── index.json
└── papers/
    └── {paper-slug}/
        ├── paper.pdf
        ├── meta.json
        ├── README.md
        ├── summary.md
        ├── insights.md
        ├── qa.md
        ├── method.md
        ├── mental-model.md
        ├── reflection.md
        ├── index.html
        ├── images/
        └── code/
```

## Minimum Expectations

- `paper.pdf`: source paper copy
- `meta.json`: parsed metadata plus local bookkeeping
- `README.md`: navigation entry point
- `summary.md`: structured summary
- `insights.md`: conceptual explanation and trade-offs
- `qa.md`: 15 study questions

## Index Format

Store a top-level object:

```json
{
  "papers": []
}
```

Each paper entry should contain at least:

- `id`
- `title`
- `slug`
- `authors`
- `abstract`
- `date`
- `tags`
- `githubLinks`
- `codeLinks`

## Language Rule

Generate user-facing materials in the user’s language whenever practical.
