# Nginx-Examples

<!-- README-OVERVIEW-IMAGE -->
![Project overview](docs/readme-overview.svg)

## Overview

`garethpaul/Nginx-Examples` is a small set of sample Nginx configurations for
PHP-style site includes and Tornado upstream proxying.

This README is based on the checked-in source, manifests, scripts, and repository metadata on the `master` branch. The project language mix found during review was: no dominant source language detected.

## Repository Contents

- `.gitignore` - local environment/log/test-output ignores
- `CHANGES.md` - baseline change log
- `Makefile` - host-portable static verification entry point
- `README` - compatibility pointer to this README
- `SECURITY.md` - security reporting and disclosure guidance
- `VISION.md` - project direction and maintenance guardrails
- `sample_php_nginx.conf` - full Nginx config skeleton with PHP/site include hooks
- `sample_tornado_nginx.conf` - reverse proxy example for local Tornado workers
- `scripts/check-nginx-examples.py` - static baseline checks used by `make check`

Additional scan context:

- Source directories: no top-level source directories detected
- Dependency and build manifests: none detected
- Entry points or build surfaces: `sample_php_nginx.conf`, `sample_tornado_nginx.conf`
- Test-looking files: `scripts/check-nginx-examples.py`

## Getting Started

### Prerequisites

- Git
- Python 3 for `make check`
- Nginx for real syntax checks with `nginx -t`

### Setup

```bash
git clone https://github.com/garethpaul/Nginx-Examples.git
cd Nginx-Examples
make lint
make test
make build
make check
```

The setup commands above are derived from repository files. Legacy mobile, Python, or JavaScript samples may require older SDKs or package versions than a modern workstation uses by default.

## Running or Using the Project

- Treat both configs as sample-only starting points, not production-ready drop-ins.
- `sample_php_nginx.conf` is a full `nginx.conf`-style skeleton. Adjust the user, pid path, log paths, `mime.types`, and `sites-enabled/*.conf` include path for the deployment host.
- `sample_tornado_nginx.conf` proxies to loopback Tornado workers on ports 8000-8003 and sets `Host`, `X-Real-IP`, `X-Forwarded-Host`, `X-Forwarded-For`, and `X-Forwarded-Proto` headers. It also hides upstream `Server` headers with `proxy_hide_header Server`. Replace `/srv/example-app` with the deployment host's static root.
- The Tornado static location uses `try_files $uri =404;` so missing static
  assets fail closed instead of falling through to another handler.
- The Tornado upstream connect timeout limits failed loopback connection setup
  to five seconds while preserving the longer application response window.
- Both samples set `client_max_body_size 1m;` as a conservative placeholder;
  adjust it deliberately for routes that need larger request bodies.
- Both samples set `X-Content-Type-Options: nosniff` with `always` so copied
  examples do not invite browser MIME sniffing by default.
- Both samples set `X-Frame-Options: SAMEORIGIN` with `always` as a sample
  clickjacking guard.
- Both samples set `Referrer-Policy: strict-origin-when-cross-origin` with
  `always` as a sample referrer-leakage guard.
- `use epoll;` is Linux-specific. Remove or change it on platforms that do not support epoll.

## Testing and Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- Pinned `ubuntu-24.04` GitHub Actions runs the static configuration/security
  baseline on Python 3.12. Deployment-host `nginx -t` remains required after
  adapting local paths and modules.
- `nginx -t -c /path/to/adjusted/nginx.conf` on a host with Nginx installed

The checked-in configs use host-specific paths such as `mime.types`, log files,
static roots, and include directories. Adjust those paths before running
`nginx -t` or installing the examples.
The PHP sample keeps `sites-enabled/*.conf` so backup files or stray files are
not included as config by default.
Both samples include `client_max_body_size` so copied examples do not silently
inherit an overly broad upload/request-body policy.

When the required SDK or runtime is unavailable, use static checks and source review first, then verify on a machine that has the matching platform toolchain.

## Configuration and Secrets

- No required secret or credential file was identified in the repository scan.
- Keep real domains, private upstreams, certificate paths, environment files, generated logs, and pid files out of git.

## Security and Privacy Notes

- Both examples disable `server_tokens` with `server_tokens off`.
- The Tornado proxy example also hides upstream `Server` response headers with `proxy_hide_header Server`.
- Preserve the upstream connect timeout or document a deployment-specific replacement.
- The Tornado static location should keep `try_files $uri =404;` before use in
  live deployments.
- Both examples cap request bodies with `client_max_body_size` as a sample
  default.
- Both examples send `X-Content-Type-Options: nosniff` as a sample browser
  hardening header.
- Both examples send `X-Frame-Options: SAMEORIGIN` as a sample clickjacking
  guard.
- Both examples send `Referrer-Policy: strict-origin-when-cross-origin` as a
  sample referrer-leakage guard.
- Review changes touching network requests, sockets, proxy headers, upstreams, or service endpoints; examples from the scan include sample_tornado_nginx.conf.
- Review changes touching file, media, JSON, XML, CSV, OCR, or data parsing; examples from the scan include sample_php_nginx.conf, sample_tornado_nginx.conf.
- Review changes touching infrastructure, proxy, cloud, or deployment configuration; examples from the scan include sample_php_nginx.conf, sample_tornado_nginx.conf.
- Keep forwarded-header handling explicit; `X-Forwarded-Host`,
  `X-Forwarded-For`, and `X-Forwarded-Proto` are part of the Tornado proxy
  example.
- Keep `X-Forwarded-Host` sourced from Nginx `$host`, not raw client
  `$http_host`.

## Maintenance Notes

- Run `make lint`, `make test`, `make build`, and `make check` before changing
  sample configs.
- Run `nginx -t` on a host with Nginx installed after adapting local paths.
- See `docs/plans/2026-06-09-make-gate-aliases.md` for the local verification
  gate aliases.
- See `docs/plans/2026-06-10-forwarded-host-header.md` for the forwarded host
  header guardrail.
- See `SECURITY.md` for vulnerability reporting and safe research guidance.
- See `VISION.md` for project direction and contribution guardrails.

## Contributing

Keep changes small and tied to the project that is already present in this repository. For code changes, document the toolchain used, avoid committing generated dependency directories or local configuration, and update this README when setup or verification steps change.
