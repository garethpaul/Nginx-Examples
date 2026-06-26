# Safe TLS Placeholder Example

Status: completed

## Context

The roadmap allowed a TLS example only when domains, certificate paths, keys,
and deployment policy remained explicit placeholders rather than production
infrastructure.

## Work Completed

- Added a template-only HTTPS server using `example.invalid` and `/path/to`
  certificate, key, pid, and content-root placeholders.
- Added a fixed-host HTTP redirect, TLS 1.2/1.3, shared session cache, bounded
  session lifetime, and disabled session tickets.
- Preserved shared response headers, request-body limit, token suppression, and
  fail-closed static-file handling.
- Deferred HSTS until domain ownership, HTTPS-only operation, renewal, rollback,
  and subdomain effects are validated by the deployment owner.
- Linked the official Nginx SSL module reference and required rendered
  deployment-host `nginx -t` validation.

## Scope Boundary

- No real domain, certificate, private key, upstream, filesystem path, or
  deployment-specific cipher policy.
- The checked-in template is intentionally not directly runnable because its
  certificate and filesystem paths must be replaced.

## Verification Completed

- The static contract failed first for the missing template, directives, docs,
  plan, and stale roadmap item.
- Root and external `make check` passed 12 checker mutations, seven live
  reverse-proxy tests, seven Make-root tests, and the static baseline.
- Sixteen isolated TLS mutations rejected placeholder, protocol, session,
  redirect, shared-header, HSTS, README, roadmap, and plan drift.
- Exact-head hosted Nginx and CodeQL gates remain required before merge.
