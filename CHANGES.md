# Changes

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
