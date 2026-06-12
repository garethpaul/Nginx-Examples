# Nginx Examples Setup And Loopback Boundary

status: completed

## Context

The sample configs are meant to be copied and adapted, not installed directly.
The Tornado proxy example also contains `http://frontends` as an Nginx upstream
group reference, not an active external HTTP integration. The setup docs needed
to make that boundary explicit.

## Changes

- Documented that checked-in configs require host-specific path adjustment
  before `nginx -t` or installation.
- Clarified that Tornado upstreams are loopback-only upstream placeholders.
- Clarified that public HTTP upstreams, real hostnames, and private
  infrastructure details require a separate design before being added.
- Extended the static checker so README, VISION, and SECURITY keep this setup
  and loopback boundary visible.

## Verification

- `make check`
- `git diff --check`
