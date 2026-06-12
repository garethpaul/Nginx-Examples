## Nginx Examples Vision

This document explains the current state and direction of the project.
Project overview and developer docs: [`README.md`](README.md)

Nginx Examples is a small collection of sample Nginx configuration files for PHP
and Tornado-style upstream proxying.

The repository is useful as a compact reference for server blocks, proxy
headers, gzip settings, access logs, and upstream configuration.

The goal is to keep the examples readable and clearly marked as samples rather
than production-ready drop-ins.

The current focus is:

Priority:

- Preserve PHP and Tornado example configuration files
- Keep logging, gzip, proxy, and upstream settings easy to inspect
- Keep PHP sample includes limited to `sites-enabled/*.conf`
- Keep request body size limits explicit in both samples
- Avoid embedding real domain names, certificates, or private upstreams
- Maintain security policy for the examples
- Keep sample-only guardrails visible in README and checks
- Keep upstream server header disclosure disabled in proxy samples
- Keep `X-Forwarded-Host` tied to Nginx `$host` in proxy samples
- Keep static-file handling explicit with `try_files $uri =404`
- Keep browser MIME-sniffing protection visible in both samples
- Keep the sample clickjacking guard visible in both samples
- Keep the sample referrer policy guard visible in both samples
- Keep `make lint`, `make test`, `make build`, and `make check` on the
  SDK-free static baseline
- Keep setup docs clear that operators should not install the checked-in
  configs directly
- Keep Tornado proxy examples scoped to loopback-only upstream placeholders

Next priorities:

- Keep README explanations for each config file current
- Keep syntax validation guidance with `nginx -t`
- Document which settings are sample-only and should be adapted before production
- Add TLS examples only with safe placeholders

Contribution rules:

- One PR = one focused config, comment, or documentation change.
- Use placeholders for domains, paths, and certificates.
- Run `make lint`, `make test`, `make build`, and `make check`, then verify
  config syntax with `nginx -t` where possible.
- Do not add production secrets or private infrastructure details.
- Preserve the Tornado static `try_files $uri =404` guard.
- Preserve `X-Forwarded-Host` when changing Tornado proxy headers.
- Preserve `X-Content-Type-Options: nosniff` when changing sample headers.
- Preserve `Referrer-Policy: strict-origin-when-cross-origin` when changing
  sample headers.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Web server examples can be copied into production. They should avoid insecure
defaults, real secrets, and misleading claims about readiness.
Defaults such as `server_tokens off`, `proxy_hide_header Server`, explicit
forwarded headers including `X-Forwarded-Host`, `client_max_body_size`,
`X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`,
`Referrer-Policy: strict-origin-when-cross-origin`, and non-debug logging are
part of the baseline.
The Tornado static location also keeps `try_files $uri =404`.

## What We Will Not Merge (For Now)

- Private hostnames, upstreams, or certificate paths
- Production credentials
- TLS/security examples without clear placeholders
- Config changes without syntax guidance

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
