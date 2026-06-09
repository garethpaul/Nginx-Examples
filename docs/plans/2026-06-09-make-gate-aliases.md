# Make Gate Aliases

status: completed

## Context

The repository had a working `make check` static baseline, but the shared
maintenance workflow also runs `make lint`, `make test`, and `make build`
before pushing. Those commands should reach the same SDK-free verifier on hosts
without Nginx installed.

## Objectives

- Add `make lint`, `make test`, and `make build` aliases.
- Keep `make check` and `make verify` on the static baseline.
- Preserve bytecode-free checker execution.
- Extend docs and the static baseline for the standard gate contract.

## Verification

- `make lint`
- `make test`
- `make build`
- `make check`
- `git diff --check`
