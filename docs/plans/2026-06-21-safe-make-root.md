# Fail-Closed Make Root Metadata

status: completed

## Problem

`ROOT` was protected with GNU Make's `override` directive, but callers could
replace the automatic `MAKEFILE_LIST` metadata used to derive it. Command-line
or environment-preferred metadata redirected every verification recipe into an
unreviewed tree.

## Change

- Reject non-file origins for GNU Make's automatic `MAKEFILE_LIST` value before
  any recipe expands.
- Preserve the existing protected `ROOT` assignment.
- Add command-line and environment regressions for both variables.
- Run the root-policy suite through the normal `test`, `verify`, and `check`
  graph.

## Validation

- Four root-policy tests cover command-line and environment input.
- The complete static, mutation, and live loopback proxy gates remain required.
