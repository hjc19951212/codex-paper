#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="${SKILL_DIR}/assets/webui"

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required (>= 18)." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required." >&2
  exit 1
fi

echo "Installing skill dependencies..."
cd "${SKILL_DIR}"
npm install

echo "Installing web UI dependencies..."
cd "${WEB_DIR}"
npm install

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required for image extraction." >&2
  exit 1
fi

if python3 - <<'PY'
try:
    import fitz
    print("PyMuPDF already available")
except Exception:
    raise SystemExit(1)
PY
then
  :
else
  python3 -m pip install --user pymupdf
fi

echo "Dependencies are ready."
