# Content Type Nosniff Header

status: completed

## Context

The Nginx examples may be copied into new deployments. They already disable
server version disclosure, cap request bodies, and fail static misses closed,
but they did not include a browser MIME-sniffing guard.

## Objectives

- Add `X-Content-Type-Options: nosniff` to both sample configs.
- Use the `always` flag so error responses keep the sample header.
- Extend static checks and docs so the header remains visible.
- Keep the examples sample-only and avoid adding broader app-specific headers.

## Verification

- `make check`
- `python3 scripts/check-nginx-examples.py`
- `git diff --check`

`nginx` is not installed on this host. Run `nginx -t` with adjusted local paths
on a host that has Nginx installed before using the sample in production.
