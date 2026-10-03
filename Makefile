PYTHON ?= python
.PHONY: all build test test-full verify status demo audit
all: build
build:
	$(PYTHON) -m ops.build
test: build
	$(PYTHON) -m unittest discover -s tests -v
test-full: test
	$(PYTHON) -m ops.validate --full
verify: build
	$(PYTHON) -m ops.verify
status:
	$(PYTHON) -m ops.supervisor status
audit:
	$(PYTHON) -m ops.vault_report
demo: build
	$(PYTHON) -m ops.validate
