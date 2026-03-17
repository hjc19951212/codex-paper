#!/usr/bin/env python3
from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import stat
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "https://api.commonpaper.com/v1"
TOKEN_PATTERN = re.compile(r"^zpka_[A-Za-z0-9_]+$")


def default_skill_home() -> Path:
    explicit = os.environ.get("COMMONPAPER_SKILL_HOME")
    if explicit:
        return Path(explicit).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()
    return codex_home / "skills" / "commonpaper"


def token_path() -> Path:
    return default_skill_home() / "cp-api-token"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_token(path: Path | None = None) -> str:
    current = path or token_path()
    if not current.exists():
        raise SystemExit(f"Token file not found: {current}")
    token = current.read_text(encoding="utf-8").strip()
    if not token:
        raise SystemExit(f"Token file is empty: {current}")
    return token


def write_token(token: str, path: Path | None = None) -> Path:
    current = path or token_path()
    ensure_parent(current)
    current.write_text(token, encoding="utf-8")
    current.chmod(stat.S_IRUSR | stat.S_IWUSR)
    return current


def parse_query_items(items: list[str]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for item in items:
        if "=" not in item:
            raise SystemExit(f"Invalid --query value (expected key=value): {item}")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise SystemExit(f"Invalid empty query key in: {item}")
        pairs.append((key, value))
    return pairs


def build_url(endpoint: str, query_items: list[tuple[str, str]]) -> str:
    if not endpoint.startswith("/"):
        raise SystemExit("Endpoint must start with '/'.")
    if "://" in endpoint:
        raise SystemExit("Endpoint must be relative to the Common Paper API base URL.")
    url = f"{BASE_URL}{endpoint}"
    if query_items:
        url = f"{url}?{urlencode(query_items, doseq=True)}"
    return url


def request_json(
    method: str,
    endpoint: str,
    query_items: list[tuple[str, str]] | None = None,
    body: Any | None = None,
    timeout: int = 30,
) -> tuple[int, Any]:
    token = read_token()
    url = build_url(endpoint, query_items or [])
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "commonpaper-codex-skill/1.0",
    }
    payload = None
    if body is not None:
        payload = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(url, data=payload, headers=headers, method=method.upper())
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            if not raw.strip():
                return response.status, None
            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, raw
    except HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        message = {
            "status": error.code,
            "url": url,
            "body": raw,
        }
        print(json.dumps(message, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)
    except URLError as error:
        raise SystemExit(f"Network error: {error}") from error


def cmd_show_paths(_: argparse.Namespace) -> int:
    print(json.dumps({"skill_home": str(default_skill_home()), "token_path": str(token_path())}, ensure_ascii=False, indent=2))
    return 0


def cmd_save_token(args: argparse.Namespace) -> int:
    token = getpass.getpass("Common Paper API token: ").strip()
    if not TOKEN_PATTERN.match(token):
        raise SystemExit("Token format looks invalid. Expected a token like zpka_...")
    confirm = getpass.getpass("Re-enter token: ").strip()
    if token != confirm:
        raise SystemExit("Tokens did not match.")
    if not args.no_validate:
        write_token(token)
        try:
            request_json("GET", "/agreements", [("page[size]", "1")], timeout=args.timeout)
        except SystemExit:
            token_path().unlink(missing_ok=True)
            raise
    target = write_token(token)
    print(f"Saved token to {target}")
    return 0


def cmd_validate_token(args: argparse.Namespace) -> int:
    if args.token_file:
        token = read_token(Path(args.token_file).expanduser())
        if not TOKEN_PATTERN.match(token):
            raise SystemExit("Stored token format looks invalid.")
    else:
        token = read_token()
        if not TOKEN_PATTERN.match(token):
            raise SystemExit("Stored token format looks invalid.")
    status_code, _ = request_json("GET", "/agreements", [("page[size]", "1")], timeout=args.timeout)
    print(f"Token is valid (HTTP {status_code}).")
    return 0


def load_body(body_file: str | None) -> Any | None:
    if not body_file:
        return None
    path = Path(body_file).expanduser()
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_request(args: argparse.Namespace) -> int:
    query_items = parse_query_items(args.query or [])
    body = load_body(args.body_file)
    status_code, payload = request_json(args.method, args.endpoint, query_items, body, timeout=args.timeout)
    if args.include_status and isinstance(payload, dict):
        payload = {"status": status_code, "data": payload}
    elif args.include_status and payload is None:
        payload = {"status": status_code}
    if payload is None:
        print(json.dumps({"status": status_code}, ensure_ascii=False, indent=2))
        return 0
    if isinstance(payload, (dict, list)):
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    print(payload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Common Paper API helper for Codex skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_paths = subparsers.add_parser("show-paths", help="Show the skill and token paths.")
    show_paths.set_defaults(func=cmd_show_paths)

    save_token = subparsers.add_parser("save-token", help="Prompt for and store the Common Paper API token.")
    save_token.add_argument("--no-validate", action="store_true", help="Save without testing the token.")
    save_token.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    save_token.set_defaults(func=cmd_save_token)

    validate = subparsers.add_parser("validate-token", help="Validate the stored token with a lightweight API call.")
    validate.add_argument("--token-file", help="Optional explicit token file path.")
    validate.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    validate.set_defaults(func=cmd_validate_token)

    request_parser = subparsers.add_parser("request", help="Send a Common Paper API request using the stored token.")
    request_parser.add_argument("method", help="HTTP method, for example GET, POST, or PATCH.")
    request_parser.add_argument("endpoint", help="API endpoint path, for example /agreements or /agreements/123/history.")
    request_parser.add_argument("--query", action="append", help="Query item in key=value form. Repeat as needed.")
    request_parser.add_argument("--body-file", help="Path to a JSON file used as the request body.")
    request_parser.add_argument("--include-status", action="store_true", help="Wrap JSON output with the HTTP status code.")
    request_parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds.")
    request_parser.set_defaults(func=cmd_request)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
