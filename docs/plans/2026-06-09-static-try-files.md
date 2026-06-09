# Static Try Files Plan

status: completed

## Context

The Tornado sample serves `/static/` from a placeholder root. Without an
explicit `try_files` rule, copied configurations can be harder to reason about
when a requested asset is missing or the static root is adapted incorrectly.

## Objectives

- Add `try_files $uri =404;` to the Tornado static location.
- Preserve the placeholder static root and query-string cache behavior.
- Extend the static checker and docs so the static-file guard remains visible.

## Verification

- `make check`
- `git diff --check`
