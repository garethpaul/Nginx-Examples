# Nginx Proxy Boundary Review

status: completed

## Context

PRs #2 and #4-#11 formed a linear proxy-maintenance stack. PR #1 was a
separate CI/setup root with overlapping checkout hardening and useful repository
ownership guidance. The review evaluated the combined tree rather than relying
on individual grep-based claims.

## Root Causes

- The proxy normalized host, address, scheme, `Forwarded`, and `Proxy` metadata
  but did not replace `X-Forwarded-Port`, so a client-selected value crossed the
  direct-edge boundary.
- The WebSocket map treated every nonempty `Upgrade` value as an upgrade and
  forwarded the original token, allowing unrelated protocols such as `h2c` to
  reach a Tornado upstream.
- The static checker searched raw source text for several directives, so a
  commented-out safety line could satisfy the gate.

## Changes

- Replaced `X-Forwarded-Port` with `$server_port` before `proxy_pass`.
- Added a WebSocket-only sanitization map and derived `Connection` from the
  sanitized value.
- Made config assertions ignore comments and protected the no-URI `proxy_pass`
  path/query behavior.
- Added hostile checker mutations and a live Nginx loopback backend suite for
  forwarding metadata, Upgrade behavior, request URI preservation, and the
  one-megabyte body limit.
- Integrated CODEOWNERS, AGENTS guidance, and setup/loopback documentation from
  PR #1.

## Verification Completed

- `python3 -m py_compile scripts/check-nginx-examples.py scripts/test-check-nginx-examples.py scripts/test-nginx-proxy.py`
- `make lint`, `make test`, `make build`, and `make check`
- External-directory Make gates
- Live Nginx 1.31.2 syntax and reverse-proxy tests
- Seven isolated hostile mutations rejected
- `git diff --check`

## Deployment Risks

- The checked-in listener is HTTP-only and assumes direct client connections.
- Deployments behind trusted proxies must configure exact real-IP trust CIDRs
  and trusted scheme/port normalization.
- HSTS belongs only on a fully deployed HTTPS virtual host.
- Streaming and WebSocket deployments must adapt buffering, ping cadence, and
  the 30-second read timeout.
- Application-specific headers remain end-to-end unless explicitly replaced;
  upstream applications must not trust arbitrary client headers as identity.
