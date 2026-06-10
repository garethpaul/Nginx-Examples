# Hosted Static Validation

status: completed

## Context

The repository has static checks for Nginx security headers, proxy metadata,
request limits, include patterns, static-file handling, placeholders, and
balanced configuration structure, but no hosted validation. Real `nginx -t`
requires deployment-specific path adjustment and the target host's modules.

## Priorities

1. Run the canonical static gate on pinned hosted Linux.
2. Enforce read-only permissions, concurrency, timeout, and pinned actions.
3. Keep target-host `nginx -t` as an explicit deployment verification step.
4. Avoid production paths, certificates, private infrastructure, and secrets.

## Implementation Units

Files:

- `.github/workflows/check.yml`
- `scripts/check-nginx-examples.py`
- `README.md`
- `VISION.md`
- `SECURITY.md`
- `CHANGES.md`

Add push, pull-request, and manual triggers; read-only permissions; concurrency
cancellation; a bounded `ubuntu-24.04` job; commit-pinned checkout and Python
setup; and `make check`. Require that contract from the baseline checker.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- workflow YAML parse
- `git diff --check`
- successful hosted Linux `Check` workflow for the pushed commit

## Boundaries

- Do not treat hosted static checks as deployment-host `nginx -t` validation.
- Do not add production paths, certificates, infrastructure names, or secrets.
