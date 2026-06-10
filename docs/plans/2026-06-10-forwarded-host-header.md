# Forwarded Host Header

status: completed

## Context

The Tornado proxy sample normalizes the upstream `Host` header to Nginx
`$host` and already forwards client/protocol metadata. Upstream applications may
also consult `X-Forwarded-Host` when constructing external URLs, so the sample
should provide that value from the same normalized host source instead of raw
client host input.

## Objectives

- Add `proxy_set_header X-Forwarded-Host $host;` to the Tornado proxy sample.
- Reject raw `$http_host` forwarding in the static baseline.
- Preserve existing `Host`, `X-Forwarded-For`, and `X-Forwarded-Proto`
  behavior.
- Extend docs and baseline checks for the forwarded host header guard.

## Verification

- `scripts/check-nginx-examples.py`
- `make check`
- `git diff --check`
