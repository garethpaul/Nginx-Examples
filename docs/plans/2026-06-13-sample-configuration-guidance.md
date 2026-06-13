# Sample Configuration Guidance

status: planned

## Context

The repository states that its Nginx configurations are sample-only, but the
README presents their behavior and deployment substitutions as one long list.
Readers must infer which paths, upstreams, platform assumptions, and policy
values belong to each file before they can adapt and validate a configuration.

## Priorities

1. Give each sample configuration a concise purpose and adaptation checklist.
2. Distinguish checked-in safeguards from deployment-specific policy choices.
3. Keep `nginx -t` guidance honest about host paths, modules, and permissions.
4. Protect the guidance with focused static contracts and hostile mutations.

## Implementation Units

### Per-File Guidance

File: `README.md`

Document the PHP skeleton and Tornado reverse proxy separately, including the
paths, users, domains, upstreams, timeouts, body limits, and platform-specific
directives that operators must review before deployment.

### Maintenance And Security Boundaries

Files:

- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`

Record that sample values are not production policy and that adapted configs
need deployment-host syntax validation before installation or reload.

### Static Contract

Files:

- `scripts/check-nginx-examples.py`
- `docs/plans/2026-06-13-sample-configuration-guidance.md`

Require the per-file guidance, production adaptation boundaries, completed
plan evidence, and deployment-host `nginx -t` instruction.

## Verification Plan

- `python3 -m py_compile scripts/check-nginx-examples.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- run the checker outside the repository working directory
- parse the workflow YAML
- run focused hostile mutations against the new guidance contract
- `git diff --check`
- scan the intended diff for secrets and generated artifacts

## Boundaries

- Do not change either sample Nginx configuration in this unit.
- Do not claim static checks replace `nginx -t` on the deployment host.
- Do not prescribe universal production values for workload-specific settings.
- Do not add TLS examples without safe placeholders and separate validation.
