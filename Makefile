virtualenvironment:
	python3.12 -m venv venv
.PHONY: virtualenvironment

check-virtual-env:
	@# Test if the variable is set
	@if [ -z "${VIRTUAL_ENV}" ]; then                                               \
  		echo "Need to activate virtual environment: source ./venv/bin/activate";    \
  		false;       																\
  	fi

install: requirements install-githooks
.PHONY: install

install-githooks: check-virtual-env
	pre-commit install
.PHONY: install-githooks

test: check-virtual-env typecheck test-python
.PHONY: test

test-python: check-virtual-env
	pytest tests
.PHONY: test-python

typecheck: check-virtual-env
	$(eval FILES := $(shell find "." -type f -name '*.py' -not -path './venv/*' -prune))
	@if [ -z "${FILES}" ]; then echo "nothing to do"; fi
	mypy ${FILES}
.PHONY: typecheck

requirements: check-virtual-env requirements.txt
	pip3 install -r requirements.txt

pre-commit: test
.PHONY: pre-commit