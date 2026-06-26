#!/usr/bin/env python3
"""Static checks for the Nginx example configuration baseline."""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MAKEFILE = """ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); /usr/bin/dirname -- "$$path")
override SHELL_ROOT := $(subst ','"'"',$(ROOT))

.PHONY: build check checker-test lint proxy-test root-test static-check test verify

PYTHON ?= python3

check: verify

verify: static-check test

lint build: static-check

test: checker-test proxy-test root-test

checker-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/test-check-nginx-examples.py'

proxy-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/test-nginx-proxy.py'

root-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/test-makefile-root.py'

static-check:
\tPYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/check-nginx-examples.py'
"""
CONFIGS = ["sample_php_nginx.conf", "sample_tornado_nginx.conf"]
TLS_TEMPLATE = "sample_tls_nginx.conf.example"
REQUIRED = [
    ".gitignore",
    ".github/CODEOWNERS",
    ".github/workflows/check.yml",
    "AGENTS.md",
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
    "docs/plans/2026-06-12-upstream-io-timeouts.md",
    "docs/plans/2026-06-12-checkout-credential-boundary.md",
    "docs/plans/2026-06-13-sample-configuration-guidance.md",
    "docs/plans/2026-06-13-location-independent-make.md",
    "docs/plans/2026-06-15-proxy-request-header-suppression.md",
    "docs/plans/2026-06-15-forwarded-for-trust-boundary.md",
    "docs/plans/2026-06-15-forwarded-host-trust-boundary.md",
    "docs/plans/2026-06-15-forwarded-header-suppression.md",
    "docs/plans/2026-06-16-websocket-upgrade-proxying.md",
    "docs/plans/2026-06-19-proxy-boundary-review.md",
    "docs/plans/2026-06-21-safe-make-root.md",
    "docs/plans/2026-06-21-spaced-makefile-path.md",
    "docs/plans/2026-06-25-safe-tls-placeholder.md",
    "docs/readme-overview.svg",
    "scripts/check-nginx-examples.py",
    "scripts/test-check-nginx-examples.py",
    "scripts/test-makefile-root.py",
    "scripts/test-nginx-proxy.py",
] + CONFIGS + [TLS_TEMPLATE]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def markdown_section(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*$\n(.*?)(?=^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


def markdown_subsection(text: str, heading: str) -> str:
    match = re.search(
        rf"(?ms)^### {re.escape(heading)}\s*$\n(.*?)(?=^### |^## |\Z)",
        text,
    )
    return match.group(1).strip() if match else ""


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
        active_text = strip_comments(text)
        check_balanced_braces(config, text, failures)
        if "server_tokens off;" not in active_text:
            failures.append(f"{config} must disable server_tokens")
        if "client_max_body_size 1m;" not in active_text:
            failures.append(f"{config} must define the sample client_max_body_size limit")
        if "add_header X-Content-Type-Options nosniff always;" not in active_text:
            failures.append(f"{config} must set the X-Content-Type-Options nosniff header")
        if "add_header X-Frame-Options SAMEORIGIN always;" not in active_text:
            failures.append(f"{config} must set the X-Frame-Options SAMEORIGIN header")
        if "add_header Referrer-Policy strict-origin-when-cross-origin always;" not in active_text:
            failures.append(f"{config} must set the Referrer-Policy header")
        if re.search(r"error_log\s+\S+\s+debug\s*;", active_text):
            failures.append(f"{config} must not default to debug error logging")
        if re.search(r"ssl_certificate(_key)?\s+[^;]*(/etc|/home|BEGIN|PRIVATE)", active_text):
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
    active_tornado = strip_comments(tornado)
    for phrase in [
        "server_name example.local;",
        "proxy_set_header Host $server_name;",
        "proxy_set_header X-Forwarded-Host $server_name;",
        "proxy_set_header X-Forwarded-For $remote_addr;",
        "proxy_set_header X-Forwarded-Proto $scheme;",
        "proxy_set_header X-Forwarded-Port $server_port;",
        "proxy_hide_header Server;",
        "proxy_next_upstream error;",
        "proxy_connect_timeout 5s;",
        "proxy_read_timeout 30s;",
        "proxy_send_timeout 30s;",
        "# Linux-specific; remove this directive on platforms that do not support epoll.",
        "# Replace with the static root for the deployment host.",
        "root /srv/example-app;",
        "try_files $uri =404;",
    ]:
        source = tornado if phrase.startswith("#") else active_tornado
        if phrase not in source:
            failures.append(f"sample_tornado_nginx.conf must include {phrase}")
    if "/home/ubuntu" in tornado:
        failures.append("sample_tornado_nginx.conf must use placeholder paths, not host-specific home paths")
    proxy_location = active_tornado.split("location / {", 1)[-1].split("\n        }", 1)[0]
    host_override = "proxy_set_header Host $server_name;"
    forwarded_host_override = "proxy_set_header X-Forwarded-Host $server_name;"
    host_override_index = proxy_location.find(host_override)
    forwarded_host_index = proxy_location.find(forwarded_host_override)
    forwarded_for_override = "proxy_set_header X-Forwarded-For $remote_addr;"
    forwarded_for_index = proxy_location.find(forwarded_for_override)
    forwarded_port_override = "proxy_set_header X-Forwarded-Port $server_port;"
    forwarded_port_index = proxy_location.find(forwarded_port_override)
    forwarded_suppression = 'proxy_set_header Forwarded "";'
    forwarded_suppression_index = proxy_location.find(forwarded_suppression)
    proxy_suppression_index = proxy_location.find('proxy_set_header Proxy "";')
    proxy_http_version = "proxy_http_version 1.1;"
    upgrade_header = "proxy_set_header Upgrade $upstream_upgrade;"
    connection_header = "proxy_set_header Connection $connection_upgrade;"
    proxy_http_version_index = proxy_location.find(proxy_http_version)
    upgrade_header_index = proxy_location.find(upgrade_header)
    connection_header_index = proxy_location.find(connection_header)
    proxy_pass_index = proxy_location.find("proxy_pass http://frontends;")
    if not (
        active_tornado.count(host_override) == 1
        and active_tornado.count(forwarded_host_override) == 1
        and 0 <= host_override_index < forwarded_host_index < proxy_pass_index
        and "proxy_set_header Host $host;" not in active_tornado
        and "proxy_set_header X-Forwarded-Host $host;" not in active_tornado
        and "$http_host" not in active_tornado
    ):
        failures.append("Tornado proxy requests must pin upstream host identity before proxy_pass")
    if not (
        active_tornado.count(forwarded_for_override) == 1
        and 0 <= forwarded_for_index < proxy_pass_index
        and "$proxy_add_x_forwarded_for" not in active_tornado
        and "$http_x_forwarded_for" not in active_tornado
    ):
        failures.append("Tornado proxy requests must replace untrusted X-Forwarded-For before proxy_pass")
    if not (
        active_tornado.count(forwarded_port_override) == 1
        and 0 <= forwarded_port_index < proxy_pass_index
        and "$http_x_forwarded_port" not in active_tornado
    ):
        failures.append("Tornado proxy requests must replace untrusted X-Forwarded-Port before proxy_pass")
    if not (
        len(re.findall(r"(?m)^\s*proxy_set_header\s+Forwarded\b", proxy_location)) == 1
        and active_tornado.count(forwarded_suppression) == 1
        and 0 <= forwarded_suppression_index < proxy_pass_index
    ):
        failures.append("Tornado proxy requests must suppress the inbound Forwarded header before proxy_pass")
    if not (
        active_tornado.count('proxy_set_header Proxy "";') == 1
        and 0 <= proxy_suppression_index < proxy_pass_index
    ):
        failures.append("Tornado proxy requests must suppress the inbound Proxy header before proxy_pass")
    connection_token_map = re.findall(
        r"(?ms)^\s*map\s+\$http_connection\s+\$connection_has_upgrade\s*\{\s*"
        r"default\s+0;\s*~\*\(\^\|,\)\\s\*upgrade\\s\*\(,\|\$\)\s+1;\s*\}",
        active_tornado,
    )
    sanitized_upgrade_map = re.findall(
        r'(?ms)^\s*map\s+"\$connection_has_upgrade:\$http_upgrade"\s+\$upstream_upgrade\s*\{\s*'
        r"default\s+'';\s*~\*\^1:websocket\$\s+websocket;\s*\}",
        active_tornado,
    )
    connection_upgrade_map = re.findall(
        r"(?ms)^\s*map\s+\$upstream_upgrade\s+\$connection_upgrade\s*\{\s*"
        r"default\s+close;\s*websocket\s+upgrade;\s*\}",
        active_tornado,
    )
    http_index = active_tornado.find("http {")
    connection_token_map_index = active_tornado.find(
        "map $http_connection $connection_has_upgrade {"
    )
    map_index = active_tornado.find(
        'map "$connection_has_upgrade:$http_upgrade" $upstream_upgrade {'
    )
    connection_map_index = active_tornado.find("map $upstream_upgrade $connection_upgrade {")
    upstream_index = active_tornado.find("upstream frontends {")
    if not (
        len(connection_token_map) == 1
        and len(sanitized_upgrade_map) == 1
        and len(connection_upgrade_map) == 1
        and 0
        <= http_index
        < connection_token_map_index
        < map_index
        < connection_map_index
        < upstream_index
        and active_tornado.count("$connection_has_upgrade") == 2
    ):
        failures.append(
            "Tornado WebSocket upgrade maps must require Connection upgrade intent and exact websocket traffic at http scope"
        )
    if not (
        active_tornado.count(proxy_http_version) == 1
        and active_tornado.count(upgrade_header) == 1
        and active_tornado.count(connection_header) == 1
        and 0 <= proxy_http_version_index < upgrade_header_index < connection_header_index < proxy_pass_index
        and 'proxy_set_header Connection "upgrade";' not in active_tornado
        and "proxy_set_header Upgrade $http_upgrade;" not in active_tornado
    ):
        failures.append("Tornado WebSocket upgrade headers must preserve mixed traffic before proxy_pass")
    if "proxy_pass_header Server;" in active_tornado:
        failures.append("sample_tornado_nginx.conf must not pass upstream Server headers")
    if active_tornado.count("proxy_pass http://frontends;") != 1:
        failures.append("Tornado proxy_pass must preserve the original path and query without a URI suffix")
    upstreams = re.findall(r"server\s+([^:;\s]+):\d+;", active_tornado)
    if not upstreams or any(host != "127.0.0.1" for host in upstreams):
        failures.append("sample_tornado_nginx.conf upstreams must stay loopback placeholders")

    tls_path = ROOT / TLS_TEMPLATE
    tls = read(TLS_TEMPLATE) if tls_path.is_file() else ""
    active_tls = strip_comments(tls)
    check_balanced_braces(TLS_TEMPLATE, tls, failures)
    for phrase in [
        "# TEMPLATE ONLY:",
        "listen 443 ssl;",
        "server_name example.invalid;",
        "ssl_certificate /path/to/fullchain.pem;",
        "ssl_certificate_key /path/to/privkey.pem;",
        "ssl_protocols TLSv1.2 TLSv1.3;",
        "ssl_session_cache shared:TLS:10m;",
        "ssl_session_timeout 1d;",
        "ssl_session_tickets off;",
        "return 301 https://example.invalid$request_uri;",
    ]:
        source = tls if phrase.startswith("#") else active_tls
        if phrase not in source:
            failures.append(f"{TLS_TEMPLATE} must include {phrase}")
    for phrase in [
        "server_tokens off;",
        "client_max_body_size 1m;",
        "add_header X-Content-Type-Options nosniff always;",
        "add_header X-Frame-Options SAMEORIGIN always;",
        "add_header Referrer-Policy strict-origin-when-cross-origin always;",
    ]:
        if phrase not in active_tls:
            failures.append(f"{TLS_TEMPLATE} must preserve the shared sample guard {phrase}")
    if "add_header Strict-Transport-Security" in active_tls:
        failures.append(f"{TLS_TEMPLATE} must not enable HSTS before deployment ownership and HTTPS validation")
    if "Add HSTS only after" not in tls:
        failures.append(f"{TLS_TEMPLATE} must explain the deferred HSTS boundary")
    if re.search(r"server_name\s+(?!example\.invalid)[^;]+;", active_tls):
        failures.append(f"{TLS_TEMPLATE} must use only example.invalid as its placeholder domain")

    makefile = read("Makefile")
    if makefile != EXPECTED_MAKEFILE:
        failures.append(
            "Makefile must exactly preserve rooted dependency-free aliases and the Python override"
        )

    readme = read("README.md")
    docs = readme + "\n" + read("VISION.md") + "\n" + read("SECURITY.md")
    location_independent_make_plan = read(
        "docs/plans/2026-06-13-location-independent-make.md"
    )
    spaced_makefile_plan = read("docs/plans/2026-06-21-spaced-makefile-path.md")
    if "make -f /path/to/Nginx-Examples/Makefile check" not in readme:
        failures.append("README must document location-independent Makefile invocation")
    if "`sample_tls_nginx.conf.example`" not in readme:
        failures.append("README must document the TLS placeholder template")
    security = read("SECURITY.md")
    normalized_security = " ".join(security.split())
    if "The runnable PHP and Tornado examples are HTTP-only." not in normalized_security:
        failures.append("SECURITY must scope the HTTP-only boundary to the runnable examples")
    if "The checked-in TLS file is a non-runnable placeholder template" not in normalized_security:
        failures.append("SECURITY must identify the TLS file as a non-runnable placeholder")
    if "The examples are HTTP-only." in normalized_security:
        failures.append("SECURITY must not describe the TLS template as an HTTP-only example")
    if "Add TLS examples only with safe placeholders" in read("VISION.md"):
        failures.append("VISION must not retain the completed TLS placeholder priority")
    tls_plan = read("docs/plans/2026-06-25-safe-tls-placeholder.md")
    if not all(
        phrase in tls_plan
        for phrase in [
            "Status: completed",
            "example.invalid",
            "TLS 1.2/1.3",
            "Deferred HSTS",
            "nginx -t",
            "make check",
        ]
    ):
        failures.append("TLS placeholder plan must record completed scope and verification")
    if not all(
        evidence in location_independent_make_plan.lower()
        for evidence in [
            "status: completed",
            "root and external-directory",
            "six isolated hostile mutations",
        ]
    ):
        failures.append(
            "location-independent Make plan must record completed root, external, and mutation verification"
        )
    if not all(
        evidence in spaced_makefile_plan
        for evidence in [
            "status: completed",
            "all nine Make aliases",
            "command-substitution",
            "live loopback Nginx tests",
        ]
    ):
        failures.append(
            "spaced Makefile path plan must preserve hostile-path and execution proof"
        )
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
        "X-Forwarded-Port",
        "proxy_hide_header Server",
        "sites-enabled/*.conf",
        "try_files $uri =404",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "upstream I/O timeouts",
        "Proxy request header suppression",
        "WebSocket upgrade proxying",
        "Do not install the checked-in configs directly",
        "loopback-only",
        "HSTS",
    ]:
        if phrase not in docs:
            failures.append(f"docs must mention {phrase}")
    for relative_path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]:
        if "proxy request header suppression" not in read(relative_path).lower():
            failures.append(f"{relative_path} must document Proxy request header suppression")
        if "forwarded host trust boundary" not in read(relative_path).lower():
            failures.append(f"{relative_path} must document the Forwarded Host trust boundary")
        if "websocket upgrade proxying" not in read(relative_path).lower():
            failures.append(f"{relative_path} must document WebSocket upgrade proxying")

    normalized_readme = " ".join(readme.split())
    php_guidance = " ".join(markdown_subsection(readme, "`sample_php_nginx.conf`").split())
    tornado_guidance = " ".join(markdown_subsection(readme, "`sample_tornado_nginx.conf`").split())
    adaptation_guidance = " ".join(markdown_section(readme, "Production Adaptation Checklist").split())
    guidance_contracts = {
        "README sample-only boundary": (
            normalized_readme,
            ["they are not a production capacity, routing, or security policy"],
        ),
        "PHP sample guidance": (
            php_guidance,
            ["service account", "sites-enabled/*.conf", "FastCGI upstreams", "certificate placeholders"],
        ),
        "Tornado sample guidance": (
            tornado_guidance,
            ["loopback ports", "example.local", "/srv/example-app", "upstream I/O timeouts", "use epoll;"],
        ),
        "production adaptation checklist": (
            adaptation_guidance,
            [
                "domains",
                "filesystem paths",
                "service users",
                "file permissions",
                "forwarded-header trust",
                "Run deployment-host `nginx -t` against the fully adapted configuration",
            ],
        ),
    }
    for contract, (section, phrases) in guidance_contracts.items():
        if not section:
            failures.append(f"README must include {contract}")
            continue
        for phrase in phrases:
            if phrase not in section:
                failures.append(f"{contract} must include {phrase}")

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
    connect_timeout_plan = read("docs/plans/2026-06-10-upstream-connect-timeout.md")
    if "status: completed" not in connect_timeout_plan or "proxy_connect_timeout 5s" not in connect_timeout_plan:
        failures.append("upstream connect timeout plan must record status and verification")
    io_timeout_plan = read("docs/plans/2026-06-12-upstream-io-timeouts.md")
    io_timeout_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", io_timeout_plan)
    io_timeout_work = markdown_section(io_timeout_plan, "Work Completed")
    io_timeout_verification = markdown_section(io_timeout_plan, "Verification Completed")
    if io_timeout_status != ["completed"] or not io_timeout_work:
        failures.append("upstream I/O timeout plan must record one completed status and completed work")
    if not io_timeout_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", io_timeout_verification
    ):
        failures.append("upstream I/O timeout plan must record completed verification")
    for evidence in [
        "python3 -m py_compile scripts/check-nginx-examples.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "git diff --check",
        "27397838809",
        "27397840573",
        "2d892be8619d5b95d017a8a5f48ae7e67ddf6d0e",
        "proxy_connect_timeout 5s;",
        "proxy_read_timeout 30s;",
        "proxy_send_timeout 30s;",
    ]:
        if evidence not in io_timeout_verification:
            failures.append(f"upstream I/O timeout verification must record {evidence}")

    proxy_header_plan = read("docs/plans/2026-06-15-proxy-request-header-suppression.md")
    proxy_header_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", proxy_header_plan)
    proxy_header_verification = markdown_section(proxy_header_plan, "Verification Completed")
    if (
        proxy_header_status != ["completed"]
        or "All four Make gates passed" not in proxy_header_verification
        or "Six isolated hostile mutations were rejected" not in proxy_header_verification
        or "external directory" not in proxy_header_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", proxy_header_verification)
    ):
        failures.append("Proxy request header suppression plan must record completed verification")

    forwarded_for_plan = read("docs/plans/2026-06-15-forwarded-for-trust-boundary.md")
    forwarded_for_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", forwarded_for_plan)
    forwarded_for_verification = markdown_section(forwarded_for_plan, "Verification Completed")
    if (
        forwarded_for_status != ["completed"]
        or "All four Make gates passed" not in forwarded_for_verification
        or "Seven isolated hostile mutations were rejected" not in forwarded_for_verification
        or "external directory" not in forwarded_for_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", forwarded_for_verification)
    ):
        failures.append("Forwarded-For trust boundary plan must record completed verification")
    for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]:
        if "forwarded-for trust boundary" not in read(path).lower():
            failures.append(f"{path} must document the Forwarded-For trust boundary")
        if "forwarded header suppression" not in read(path).lower():
            failures.append(f"{path} must document Forwarded header suppression")

    forwarded_header_plan = read("docs/plans/2026-06-15-forwarded-header-suppression.md")
    forwarded_header_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", forwarded_header_plan)
    forwarded_header_verification = markdown_section(forwarded_header_plan, "Verification Completed")
    if (
        forwarded_header_status != ["completed"]
        or "All four Make gates passed" not in forwarded_header_verification
        or "Six isolated hostile mutations were rejected" not in forwarded_header_verification
        or "external directory" not in forwarded_header_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", forwarded_header_verification)
    ):
        failures.append("Forwarded header suppression plan must record completed verification")
    forwarded_host_boundary_plan = read("docs/plans/2026-06-15-forwarded-host-trust-boundary.md")
    forwarded_host_boundary_status = re.findall(
        r"(?mi)^status:\s*(.+?)\s*$", forwarded_host_boundary_plan
    )
    forwarded_host_boundary_verification = markdown_section(
        forwarded_host_boundary_plan, "Verification Completed"
    )
    if (
        forwarded_host_boundary_status != ["completed"]
        or "All four Make gates passed" not in forwarded_host_boundary_verification
        or "Seven isolated hostile mutations were rejected" not in forwarded_host_boundary_verification
        or "external directory" not in forwarded_host_boundary_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", forwarded_host_boundary_verification)
    ):
        failures.append("Forwarded Host trust boundary plan must record completed verification")

    guidance_plan = read("docs/plans/2026-06-13-sample-configuration-guidance.md")
    guidance_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", guidance_plan)
    guidance_work = markdown_section(guidance_plan, "Work Completed")
    guidance_verification = markdown_section(guidance_plan, "Verification Completed")
    if guidance_status != ["completed"] or not guidance_work:
        failures.append("sample configuration guidance plan must record completed status and work")
    if not guidance_verification or re.search(
        r"(?i)\b(?:pending|todo|tbd|not run)\b", guidance_verification
    ):
        failures.append("sample configuration guidance plan must record completed verification")
    for evidence in [
        "python3 -m py_compile scripts/check-nginx-examples.py",
        "make lint",
        "make test",
        "make build",
        "make check",
        "external working directory",
        "hostile mutations rejected",
        "git diff --check",
    ]:
        if evidence not in guidance_verification:
            failures.append(f"sample configuration guidance verification must record {evidence}")

    websocket_plan = read("docs/plans/2026-06-16-websocket-upgrade-proxying.md")
    websocket_status = re.findall(r"(?mi)^status:\s*(.+?)\s*$", websocket_plan)
    websocket_verification = markdown_section(websocket_plan, "Verification Completed")
    if (
        websocket_status != ["completed"]
        or "All four Make gates passed" not in websocket_verification
        or "Twelve isolated hostile mutations were rejected" not in websocket_verification
        or "external directory" not in websocket_verification
        or re.search(r"(?i)\b(?:pending|todo|tbd|not run)\b", websocket_verification)
    ):
        failures.append("WebSocket upgrade proxying plan must record completed verification")

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
        "actions/setup-python@a309ff8b426b58ec0e2a45f0f869d46889d02405",
        'python-version: "3.12"',
        "sudo apt-get update && sudo apt-get install --no-install-recommends -y nginx",
        "run: make check",
    ]:
        if expected not in workflow:
            failures.append(f"Check workflow must keep {expected}")
    workflow_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / ".github/workflows").iterdir()
        if path.is_file()
    )
    checkout_step = (
        "      - uses: actions/checkout@df4cb1c069e1874edd31b4311f1884172cec0e10\n"
        "        with:\n"
        "          persist-credentials: false"
    )
    if workflow_files != [".github/workflows/check.yml"]:
        failures.append("workflow inventory must contain only .github/workflows/check.yml")
    if workflow.count("actions/checkout@") != 1 or checkout_step not in workflow:
        failures.append("Check workflow must use one pinned credential-free checkout")
    if workflow.count("persist-credentials:") != 1 or "persist-credentials: true" in workflow:
        failures.append("Check workflow must not persist checkout credentials")
    if codeowners.strip() != "* @garethpaul":
        failures.append("CODEOWNERS must assign the repository to @garethpaul")
    checkout_plan = read("docs/plans/2026-06-12-checkout-credential-boundary.md")
    if (
        "status: completed" not in checkout_plan.lower()
        or "persist-credentials: false" not in checkout_plan
        or "hostile mutations rejected" not in checkout_plan
    ):
        failures.append("checkout credential plan must record completed verification")
    guidance = " ".join(
        "\n".join(read(path) for path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]).split()
    ).lower()
    if (
        "checkout credentials are not persisted" not in guidance
        or "credential-free checkout" not in guidance
    ):
        failures.append("repository guidance must document the credential-free checkout boundary")
    setup_plan = read("docs/plans/2026-06-10-setup-and-loopback-boundary.md")
    if "status: completed" not in setup_plan or "loopback-only" not in setup_plan:
        failures.append("setup and loopback boundary plan must record completed verification")
    review_plan = read("docs/plans/2026-06-19-proxy-boundary-review.md")
    if (
        "status: completed" not in review_plan
        or "Live Nginx" not in review_plan
        or "hostile mutations" not in review_plan
    ):
        failures.append("proxy boundary review plan must record completed runtime and mutation verification")

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
