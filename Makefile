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
	pytest parser tests
.PHONY: test-python

typecheck: check-virtual-env
	mypy . --exclude venv
.PHONY: typecheck

requirements: check-virtual-env requirements.txt
	pip3 install -r requirements.txt

pre-commit: test
.PHONY: pre-commit