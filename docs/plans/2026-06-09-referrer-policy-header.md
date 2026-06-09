# Referrer Policy Header

status: completed

## Context

The sample configs already include `X-Content-Type-Options` and
`X-Frame-Options` browser hardening headers. A copied config should also include
a conservative referrer policy so cross-origin navigation does not leak full
paths by default.

## Objectives

- Add `Referrer-Policy: strict-origin-when-cross-origin` to both sample configs.
- Keep the header marked `always`, matching the other browser hardening headers.
- Extend the static baseline and docs so the header stays visible in copied
  examples.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
