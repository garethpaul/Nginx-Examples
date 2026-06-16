---
title: WebSocket Upgrade Proxying
status: completed
date: 2026-06-16
---

# WebSocket Upgrade Proxying

## Priority

P1 proxy compatibility. The Tornado sample currently drops the hop-by-hop
headers required for a WebSocket handshake, so WebSocket handlers cannot be
reached through the documented reverse proxy.

## Problem

Nginx does not pass client `Upgrade` and `Connection` headers to an upstream by
default. The Tornado sample proxies all application traffic through one
location but does not explicitly forward WebSocket upgrade intent or select
HTTP/1.1 for Nginx versions before 1.29.7.

## Approach

- Add the official mixed-traffic `map` from client upgrade intent to an
  upstream `Connection` value.
- Set the upstream proxy HTTP version and forward `Upgrade` plus the mapped
  `Connection` header before `proxy_pass`.
- Preserve the direct-edge forwarded-header trust boundary, timeouts, static
  handling, PHP sample, and all existing security headers.
- Extend the dependency-free checker, maintained guidance, changelog, and
  completed verification evidence.

## Primary Sources

- Nginx WebSocket proxying:
  <https://nginx.org/en/docs/http/websocket.html>
- Tornado WebSocket handler documentation:
  <https://www.tornadoweb.org/en/stable/websocket.html>

## Files

- `sample_tornado_nginx.conf`
- `scripts/check-nginx-examples.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-16-websocket-upgrade-proxying.md`

## Verification

- Prove the map is unique, scoped to `http`, and distinguishes upgrade from
  ordinary traffic.
- Prove the HTTP version and both upgrade headers are unique and ordered before
  `proxy_pass` without weakening existing proxy identity controls.
- Run all repository and external-directory Make gates.
- Reject isolated map, version, header, ordering, guidance, changelog, and
  completed-plan mutations.
- Audit the exact diff, generated artifacts, credentials, certificates, keys,
  conflict markers, binaries, large files, modes, and whitespace.

## Scope Boundaries

- Do not add a WebSocket endpoint, alter upstream membership, change timeout
  values, or claim that every deployment needs WebSockets.
- Do not change the PHP sample, workflow, Makefile, TLS posture, domains, paths,
  or certificate placeholders.
- Keep PR #10 and its predecessors open and retain base-first stack ordering.

## Success Criteria

- The Tornado proxy sample can preserve WebSocket handshake intent while
  ordinary HTTP requests use a non-upgrade connection value.
- Existing proxy trust and reliability contracts remain unchanged.

## Work Completed

- Added one `http`-scoped upgrade map with distinct upgrade and ordinary
  request branches.
- Added explicit upstream HTTP/1.1 plus ordered `Upgrade` and mapped
  `Connection` headers before `proxy_pass`.
- Extended the static baseline and maintained guidance while preserving every
  existing trust, timeout, static-file, workflow, and PHP-sample contract.

## Verification Completed

- All four Make gates passed from the repository root and an external directory.
- Twelve isolated hostile mutations were rejected across map presence, scope,
  and both branches, HTTP version, upgrade headers, directive ordering, README,
  SECURITY, VISION, and changelog evidence.
- The focused Python checker passed before and after the completed-plan
  contract was added.
- Exact diff, generated artifact, credential, certificate/key, conflict marker,
  binary, large-file, mode, and whitespace audits passed for intended files.
- Live `nginx -t` was unavailable because Nginx is not installed; deployment
  hosts must still validate their fully adapted configuration before reload.
