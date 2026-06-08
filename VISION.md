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
- Avoid embedding real domain names, certificates, or private upstreams
- Maintain security policy for the examples
- Keep sample-only guardrails visible in README and checks

Next priorities:

- Keep README explanations for each config file current
- Keep syntax validation guidance with `nginx -t`
- Document which settings are sample-only and should be adapted before production
- Add TLS examples only with safe placeholders

Contribution rules:

- One PR = one focused config, comment, or documentation change.
- Use placeholders for domains, paths, and certificates.
- Run `make check` and verify config syntax with `nginx -t` where possible.
- Do not add production secrets or private infrastructure details.

## Security

Canonical security policy and reporting:

- [`SECURITY.md`](SECURITY.md)

Web server examples can be copied into production. They should avoid insecure
defaults, real secrets, and misleading claims about readiness.
Defaults such as `server_tokens off`, explicit forwarded headers, and non-debug
logging are part of the baseline.

## What We Will Not Merge (For Now)

- Private hostnames, upstreams, or certificate paths
- Production credentials
- TLS/security examples without clear placeholders
- Config changes without syntax guidance

This list is a roadmap guardrail, not a permanent rule.
Strong user demand and strong technical rationale can change it.
