# AGENTS.md

## Repository purpose

`garethpaul/Nginx-Examples` is a small set of sample Nginx configurations for PHP-style site includes and Tornado upstream proxying.

## Project structure

- `Makefile` - repository verification targets
- `scripts` - baseline checks and helper scripts
- `docs` - plans, notes, and generated README assets

## Development commands

- Install dependencies: no repository-specific install command is documented.
- Full baseline: `make check`
- Combined verification: `make verify`
- If a command above skips because a platform toolchain is missing, verify on a machine with that SDK before claiming platform behavior is tested.

## Coding conventions

- Language mix noted in the README: no dominant source language detected.

## Testing guidance

- No dedicated test files were detected; treat `make check` as the minimum baseline.
- Start with the narrowest relevant test or Make target, then run `make check` before handing off if the change is not documentation-only.
- Keep README verification notes in sync when commands, fixtures, or supported toolchains change.

## PR / change guidance

- Keep diffs focused on the requested repository and avoid unrelated modernization or formatting churn.
- Preserve public APIs, sample behavior, file formats, and documented environment variables unless the task explicitly changes them.
- Update tests, README notes, or docs/plans when behavior, security posture, or validation commands change.
- Call out skipped platform validation, legacy toolchain assumptions, and any risky files touched in the final summary.

## Safety and gotchas

- No required secret or credential file was identified in the repository scan.
- Keep real domains, private upstreams, certificate paths, environment files, generated logs, and pid files out of git.
- Both examples disable `server_tokens` with `server_tokens off`.
- The Tornado proxy example also hides upstream `Server` response headers with `proxy_hide_header Server`.
- The Tornado static location should keep `try_files $uri =404;` before use in live deployments.
- Both examples cap request bodies with `client_max_body_size` as a sample default.

## Agent workflow

1. Inspect the README, Makefile, manifests, and the files directly related to the request.
2. Make the smallest source or docs change that satisfies the task; avoid generated, vendored, or local-environment files unless required.
3. Run the narrowest useful validation first, then `make check` or the documented package/platform gate when available.
4. If a required SDK, service credential, or external runtime is unavailable, record the skipped command and why.
5. Summarize changed files, commands run, and remaining risks or follow-up validation.
