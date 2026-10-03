PYTHON ?= python
.PHONY: all build test test-full verify status demo
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
demo: build
	$(PYTHON) -m ops.validate
