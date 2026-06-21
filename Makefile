ifneq ($(origin MAKEFILE_LIST),file)
$(error MAKEFILE_LIST must not be overridden)
endif
override ROOT := $(shell path='$(subst ','"'"',$(MAKEFILE_LIST))'; path=$$(printf '%s' "$$path" | /usr/bin/sed 's/^ //'); /usr/bin/dirname -- "$$path")
override SHELL_ROOT := $(subst ','"'"',$(ROOT))

.PHONY: build check checker-test lint proxy-test root-test static-check test verify

PYTHON ?= python3

check: verify

verify: static-check test

lint build: static-check

test: checker-test proxy-test root-test

checker-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/test-check-nginx-examples.py'

proxy-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/test-nginx-proxy.py'

root-test:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/test-makefile-root.py'

static-check:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) '$(SHELL_ROOT)/scripts/check-nginx-examples.py'
