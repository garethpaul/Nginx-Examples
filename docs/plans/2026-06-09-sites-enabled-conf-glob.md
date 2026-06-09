# Sites-Enabled Config Glob Plan

status: completed

## Context

The PHP sample included every file under `sites-enabled`. That pattern is convenient but can accidentally load editor backups, temporary files, or other non-config files.

## Objectives

- Limit the sample include pattern to `sites-enabled/*.conf`.
- Keep the include path clearly marked as deployment-specific.
- Extend the static baseline and docs so the narrower include remains visible.

## Verification

- `python3 scripts/check-nginx-examples.py`
- `make check`
- `git diff --check`
