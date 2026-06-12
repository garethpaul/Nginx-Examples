# Checkout Credential Boundary

status: completed

## Context

Canonical PR #3 runs a read-only static hosted gate and performs no
authenticated Git operation after checkout, but the action default retained the
workflow token in the runner's Git configuration.

## Implementation

- Set `persist-credentials: false` on the one commit-pinned checkout step.
- Require exactly one checkout action and only the canonical workflow file.
- Preserve Ubuntu 24.04, Python 3.12, read-only permission, timeout,
  concurrency, and `make check` command.
- Preserve all Nginx proxy, static-file, header, body-size, and timeout checks.

## Verification

- `make lint`, `make test`, `make build`, and `make check` passed.
- The checker passed from an external working directory.
- Workflow YAML parsing, Python compilation, and `git diff --check` passed.
- Focused hostile mutations rejected a missing or true credential setting,
  duplicate checkout action, extra workflow file, incomplete plan, and stale
  documentation; all hostile mutations rejected.
- Exact-head hosted verification remains pending until this successor is
  pushed.

## Boundaries

- Do not change sample Nginx configuration behavior in this unit.
- Do not add post-checkout pushes, tags, or authenticated Git fetches.
