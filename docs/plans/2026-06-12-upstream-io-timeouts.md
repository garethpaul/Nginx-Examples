# Upstream I/O Timeouts

status: completed

## Context

The Tornado proxy example bounds upstream connection establishment at five
seconds, but permits a 200-second response wait and leaves request-send timeout
behavior implicit. Stalled upstream reads or writes can therefore retain proxy
resources far longer than the sample's connect boundary suggests.

## Priorities

1. Set explicit 30-second upstream read and send timeouts.
2. Keep the existing five-second connect timeout and error-only retry policy.
3. Protect exact timeout values with the static checker.
4. Document that deployments must tune values for their workloads.

## Implementation Units

### Tornado Proxy Example

File: `sample_tornado_nginx.conf`

Replace the 200-second read timeout with `30s` and add
`proxy_send_timeout 30s` in the shared HTTP proxy settings.

### Static Contract And Documentation

Files:

- `scripts/check-nginx-examples.py`
- `README.md`
- `SECURITY.md`
- `VISION.md`
- `CHANGES.md`
- `docs/plans/2026-06-12-upstream-io-timeouts.md`

Require connect/read/send timeout values, completed evidence, and deployment
tuning guidance.

## Verification

Completed locally on 2026-06-12:

- `python3 -m py_compile scripts/check-nginx-examples.py`
- `make lint`
- `make test`
- `make build`
- `make check`
- hostile mutations lengthening the read timeout or removing the send timeout
  were each rejected by the static contract
- `git diff --check`

Completed on GitHub Actions for implementation head
`e81f1630c0b6d9a0e798b85d8c4d943847991378`:

- push run `27397824585`: success
- pull-request run `27397825722`: success

## Boundaries

- Do not claim these examples are production-ready without host-specific review.
- Do not change upstream membership or retry behavior.
- Do not require a live Nginx process for the static baseline.
