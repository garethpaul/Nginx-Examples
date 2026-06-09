# Request Body Size Limit

status: completed

## Context

These Nginx files are sample-only configs that may be copied into new
deployments. Neither sample declared a request body limit, leaving copied
configs to inherit whatever default the target Nginx installation uses.

## Objectives

- Add an explicit `client_max_body_size` placeholder to both examples.
- Keep the value conservative and clearly sample-oriented.
- Document that deployments should adjust the limit deliberately.
- Extend the static checker so the request body size limit remains visible.

## Verification

- `python3 scripts/check-nginx-examples.py`
- `make check`
- `git diff --check`
