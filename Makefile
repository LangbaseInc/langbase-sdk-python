.PHONY: clean clean-build clean-pyc help test lint format build
.DEFAULT_GOAL := help

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: clean-build clean-pyc ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

lint: ## check style with flake8
	flake8 langbase tests examples

format: ## format code with black and isort
	black langbase tests examples
	isort langbase tests examples

test: ## run tests
	pytest

test-cov: ## run tests with coverage report
	pytest --cov=langbase --cov-report=term --cov-report=html

venv: ## create virtual environment
	python -m venv venv
	@echo "Run 'source venv/bin/activate' to activate the virtual environment"

dev-install: ## install the package in development mode
	pip install -e ".[dev]"

build: clean ## build the package
	python -m build

publish-test: build ## publish package to TestPyPI
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish: build ## publish package to PyPI
	twine upload dist/*

install-test: ## install package from TestPyPI
	pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple langbase

examples: ## run examples
	@echo "Running examples..."
	@for example in $(shell find examples -name "*.py" | sort); do \
		echo "\nRunning $${example}:"; \
		python $${example}; \
	done

docs: ## generate Sphinx documentation
	sphinx-apidoc -o docs/source langbase
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
