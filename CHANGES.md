# Changes

## 2026-06-10

- Clarified setup guidance and loopback-only upstream placeholders so the
  checked-in configs are not treated as direct production installs or public
  HTTP upstream integrations.
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
