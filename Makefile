.PHONY: check static-check

check: static-check

static-check:
	python3 scripts/check-nginx-examples.py
