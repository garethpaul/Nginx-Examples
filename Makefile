override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check checker-test lint proxy-test static-check test verify

PYTHON ?= python3

check: verify

verify: static-check test

lint build: static-check

test: checker-test proxy-test

checker-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-check-nginx-examples.py"

proxy-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-nginx-proxy.py"

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-nginx-examples.py"
