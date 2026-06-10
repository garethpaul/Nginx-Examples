# Security Policy

## Supported Versions

The supported security scope for `Nginx-Examples` is the current default branch, `master`. Older commits, tags, branches, forks, demos, and generated artifacts are not actively supported unless the repository explicitly marks them as maintained.

Project summary: Nginx Examples

## Reporting a Vulnerability

Please report suspected vulnerabilities through GitHub's private vulnerability reporting or by opening a draft GitHub Security Advisory for `garethpaul/Nginx-Examples` when that option is available. If GitHub does not show a private reporting option for this repository, contact the repository owner through GitHub and avoid posting exploit details publicly until the issue can be assessed.

Do not open a public issue that includes exploit code, secrets, personal data, or detailed reproduction steps for an unpatched vulnerability.

## What to Include

Helpful reports include:

- the affected file, endpoint, permission, dependency, or workflow
- a concise impact statement explaining what an attacker could do
- reproduction steps using test data and accounts you control
- the branch, commit SHA, platform version, device, runtime, or dependency versions used
- logs, screenshots, or proof-of-concept snippets that demonstrate impact without exposing private data

## Project Security Posture

- This repository appears to be a web server configuration sample. The active security scope is the code and documentation on the default branch.
- The checked-in files are sample-only Nginx configs. They must be adapted and verified with `nginx -t` before use in a live deployment.
- Both examples should keep `server_tokens off` so Nginx version disclosure is not enabled by default.
- Both examples should keep an explicit `client_max_body_size` placeholder so
  copied configs do not inherit an unintended upload/request-body policy.
- PHP sample includes should stay limited to `sites-enabled/*.conf` so unrelated files are not loaded as config by default.
- Proxy examples should keep `proxy_hide_header Server` so upstream framework or app server versions are not exposed by default.
- Proxy examples should forward `X-Forwarded-Host` from Nginx `$host` so
  upstream apps receive a normalized host value instead of raw client
  `$http_host`.
- The upstream connect timeout should bound failed loopback backend connection
  attempts; deployments should review the five-second sample value.
- Static file locations should keep `try_files $uri =404` so missing files fail
  closed instead of falling through unexpectedly.
- Examples should keep `X-Content-Type-Options: nosniff` so copied configs do
  not encourage browser MIME sniffing by default.
- Examples should keep `X-Frame-Options: SAMEORIGIN` so copied configs include
  a basic clickjacking guard by default.
- Examples should keep `Referrer-Policy: strict-origin-when-cross-origin` so
  copied configs include a basic referrer-leakage guard by default.
- Review found network clients, sockets, web APIs, proxy headers, or service endpoints; changes in those areas should receive security-focused review before merge.
- Review found file, document, data, or media parsing flows; changes in those areas should receive security-focused review before merge.
- Review found infrastructure, deployment, proxy, or cloud configuration; changes in those areas should receive security-focused review before merge.
- No primary dependency manifest was detected in the repository root. If dependencies are added later, include a manifest and prefer reproducible installation instructions.

## Service and API Notes

For web services, APIs, sockets, or scraping workflows, prioritize reports involving authentication bypass, authorization errors, injection, server-side request forgery, unsafe deserialization, credential leakage, data exposure, or denial-of-service conditions. Use test accounts and minimal proof-of-concept traffic only.

For these Nginx examples, also prioritize reports involving unsafe proxy header
handling, especially raw host forwarding, untrusted upstreams, path traversal
through static roots, accidental debug logging, certificate path exposure, or
private infrastructure details.

## Dependency and Supply Chain Security

Dependency updates should come from trusted package managers and should keep lockfiles in sync when lockfiles exist. Do not commit credentials, private keys, tokens, generated secrets, or machine-local configuration. If a vulnerability depends on a compromised package, typosquatting risk, insecure transitive dependency, or unsafe build step, include the package name, affected version, and the path through which it is used.

Run `make lint`, `make test`, `make build`, and `make check` before publishing
config changes, then run `nginx -t` with locally adjusted paths on a system
that has Nginx installed.

The pinned Linux workflow runs only the static configuration/security baseline;
it does not replace deployment-host `nginx -t` with adapted paths and modules.

## Safe Research Guidelines

Good-faith research is welcome when it stays within these boundaries:

- use only accounts, devices, data, and infrastructure that you own or have explicit permission to test
- avoid destructive actions, persistence, spam, phishing, social engineering, or denial-of-service testing
- minimize access to personal data and stop testing immediately if private data is exposed
- do not exfiltrate secrets or third-party data; report the minimum evidence needed to verify impact
- keep vulnerability details confidential until the maintainer has assessed the report

## Maintainer Response

The maintainer will review complete reports as availability allows, prioritize issues by exploitability and impact, and coordinate a fix or mitigation when the affected code is still maintained. For sample, archived, or educational repositories, the likely remediation may be documentation, dependency updates, or clearly marking unsupported code rather than a production-style patch release.
