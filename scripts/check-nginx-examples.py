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
    ".github/CODEOWNERS",
    ".github/workflows/check.yml",
    "CHANGES.md",
    "Makefile",
    "README",
    "README.md",
    "SECURITY.md",
    "VISION.md",
    "docs/plans/2026-06-08-nginx-examples-baseline.md",
    "docs/plans/2026-06-09-hide-upstream-server-header.md",
    "docs/plans/2026-06-09-request-body-size-limit.md",
    "docs/plans/2026-06-09-sites-enabled-conf-glob.md",
    "docs/plans/2026-06-09-static-try-files.md",
    "docs/plans/2026-06-09-content-type-nosniff-header.md",
    "docs/plans/2026-06-09-frame-options-header.md",
    "docs/plans/2026-06-09-referrer-policy-header.md",
    "docs/plans/2026-06-09-make-gate-aliases.md",
    "docs/plans/2026-06-10-forwarded-host-header.md",
    "docs/plans/2026-06-10-setup-and-loopback-boundary.md",
    "docs/plans/2026-06-10-upstream-connect-timeout.md",
    "docs/plans/2026-06-10-hosted-static-validation.md",
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
        if "client_max_body_size 1m;" not in text:
            failures.append(f"{config} must define the sample client_max_body_size limit")
        if "add_header X-Content-Type-Options nosniff always;" not in text:
            failures.append(f"{config} must set the X-Content-Type-Options nosniff header")
        if "add_header X-Frame-Options SAMEORIGIN always;" not in text:
            failures.append(f"{config} must set the X-Frame-Options SAMEORIGIN header")
        if "add_header Referrer-Policy strict-origin-when-cross-origin always;" not in text:
            failures.append(f"{config} must set the Referrer-Policy header")
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
        "include /usr/local/nginx/sites-enabled/*.conf;",
    ]:
        if phrase not in php:
            failures.append(f"sample_php_nginx.conf must include {phrase}")
    if "include /usr/local/nginx/sites-enabled/*;" in php:
        failures.append("sample_php_nginx.conf must not include every file from sites-enabled")

    tornado = read("sample_tornado_nginx.conf")
    for phrase in [
        "server_name example.local;",
        "proxy_set_header Host $host;",
        "proxy_set_header X-Forwarded-Host $host;",
        "proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;",
        "proxy_set_header X-Forwarded-Proto $scheme;",
        "proxy_hide_header Server;",
        "proxy_next_upstream error;",
        "proxy_connect_timeout 5s;",
        "# Linux-specific; remove this directive on platforms that do not support epoll.",
        "# Replace with the static root for the deployment host.",
        "root /srv/example-app;",
        "try_files $uri =404;",
    ]:
        if phrase not in tornado:
            failures.append(f"sample_tornado_nginx.conf must include {phrase}")
    if "/home/ubuntu" in tornado:
        failures.append("sample_tornado_nginx.conf must use placeholder paths, not host-specific home paths")
    if "proxy_set_header Host $http_host;" in tornado:
        failures.append("sample_tornado_nginx.conf must not trust raw client Host headers")
    if "proxy_set_header X-Forwarded-Host $http_host;" in tornado:
        failures.append("sample_tornado_nginx.conf must not forward raw client Host headers")
    if "proxy_pass_header Server;" in tornado:
        failures.append("sample_tornado_nginx.conf must not pass upstream Server headers")
    upstreams = re.findall(r"server\s+([^:;\s]+):\d+;", tornado)
    if not upstreams or any(host != "127.0.0.1" for host in upstreams):
        failures.append("sample_tornado_nginx.conf upstreams must stay loopback placeholders")

    makefile = read("Makefile")
    for phrase in [
        ".PHONY: build check lint static-check test verify",
        "check: verify",
        "verify: static-check",
        "lint test build: static-check",
        "PYTHONDONTWRITEBYTECODE=1 $(PYTHON) scripts/check-nginx-examples.py",
    ]:
        if phrase not in makefile:
            failures.append(f"Makefile must include standard gate alias: {phrase}")

    docs = read("README.md") + "\n" + read("VISION.md") + "\n" + read("SECURITY.md")
    for phrase in [
        "make lint",
        "make test",
        "make build",
        "make check",
        "nginx -t",
        "sample-only",
        "server_tokens off",
        "client_max_body_size",
        "X-Forwarded-For",
        "X-Forwarded-Host",
        "proxy_hide_header Server",
        "sites-enabled/*.conf",
        "try_files $uri =404",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "loopback-only upstream placeholders",
        "Do not install the checked-in configs directly",
        "public HTTP upstreams",
    ]:
        if phrase not in docs:
            failures.append(f"docs must mention {phrase}")

    plan = read("docs/plans/2026-06-08-nginx-examples-baseline.md")
    if "status: completed" not in plan or "make check" not in plan:
        failures.append("completed plan must record status and verification")
    header_plan = read("docs/plans/2026-06-09-hide-upstream-server-header.md")
    if "status: completed" not in header_plan or "proxy_hide_header Server" not in header_plan:
        failures.append("upstream header plan must record status and verification")
    include_plan_path = ROOT / "docs/plans/2026-06-09-sites-enabled-conf-glob.md"
    include_plan = include_plan_path.read_text(encoding="utf-8") if include_plan_path.exists() else ""
    if "status: completed" not in include_plan or "sites-enabled/*.conf" not in include_plan:
        failures.append("sites-enabled include plan must record status and verification")
    body_size_plan_path = ROOT / "docs/plans/2026-06-09-request-body-size-limit.md"
    body_size_plan = body_size_plan_path.read_text(encoding="utf-8") if body_size_plan_path.exists() else ""
    if "status: completed" not in body_size_plan or "client_max_body_size" not in body_size_plan:
        failures.append("request body size plan must record status and verification")
    static_plan_path = ROOT / "docs/plans/2026-06-09-static-try-files.md"
    static_plan = static_plan_path.read_text(encoding="utf-8") if static_plan_path.exists() else ""
    if "status: completed" not in static_plan or "try_files $uri =404" not in static_plan:
        failures.append("static try_files plan must record status and verification")
    nosniff_plan_path = ROOT / "docs/plans/2026-06-09-content-type-nosniff-header.md"
    nosniff_plan = nosniff_plan_path.read_text(encoding="utf-8") if nosniff_plan_path.exists() else ""
    if "status: completed" not in nosniff_plan or "X-Content-Type-Options" not in nosniff_plan:
        failures.append("content type nosniff plan must record status and verification")
    frame_options_plan_path = ROOT / "docs/plans/2026-06-09-frame-options-header.md"
    frame_options_plan = frame_options_plan_path.read_text(encoding="utf-8") if frame_options_plan_path.exists() else ""
    if "status: completed" not in frame_options_plan or "X-Frame-Options" not in frame_options_plan:
        failures.append("frame options header plan must record status and verification")
    referrer_policy_plan_path = ROOT / "docs/plans/2026-06-09-referrer-policy-header.md"
    referrer_policy_plan = referrer_policy_plan_path.read_text(encoding="utf-8") if referrer_policy_plan_path.exists() else ""
    if "status: completed" not in referrer_policy_plan or "Referrer-Policy" not in referrer_policy_plan:
        failures.append("referrer policy header plan must record status and verification")
    make_gate_plan_path = ROOT / "docs/plans/2026-06-09-make-gate-aliases.md"
    make_gate_plan = make_gate_plan_path.read_text(encoding="utf-8") if make_gate_plan_path.exists() else ""
    if "status: completed" not in make_gate_plan or "make lint" not in make_gate_plan or "make build" not in make_gate_plan:
        failures.append("make gate alias plan must record status and verification")
    forwarded_host_plan_path = ROOT / "docs/plans/2026-06-10-forwarded-host-header.md"
    forwarded_host_plan = forwarded_host_plan_path.read_text(encoding="utf-8") if forwarded_host_plan_path.exists() else ""
    if "status: completed" not in forwarded_host_plan or "X-Forwarded-Host" not in forwarded_host_plan:
        failures.append("forwarded host header plan must record status and verification")
    setup_boundary_plan_path = ROOT / "docs/plans/2026-06-10-setup-and-loopback-boundary.md"
    setup_boundary_plan = setup_boundary_plan_path.read_text(encoding="utf-8") if setup_boundary_plan_path.exists() else ""
    if "status: completed" not in setup_boundary_plan or "loopback-only upstream placeholders" not in setup_boundary_plan:
        failures.append("setup and loopback boundary plan must record status and verification")
    connect_timeout_plan = read("docs/plans/2026-06-10-upstream-connect-timeout.md")
    if "status: completed" not in connect_timeout_plan or "proxy_connect_timeout 5s" not in connect_timeout_plan:
        failures.append("upstream connect timeout plan must record status and verification")

    hosted_plan = read("docs/plans/2026-06-10-hosted-static-validation.md")
    workflow = read(".github/workflows/check.yml")
    codeowners = read(".github/CODEOWNERS")
    if "status: completed" not in hosted_plan or "make check" not in hosted_plan:
        failures.append("hosted static validation plan must record status and verification")
    for expected in [
        "permissions:\n  contents: read",
        "cancel-in-progress: true",
        "runs-on: ubuntu-24.04",
        "timeout-minutes: 10",
        "actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10",
        "persist-credentials: false",
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "run: make check",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")
    workflow_files = sorted(str(path.relative_to(ROOT)) for path in (ROOT / ".github/workflows").rglob("*") if path.is_file())
    if workflow_files != [".github/workflows/check.yml"]:
        failures.append("check.yml must be the repository's only hosted workflow")
    if codeowners.strip() != "* @garethpaul":
        failures.append("CODEOWNERS must assign the repository to @garethpaul")

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
