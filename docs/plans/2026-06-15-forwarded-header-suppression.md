# Forwarded Header Suppression

Status: planned

## Problem

The Tornado sample replaces client-selected legacy forwarding headers, but it
does not override the standardized `Forwarded` request header. Nginx passes
original request headers to a proxied server by default, so an upstream that
prefers `Forwarded` could still consume attacker-selected host, scheme, or
client identity despite the hardened `X-Forwarded-*` values.

Nginx documents that assigning an empty value with `proxy_set_header` prevents
that field from being passed to the proxied server.

## Scope

- Suppress the inbound `Forwarded` header before `proxy_pass` in the direct-edge
  Tornado sample.
- Require exactly one ordered empty override and reject non-empty or duplicate
  Forwarded overrides.
- Preserve pinned host identity, replaced Forwarded-For identity, scheme
  forwarding, Proxy suppression, loopback upstreams, retries, body limits, and
  I/O timeouts.
- Add mutation-sensitive portable contracts and synchronized guidance.
- Keep the PHP sample, Makefile, workflow, certificates, and dependencies
  unchanged.

## Files

- `sample_tornado_nginx.conf`
- `scripts/check-nginx-examples.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-15-forwarded-header-suppression.md`

## Verification

- Run checker compilation, all four Make gates, and the absolute Makefile gate
  from an external directory.
- Reject isolated mutations for missing, non-empty, duplicate, or late
  suppression, missing guidance, and stale plan status.
- Audit the exact diff, workflow/Makefile and PHP-sample drift, generated
  artifacts, credentials, certificates/keys, conflicts, binaries, large files,
  modes, and whitespace.

## Risks

- Deployments behind a trusted proxy chain may deliberately construct a new
  standardized `Forwarded` header after defining that trust boundary.
- No live Nginx parser, listener, upstream, domain, certificate, or request is
  available locally; validation remains dependency-free and source-based.
- This change must remain stacked on PR #9; neither pull request may be merged
  or closed without explicit owner authorization.

## Success Criteria

- Client-supplied `Forwarded` metadata cannot reach the sample upstream.
- Exactly one empty override appears before `proxy_pass`.
- Existing proxy identity and reliability contracts remain intact.

## Primary Source

- <https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_set_header>
