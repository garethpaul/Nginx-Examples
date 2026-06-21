ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(abspath $(dir $(lastword $(MAKEFILE_LIST))))

.PHONY: build check checker-test lint proxy-test root-test static-check test verify

PYTHON ?= python3

check: verify

verify: static-check test

lint build: static-check

test: checker-test proxy-test root-test

checker-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-check-nginx-examples.py"

proxy-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-nginx-proxy.py"

root-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/test-makefile-root.py"

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) "$(ROOT)/scripts/check-nginx-examples.py"
