# Changes

## 2026-06-26 - P2 - Correct the TLS security boundary

### Summary

Corrected stale security guidance that described the entire repository as
HTTP-only after the non-runnable TLS placeholder template was added.

### Work completed

- Scoped the HTTP-only statement to the runnable PHP and Tornado examples.
- Identified the checked-in TLS file as a template that still requires a real
  domain, certificate, key, filesystem paths, and deployment-host `nginx -t`.
- Added a fail-closed static policy and hostile mutation for this distinction.

### Validation

- RED: the static checker rejected the stale `SECURITY.md` wording before the
  policy was corrected.
- GREEN: the focused checker and hostile mutation suite pass with the corrected
  runnable-versus-template boundary.
- Implementation head `ba89dbc5ffbafbea3f07d8e14ad13ae45771a14e`
  passed both hosted Nginx baselines, CodeQL actions and Python analyses, and
  the CodeQL aggregate gate on pull request #18.
- Required Codex review was attempted against `origin/master` and stopped
  before analysis because both WebSocket and HTTPS transports returned OpenAI
  HTTP 401. Immutable local, remote, and pull-request heads matched, and the
  manual fallback review found no actionable defects.

## 2026-06-26 06:23 - P2 - Add a safe TLS placeholder template

### Summary

Closed the TLS roadmap item with a deliberately non-runnable, contract-enforced
template that requires deployment ownership and rendered syntax validation.

### Work completed

- Added `example.invalid` and `/path/to` certificate, key, pid, and root values.
- Added TLS 1.2/1.3, fixed-host redirect, bounded session reuse, and disabled
  session tickets while preserving shared sample guards.
- Deferred HSTS until HTTPS-only operation, renewal, rollback, and subdomain
  consequences are validated.
- Added README adaptation guidance, a completed plan, and static contracts.

### Threads

- Started: safe TLS placeholder example.
- Continued: continuous open-source maintenance loop.
- Stopped: none.

### Files changed

- `sample_tls_nginx.conf.example` — template-only TLS server.
- `README.md`, `VISION.md` — usage guidance and roadmap state.
- `scripts/check-nginx-examples.py` — TLS template contract.
- `docs/plans/2026-06-25-safe-tls-placeholder.md` — completed plan.
- `CHANGES.md` — this cycle record.

### Validation

- Red static contract — failed for the missing template, directives, docs,
  plan, and stale roadmap item before implementation.
- Root and external `make check` — passed 12 checker mutations, seven live
  reverse-proxy tests, seven Make-root tests, and the static baseline.
- Sixteen isolated TLS mutations — all rejected across placeholders, protocol,
  session, redirect, header, HSTS, README, roadmap, and plan boundaries.
- Hosted Nginx and CodeQL results pending.

### Bugs / findings

- P2: The roadmap requested TLS guidance but no safe certificate/domain
  placeholder existed, leaving operators to improvise from unrelated samples.
- P2: Enabling HSTS in a generic sample would create unsafe persistence and
  subdomain assumptions without deployment ownership.

### Blockers

- The checked-in template cannot pass `nginx -t` until an operator supplies a
  real certificate, private key, domain, pid path, and content root.

### Next action

- Run static/live baseline and hostile template mutations, then require hosted
  Nginx and CodeQL evidence before review and merge.

## 2026-06-25

- Required an explicit, case-insensitive `Connection: upgrade` token before
  forwarding a WebSocket `Upgrade` request to Tornado.
- Added hostile checker mutations and live Nginx proxy coverage for missing,
  unrelated, mixed-token, and case-insensitive connection intent.

## 2026-06-21

- Rejected command-line and environment-preferred `MAKEFILE_LIST` metadata
  before verification recipes can be redirected outside the checkout.
- Added root-policy regressions to the normal test target.
- Preserved absolute Makefile paths containing whitespace and shell quoting
  characters without allowing checkout names to trigger command substitution.

## 2026-06-19

- Replaced client-selected `X-Forwarded-Port` with the direct listener port.
- Restricted upstream Upgrade forwarding to case-insensitive WebSocket tokens.
- Added live Nginx reverse-proxy tests and hostile static-checker mutations.
- Integrated repository ownership and setup/loopback guidance from the overlapping CI root.

## 2026-06-16

- Added WebSocket upgrade proxying for mixed Tornado HTTP and WebSocket traffic.

## 2026-06-15

- Added a Forwarded Host trust boundary so upstream host identity comes from
  the configured server name instead of client-selected Host metadata.
- Added a Forwarded-For trust boundary so the Tornado sample overwrites
  untrusted client chains with the direct peer address.
- Added Forwarded header suppression so standardized client-selected forwarding
  metadata cannot bypass the direct-edge proxy policy.
- Added Proxy request header suppression before the Tornado upstream boundary.

## 2026-06-13

- Made every dependency-free Make alias resolve the static checker from the
  checkout when the Makefile is invoked by absolute path.
- Added per-file purpose and production adaptation guidance for both sample
  configurations, including deployment-host `nginx -t` boundaries.

## 2026-06-12

- Disabled persisted checkout credentials and enforced the sole pinned
  credential-free workflow boundary.

## 2026-06-10

- Added 30-second upstream I/O timeouts for Tornado proxy reads and sends.
- Added a five-second upstream connect timeout to bound failed Tornado backend
  connection attempts while preserving the existing response read window.
- Added pinned, read-only Python 3.12 hosted validation for the static Nginx
  configuration and security baseline.
- Added an `X-Forwarded-Host` proxy header sourced from `$host` so Tornado
  upstreams receive normalized host metadata.

## 2026-06-08

- Added `make check` static verification for the sample Nginx configs.
- Lowered the PHP sample error log level from `debug` to `warn`.
- Disabled `server_tokens` in both samples.
- Normalized the Tornado proxy host header and added `X-Forwarded-For` and `X-Forwarded-Proto`.
- Hid upstream `Server` response headers in the Tornado proxy example.
- Added explicit `client_max_body_size` placeholders to both samples.
- Added `X-Content-Type-Options: nosniff` headers to both samples.
- Added `X-Frame-Options: SAMEORIGIN` headers to both samples.
- Added `Referrer-Policy: strict-origin-when-cross-origin` headers to both
  samples.
- Added `make lint`, `make test`, and `make build` aliases so the standard
  gate commands run the same SDK-free static baseline as `make check`.
- Added `try_files $uri =404` to the Tornado static location.
- Added a placeholder `server_name` and notes for Linux-specific `epoll` and deployment-specific include paths.
- Limited the PHP sample `sites-enabled` include to `sites-enabled/*.conf`.
- Replaced the Tornado static root with a neutral placeholder path.
- Added local ignore rules for environment files, logs, pid files, and test prefixes.
