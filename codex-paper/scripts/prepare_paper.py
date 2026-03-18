#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return normalized or "paper"


def default_library_root() -> Path:
    return Path.home() / "codex-papers"


def ensure_library(root: Path) -> tuple[Path, Path]:
    papers_dir = root / "papers"
    papers_dir.mkdir(parents=True, exist_ok=True)
    index_path = root / "index.json"
    if not index_path.exists():
        index_path.write_text(json.dumps({"papers": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    return papers_dir, index_path


def run_capture(command: list[str], cwd: Path) -> str:
    result = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True)
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        if command[:2] == ["node", "scripts/parse-pdf.js"] and "ERR_MODULE_NOT_FOUND" in (result.stderr or ""):
            print("Missing Node dependencies. Run `bash scripts/ensure_deps.sh` first.", file=sys.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def load_index(index_path: Path) -> dict:
    raw = json.loads(index_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return {"papers": raw}
    if "papers" not in raw or not isinstance(raw["papers"], list):
        raw["papers"] = []
    return raw


def upsert_index_entry(index_path: Path, entry: dict) -> None:
    data = load_index(index_path)
    papers = data["papers"]
    for idx, item in enumerate(papers):
        if item.get("slug") == entry["slug"]:
            papers[idx] = {**item, **entry}
            break
    else:
        papers.append(entry)
    index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a Codex Paper workspace from a PDF path or URL.")
    parser.add_argument("input", help="Local PDF path, direct PDF URL, or arXiv URL.")
    parser.add_argument("--library-root", default=str(default_library_root()), help="Paper library root. Defaults to ~/codex-papers.")
    args = parser.parse_args()

    skill_dir = Path(__file__).resolve().parent.parent
    root = Path(args.library_root).expanduser()
    papers_dir, index_path = ensure_library(root)

    local_pdf = run_capture(["node", "scripts/download-pdf.cjs", args.input], cwd=skill_dir)
    metadata_raw = run_capture(["node", "scripts/parse-pdf.js", local_pdf], cwd=skill_dir)
    metadata = json.loads(metadata_raw)

    title = str(metadata.get("title") or Path(local_pdf).stem).strip()
    slug = slugify(title)
    paper_dir = papers_dir / slug
    paper_dir.mkdir(parents=True, exist_ok=True)

    target_pdf = paper_dir / "paper.pdf"
    shutil.copy2(local_pdf, target_pdf)

    merged_meta = {
        **metadata,
        "title": title,
        "slug": slug,
        "source": args.input,
        "paperPath": str(target_pdf),
        "tags": metadata.get("tags") or [],
        "preparedAt": datetime.now().isoformat(timespec="seconds"),
    }
    (paper_dir / "meta.json").write_text(json.dumps(merged_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    index_entry = {
        "id": slug,
        "title": title,
        "slug": slug,
        "authors": metadata.get("authors") or [],
        "abstract": metadata.get("abstract") or "",
        "date": datetime.now().date().isoformat(),
        "tags": merged_meta["tags"],
        "githubLinks": metadata.get("githubLinks") or [],
        "codeLinks": metadata.get("codeLinks") or [],
        "source": args.input,
    }
    upsert_index_entry(index_path, index_entry)

    result = {
        "libraryRoot": str(root),
        "paperDir": str(paper_dir),
        "paperPdf": str(target_pdf),
        "metaJson": str(paper_dir / "meta.json"),
        "indexJson": str(index_path),
        "slug": slug,
        "title": title,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
