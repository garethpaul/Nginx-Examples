# Spaced Absolute Makefile Path Verification

status: completed

## Context

GNU Make list functions split a loaded absolute Makefile path at whitespace.
Recipes also expanded the derived root inside double quotes, where backticks in
a checkout name remained active shell command substitutions.

## Scope

1. Derive the checkout root from the complete `MAKEFILE_LIST` value.
2. Shell-quote the authoritative root once for every recipe.
3. Preserve the root against command-line and environment input.
4. Exercise all nine Make aliases from hostile external paths.

## Verification

- Dry-run coverage checks all nine aliases with spaces, brackets, apostrophes,
  double quotes, and both root override channels.
- Executable coverage runs the static checker, seven mutation tests, and five
  live loopback Nginx tests from a hostile checkout path.
- A controlled backtick command-substitution path cannot execute its marker.
- The four root metadata tests from the prerequisite layer remain green.

## Risk And Rollback

This changes dependency-free verification root discovery and shell quoting only.
It does not alter Nginx directives, upstream trust boundaries, WebSocket
handling, timeout policy, or runtime proxy behavior.
