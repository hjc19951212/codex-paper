#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB_DIR="${SKILL_DIR}/assets/webui"
PID_FILE="/tmp/codex-paper-webui.pid"
PORT="${CODEX_PAPER_PORT:-5815}"
export CODEX_PAPER_LIBRARY="${CODEX_PAPER_LIBRARY:-$HOME/codex-papers}"

bash "${SKILL_DIR}/scripts/ensure_deps.sh"

cd "${WEB_DIR}"

BUILD_VERSION=""
if [ -f ".output/.build-version" ]; then
  BUILD_VERSION="$(cat .output/.build-version)"
fi

SOURCE_VERSION="$(shasum package.json nuxt.config.ts server/api/papers.get.ts 2>/dev/null | shasum | awk '{print $1}')"

if [ ! -f ".output/server/index.mjs" ] || [ "${BUILD_VERSION}" != "${SOURCE_VERSION}" ]; then
  npm run build
  printf '%s' "${SOURCE_VERSION}" > .output/.build-version
fi

if lsof -i :"${PORT}" >/dev/null 2>&1; then
  if [ -f "${PID_FILE}" ] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
    echo "Codex Paper web UI is already running at http://localhost:${PORT}"
    exit 0
  fi
  echo "Port ${PORT} is already in use." >&2
  exit 1
fi

PORT="${PORT}" node .output/server/index.mjs >/tmp/codex-paper-webui.log 2>&1 &
SERVER_PID=$!
echo "${SERVER_PID}" > "${PID_FILE}"

for _ in $(seq 1 20); do
  if curl --noproxy '*' -fsS "http://127.0.0.1:${PORT}/api/papers" >/dev/null 2>&1; then
    echo "Codex Paper web UI is running at http://localhost:${PORT}"
    echo "PID: ${SERVER_PID}"
    exit 0
  fi
  sleep 1
done

kill "${SERVER_PID}" 2>/dev/null || true
rm -f "${PID_FILE}"
echo "Failed to start Codex Paper web UI." >&2
exit 1
