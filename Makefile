ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check lint static-check test verify

PYTHON ?= python3

check: verify

verify: static-check

lint test build: static-check

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-nginx-examples.py"
