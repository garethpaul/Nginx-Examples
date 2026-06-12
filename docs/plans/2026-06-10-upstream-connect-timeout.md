# Upstream Connect Timeout

status: completed

## Problem

The Tornado reverse-proxy example bounds response reads but leaves upstream
connection establishment at the Nginx default. A stopped or unreachable local
backend can therefore hold proxy attempts much longer than necessary.

## Scope

- Set a five-second upstream connection timeout for the Tornado proxy.
- Preserve the existing 200-second response read timeout.
- Keep retries limited to communication errors.
- Add static and mutation guardrails without requiring a live Nginx process.
- Document the timeout as a sample default that deployments should review.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- mutate or remove the connect timeout and require the gate to fail
- `git diff --check`

## Work Completed

- Added `proxy_connect_timeout 5s` to the Tornado HTTP block.
- Preserved the existing 200-second response read timeout and error-only retry
  policy.
- Extended the static baseline with config and completed-plan assertions.
- Documented the five-second value as a sample default for deployment review.
