#!/usr/bin/env python3
"""Static checks for the Nginx example configuration baseline."""

from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_MAKEFILE = """ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
\tPYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-nginx-examples.py"
"""
CONFIGS = ["sample_php_nginx.conf", "sample_tornado_nginx.conf"]
REQUIRED = [
    ".gitignore",
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
    "docs/plans/2026-06-10-upstream-connect-timeout.md",
    "docs/plans/2026-06-10-hosted-static-validation.md",
    "docs/plans/2026-06-12-upstream-io-timeouts.md",
    "docs/plans/2026-06-12-checkout-credential-boundary.md",
    "docs/plans/2026-06-13-sample-configuration-guidance.md",
    "docs/plans/2026-06-13-location-independent-make.md",
    "docs/plans/2026-06-15-proxy-request-header-suppression.md",
    "docs/plans/2026-06-15-forwarded-for-trust-boundary.md",
    "docs/readme-overview.svg",
    "scripts/check-nginx-examples.py",
] + CONFIGS


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
        "proxy_set_header Host $server_name;",
        "proxy_set_header X-Forwarded-Host $server_name;",
        "proxy_set_header X-Forwarded-For $remote_addr;",
        "proxy_set_header X-Forwarded-Proto $scheme;",
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
        if phrase not in tornado:
            failures.append(f"sample_tornado_nginx.conf must include {phrase}")
    if "/home/ubuntu" in tornado:
        failures.append("sample_tornado_nginx.conf must use placeholder paths, not host-specific home paths")
    proxy_location = tornado.split("location / {", 1)[-1].split("\n        }", 1)[0]
    host_override = "proxy_set_header Host $server_name;"
    forwarded_host_override = "proxy_set_header X-Forwarded-Host $server_name;"
    host_override_index = proxy_location.find(host_override)
    forwarded_host_index = proxy_location.find(forwarded_host_override)
    forwarded_for_override = "proxy_set_header X-Forwarded-For $remote_addr;"
    forwarded_for_index = proxy_location.find(forwarded_for_override)
    proxy_suppression_index = proxy_location.find('proxy_set_header Proxy "";')
    proxy_pass_index = proxy_location.find("proxy_pass http://frontends;")
    if not (
        tornado.count(host_override) == 1
        and tornado.count(forwarded_host_override) == 1
        and 0 <= host_override_index < forwarded_host_index < proxy_pass_index
        and "proxy_set_header Host $host;" not in tornado
        and "proxy_set_header X-Forwarded-Host $host;" not in tornado
        and "$http_host" not in tornado
    ):
        failures.append("Tornado proxy requests must pin upstream host identity before proxy_pass")
    if not (
        tornado.count(forwarded_for_override) == 1
        and 0 <= forwarded_for_index < proxy_pass_index
        and "$proxy_add_x_forwarded_for" not in tornado
        and "$http_x_forwarded_for" not in tornado
    ):
        failures.append("Tornado proxy requests must replace untrusted X-Forwarded-For before proxy_pass")
    if not (
        tornado.count('proxy_set_header Proxy "";') == 1
        and 0 <= proxy_suppression_index < proxy_pass_index
    ):
        failures.append("Tornado proxy requests must suppress the inbound Proxy header before proxy_pass")
    if "proxy_pass_header Server;" in tornado:
        failures.append("sample_tornado_nginx.conf must not pass upstream Server headers")
    upstreams = re.findall(r"server\s+([^:;\s]+):\d+;", tornado)
    if not upstreams or any(host != "127.0.0.1" for host in upstreams):
        failures.append("sample_tornado_nginx.conf upstreams must stay loopback placeholders")

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
    if "make -f /path/to/Nginx-Examples/Makefile check" not in readme:
        failures.append("README must document location-independent Makefile invocation")
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
        "upstream I/O timeouts",
        "Proxy request header suppression",
    ]:
        if phrase not in docs:
            failures.append(f"docs must mention {phrase}")
    for relative_path in ["README.md", "SECURITY.md", "VISION.md", "CHANGES.md"]:
        if "proxy request header suppression" not in read(relative_path).lower():
            failures.append(f"{relative_path} must document Proxy request header suppression")
        if "forwarded host trust boundary" not in read(relative_path).lower():
            failures.append(f"{relative_path} must document the Forwarded Host trust boundary")

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

    hosted_plan = read("docs/plans/2026-06-10-hosted-static-validation.md")
    workflow = read(".github/workflows/check.yml")
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
