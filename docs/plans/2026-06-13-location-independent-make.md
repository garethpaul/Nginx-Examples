# Location-Independent Nginx Example Verification

status: completed

## Context

The dependency-free Make aliases invoke `scripts/check-nginx-examples.py`
relative to the caller's working directory. An absolute Makefile invocation
from elsewhere can therefore fail or inspect the wrong tree.

## Objectives

- Resolve every Make alias from the checkout containing the loaded Makefile.
- Preserve the existing target graph and `PYTHON` override.
- Enforce the exact rooted recipe, operator guidance, completed status, and
  verification evidence in the active checker.
- Prove root and external-directory behavior with mutation-sensitive checks.

## Implementation Units

### Make Contract

Files: `Makefile` and `scripts/check-nginx-examples.py`.

Derive one absolute root from the loaded Makefile and invoke the checker by
absolute path. Require the complete small Makefile so aliases, the Python
override, and path resolution cannot drift independently.

### Documentation And Evidence

Files: `README.md`, `CHANGES.md`, and this plan.

Document absolute Makefile invocation and record bounded local and hostile
mutation verification after it completes.

## Boundaries

- Do not change the PHP or Tornado Nginx sample configurations, workflows,
  dependencies, or deployment behavior.
- Do not claim live Nginx syntax, upstream, TLS, filesystem, or service
  validation.
- Preserve the existing stacked PR chain and exact-head evidence.

## Work Completed

- Rooted every dependency-free Make alias at the checkout containing the loaded
  Makefile while preserving the target graph and `PYTHON` override.
- Added exact Makefile, README invocation, completed status, and verification
  evidence contracts to `scripts/check-nginx-examples.py`.
- Documented absolute Makefile invocation without changing either Nginx sample
  configuration or hosted workflow behavior.

## Verification Completed

- Root and external-directory `lint`, `test`, `build`, `verify`, and `check`
  gates passed through the checkout's absolute Makefile path.
- `python3 -m py_compile scripts/check-nginx-examples.py` and
  `git diff --check` passed.
- Six isolated hostile mutations covering root derivation, checker resolution,
  alias delegation, the Python override, completed plan evidence, and README
  invocation guidance were rejected by the intended contracts.
- Intended-path, secret-pattern, conflict-marker, generated-artifact, sample
  configuration, workflow, and credential-boundary audits passed; live Nginx
  syntax and deployment behavior remain explicitly unverified.
