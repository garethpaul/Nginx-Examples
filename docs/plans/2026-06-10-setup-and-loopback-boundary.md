# Nginx Examples Setup And Loopback Boundary

status: completed

## Context

The sample configs are meant to be copied and adapted, not installed directly.
The Tornado proxy example also contains `http://frontends` as an Nginx upstream
group reference, not an active external HTTP integration.

## Changes

- Documented that checked-in configs require host-specific path adjustment before `nginx -t` or installation.
- Clarified that Tornado upstreams are loopback-only placeholders.
- Clarified that public HTTP upstreams, real hostnames, and private infrastructure require a separate design.
- Extended the static checker so the setup and loopback boundary remains visible.

## Verification

- `make check`
- `git diff --check`
