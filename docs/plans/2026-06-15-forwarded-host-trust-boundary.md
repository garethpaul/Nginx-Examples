# Forwarded Host Trust Boundary

Status: planned

## Problem

The Tornado sample forwards both `Host` and `X-Forwarded-Host` from Nginx
`$host`. This rejects malformed raw Host values, but a syntactically valid
client-selected Host still becomes trusted upstream metadata. The sample has a
fixed placeholder `server_name`, so its direct-edge default can pin upstream
host identity to that configured value instead.

## Scope

- Source upstream `Host` and `X-Forwarded-Host` from `$server_name` inside the
  Tornado proxy location.
- Reject `$host` and `$http_host` sources for those two upstream headers in the
  portable baseline.
- Keep the configured placeholder server name, Forwarded-For replacement,
  scheme forwarding, Proxy suppression, loopback upstreams, retry policy, body
  limit, and I/O timeouts unchanged.
- Document that deployments using aliases, trusted ingress, or canonical public
  hosts must adapt the pinned value deliberately.
- Add mutation-sensitive contracts and completed verification evidence.

## Files

- `sample_tornado_nginx.conf`
- `scripts/check-nginx-examples.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-forwarded-host-trust-boundary.md`

## Verification

- Run checker compilation, all four dependency-free Make gates, and the
  external-directory check.
- Reject isolated mutations for either client-derived host source, a missing or
  duplicate override, ordering drift, missing guidance, and stale plan status.
- Audit the exact diff, workflow/Makefile drift, generated artifacts,
  credentials, conflicts, binaries, large files, modes, and whitespace.

## Risks

- A copied deployment with multiple aliases may need a deliberate canonical
  host or trusted ingress contract rather than the placeholder `$server_name`.
- No live Nginx listener, upstream, domain, certificate, or request is available
  locally; validation remains dependency-free and source-based.
- This change must remain stacked on PR #8; neither pull request may be merged
  or closed without explicit owner authorization.

## Success Criteria

- Client-selected host values cannot become upstream `Host` or
  `X-Forwarded-Host` metadata in the sample.
- Both headers use exactly one configured-name override before `proxy_pass`.
- Existing proxy security, reliability, and sample-adaptation contracts remain
  intact.
