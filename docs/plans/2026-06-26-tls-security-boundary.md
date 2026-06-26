# TLS Security Boundary

Status: completed

## Context

`SECURITY.md` still said that the examples were HTTP-only after
`sample_tls_nginx.conf.example` was added. The runnable PHP and Tornado samples
remain HTTP-only, but the repository now also contains an intentionally
non-runnable HTTPS template. Treating those as the same boundary can mislead an
operator about what has syntax, certificate, and deployment evidence.

## Decision

Scope the HTTP-only statement to the runnable samples and state explicitly that
the TLS file requires replacement of its domain, certificate, key, pid, and
content-root placeholders followed by deployment-host `nginx -t`.

## Verification

- The static checker failed first on the stale security wording.
- The checker requires both the runnable HTTP boundary and the non-runnable TLS
  template boundary, and rejects the old unqualified claim.
- The mutation suite replaces the scoped statement with the stale wording and
  requires the checker to reject it.
- Root and external full gates passed 13 checker mutations, seven live Nginx
  proxy tests, seven Make-root tests, and the static baseline.
- Pull request #18 implementation head
  `ba89dbc5ffbafbea3f07d8e14ad13ae45771a14e` passed both hosted Nginx
  baselines, CodeQL actions and Python analyses, and the aggregate gate.
- Required Codex review was attempted against `origin/master`; the helper
  stopped before analysis because OpenAI WebSocket and HTTPS transports both
  returned HTTP 401. Local, remote, and pull-request heads were identical, and
  an immutable manual fallback review found no actionable defects.
