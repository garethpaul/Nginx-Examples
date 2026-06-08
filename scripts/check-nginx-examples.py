#!/usr/bin/env python3
"""Static checks for the Nginx example configuration baseline."""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ["sample_php_nginx.conf", "sample_tornado_nginx.conf"]
REQUIRED = [
    ".gitignore",
    "CHANGES.md",
    "Makefile",
    "README",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "docs/plans/2026-06-08-nginx-examples-baseline.md",
    "docs/readme-overview.svg",
    "scripts/check-nginx-examples.py",
] + CONFIGS


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        lines.append(line.split("#", 1)[0])
    return "\n".join(lines)


def check_balanced_braces(path: str, text: str, failures) -> None:
    depth = 0
    for index, char in enumerate(strip_comments(text), start=1):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
        if depth < 0:
            failures.append(f"{path} has an unmatched closing brace near character {index}")
            return
    if depth != 0:
        failures.append(f"{path} has unbalanced braces")


def main() -> int:
    failures = []
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            failures.append(f"required file missing: {path}")

    for config in CONFIGS:
        text = read(config)
        check_balanced_braces(config, text, failures)
        if "server_tokens off;" not in text:
            failures.append(f"{config} must disable server_tokens")
        if re.search(r"error_log\s+\S+\s+debug\s*;", text):
            failures.append(f"{config} must not default to debug error logging")
        if re.search(r"ssl_certificate(_key)?\s+[^;]*(/etc|/home|BEGIN|PRIVATE)", text):
            failures.append(f"{config} must not include real certificate or key paths")

    php = read("sample_php_nginx.conf")
    for phrase in [
        "pid        /var/run/nginx.pid;",
        "error_log   /var/log/nginx/error.log   warn;",
        "tcp_nodelay     on;",
        "application/javascript",
        "# Adjust this include path for the deployment host.",
    ]:
        if phrase not in php:
            failures.append(f"sample_php_nginx.conf must include {phrase}")

    tornado = read("sample_tornado_nginx.conf")
    for phrase in [
        "server_name example.local;",
        "proxy_set_header Host $host;",
        "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
        "proxy_set_header X-Forwarded-Proto $scheme;",
        "proxy_next_upstream error;",
        "# Linux-specific; remove this directive on platforms that do not support epoll.",
    ]:
        if phrase not in tornado:
            failures.append(f"sample_tornado_nginx.conf must include {phrase}")
    if "proxy_set_header Host $http_host;" in tornado:
        failures.append("sample_tornado_nginx.conf must not trust raw client Host headers")
    upstreams = re.findall(r"server\s+([^:;\s]+):\d+;", tornado)
    if not upstreams or any(host != "127.0.0.1" for host in upstreams):
        failures.append("sample_tornado_nginx.conf upstreams must stay loopback placeholders")

    docs = read("README.md") + "\n" + read("VISION.md") + "\n" + read("SECURITY.md")
    for phrase in ["make check", "nginx -t", "sample-only", "server_tokens off", "X-Forwarded-For"]:
        if phrase not in docs:
            failures.append(f"docs must mention {phrase}")

    plan = read("docs/plans/2026-06-08-nginx-examples-baseline.md")
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("completed plan must record status and verification")

    gitignore = read(".gitignore")
    for expected in [".env", "*.log", "*.pid", "nginx-test-prefix/"]:
        if expected not in gitignore:
            failures.append(f".gitignore must include {expected}")

    try:
        ET.parse(ROOT / "docs/readme-overview.svg")
    except Exception as error:
        failures.append(f"docs/readme-overview.svg must parse as XML: {error}")

    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1

    print("Nginx example baseline checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
