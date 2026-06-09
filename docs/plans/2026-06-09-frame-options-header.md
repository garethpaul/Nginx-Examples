# Frame Options Header

status: completed

## Context

The sample Nginx configs already include conservative placeholders for version
disclosure, request body size, upstream header exposure, and MIME sniffing. They
did not include a clickjacking header, so copied examples could omit that
baseline browser hardening by default.

## Objectives

- Add `X-Frame-Options: SAMEORIGIN` to both sample configs.
- Use `always` so the header is present on non-2xx responses as well.
- Extend the static checker and docs for the frame-options header baseline.

## Verification

- `make check`
- `python3 scripts/check-nginx-examples.py`
- `git diff --check`
