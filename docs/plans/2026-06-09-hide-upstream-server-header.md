# Hide Upstream Server Header

status: completed

## Context

The Tornado reverse proxy example already disables Nginx version disclosure
with `server_tokens off`, but the proxy location explicitly passed the upstream
`Server` response header. That could expose framework or app server version
details when copied into a deployment.

## Objectives

- Remove the explicit upstream `Server` header pass-through.
- Add `proxy_hide_header Server` in the Tornado proxy location.
- Extend the static checker so upstream `Server` header disclosure stays
  disabled.
- Document the proxy-header baseline in README, security, vision, and changes.

## Verification

- `make check`
- `python3 scripts/check-nginx-examples.py`
- `git diff --check`

`nginx` is not installed on this host. Run `nginx -t` with adjusted local paths
on a host that has Nginx installed before using the sample in production.
