# Proxy Request Header Suppression

status: in progress

## Problem

The Tornado reverse-proxy sample explicitly rewrites trusted forwarding headers
but otherwise passes client request headers upstream. A client-supplied `Proxy`
header is unnecessary for the application and can be interpreted by some
upstream runtimes or gateways as proxy configuration.

Nginx documents that assigning an empty value with `proxy_set_header` prevents
that request header from being sent to the proxied server.

## Scope

- Suppress the inbound `Proxy` request header in the proxied application
  location.
- Preserve Host, forwarding, scheme, upstream, timeout, retry, and static-file
  behavior.
- Add an exact dependency-free contract and synchronized security guidance.
- Do not add TLS, domains, credentials, or deployment-specific upstreams.

## Implementation

1. Add `proxy_set_header Proxy "";` beside the trusted forwarding headers.
2. Require exactly one suppression directive inside the proxied location and
   before `proxy_pass`.
3. Record the boundary in README, security, vision, and changes guidance.

## Verification

- Run checker compilation and all four Make gates from the repository plus the
  canonical gate from an external directory with explicit timeouts.
- Reject isolated mutations that remove suppression, assign a nonempty value,
  move it after `proxy_pass`, duplicate it, remove guidance, or leave the plan
  incomplete.
- Audit the exact diff, generated artifacts, credential patterns, config
  inventory, conflict markers, binaries, large files, and intended paths.

## Risks

- These remain sample configurations and require deployment-specific review.
- Live `nginx -t` is unavailable unless Nginx is installed; the maintained gate
  validates the source contract without starting a listener or upstream.
- The stacked base pull request must remain available and merge first.
