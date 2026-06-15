# Forwarded-For Trust Boundary

Status: planned

## Problem

The public Tornado proxy sample uses `$proxy_add_x_forwarded_for`, which keeps
an inbound client-supplied `X-Forwarded-For` value and appends the socket peer.
An upstream that selects the wrong list position can therefore treat a spoofed
address as the client identity.

## Scope

- Overwrite `X-Forwarded-For` with Nginx `$remote_addr` at the public listener.
- Require one exact override before `proxy_pass`.
- Preserve `X-Real-IP`, Host, forwarded host/proto, Proxy suppression,
  loopback upstreams, retry behavior, and I/O timeouts.
- Add mutation-sensitive static contracts and synchronized security guidance.

## Verification

- Run checker compilation and all four Make gates from the repository plus the
  canonical external-directory check with explicit timeouts.
- Reject isolated mutations for inherited forwarding, raw inbound forwarding,
  missing, reordered, or duplicate overrides, missing guidance, and stale plan
  status.
- Audit the exact diff, generated artifacts, credential patterns, config
  inventory, conflict markers, binaries, large files, and intended paths.

## Risks

- Deployments behind a trusted proxy chain may need a deliberate real-IP module
  configuration instead of this direct-edge sample boundary.
- No live Nginx listener, upstream, domain, certificate, or request was used.
- The change must remain stacked on PR #7; neither pull request may be merged or
  closed without explicit owner authorization.
