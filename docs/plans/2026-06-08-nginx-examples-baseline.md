# Nginx Examples Baseline Plan

status: completed

## Context

`Nginx-Examples` contains sample Nginx configurations for PHP-style site
includes and Tornado upstream proxying.

## Risks

- The PHP sample defaulted error logging to `debug`.
- The examples did not disable Nginx version disclosure with `server_tokens off`.
- The Tornado proxy passed the raw client Host header and omitted common
  forwarded headers.
- There was no automated verification path for config-review guardrails.
- The README did not explain how to adapt sample-only paths before production
  or how to run `nginx -t` on a host with Nginx installed.

## Work Completed

- Added safer sample defaults for logging, `server_tokens`, placeholder server
  names, and forwarded proxy headers.
- Documented deployment-specific include/static paths and Linux-specific `epoll`
  usage.
- Added `Makefile` and `scripts/check-nginx-examples.py` static verification.
- Updated README, security policy, vision, overview image, and changelog.

## Verification

- `make check`
- `git diff --check`

`nginx` is not installed on this host. Run `nginx -t` with local path
adjustments on a system that has Nginx installed before copying these examples
into a live deployment.
