#* Variables
SHELL := bash
PYTHON := python
PYTHONPATH := `pwd`
ENV_NAME=egaznepy_dev
CONDA=mamba

#* Docker variables
IMAGE := egaznepy
VERSION := latest

#* Installation
.PHONY: install
install: $(ENV_NAME) ## Install the conda env

uninstall:
	rm -rf $(ENV_NAME)

.PHONY: pre-commit-install
pre-commit-install:
	pre-commit install

#* Formatters
.PHONY: codestyle
codestyle:
	pyupgrade --exit-zero-even-if-changed --py39-plus **/*.py
	isort --settings-path pyproject.toml ./
	black --config pyproject.toml ./

.PHONY: formatting
formatting: codestyle

#* Linting
.PHONY: test
test:
	PYTHONPATH=$(PYTHONPATH) pytest -c pyproject.toml --cov-report=html --cov=egaznepy tests/
	coverage-badge -o assets/images/coverage.svg -f

.PHONY: check-codestyle
check-codestyle:
	isort --diff --check-only --settings-path pyproject.toml ./
	black --diff --check --config pyproject.toml ./
	darglint --verbosity 2 --indentation 4 egaznepy tests

.PHONY: mypy
mypy:
	mypy --config-file pyproject.toml ./

.PHONY: check-safety
check-safety:
	safety check --full-report
	bandit -ll --recursive egaznepy tests

.PHONY: lint
lint: test check-codestyle mypy check-safety

# Conda env
$(ENV_NAME): environment.yaml
	@$(CONDA) env create -f environment.yaml -p ./$@ || (echo Probably already installed, trying update && $(CONDA) env update -f environment.yaml -p ./$@)
	@conda config --set env_prompt '($$(basename {default_env})) '
	@(cat .gitignore | grep -q $(ENV_NAME)) || echo $(ENV_NAME) >> .gitignore

#* Docker
# Example: make docker-build VERSION=latest
# Example: make docker-build IMAGE=some_name VERSION=0.1.0
.PHONY: docker-build
docker-build:
	@echo Building docker $(IMAGE):$(VERSION) ...
	docker build \
		-t $(IMAGE):$(VERSION) . \
		-f ./docker/Dockerfile --no-cache

# Example: make docker-remove VERSION=latest
# Example: make docker-remove IMAGE=some_name VERSION=0.1.0
.PHONY: docker-remove
docker-remove:
	@echo Removing docker $(IMAGE):$(VERSION) ...
	docker rmi -f $(IMAGE):$(VERSION)

#* Cleaning
.PHONY: pycache-remove
pycache-remove:
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

.PHONY: dsstore-remove
dsstore-remove:
	find . | grep -E ".DS_Store" | xargs rm -rf

.PHONY: mypycache-remove
mypycache-remove:
	find . | grep -E ".mypy_cache" | xargs rm -rf

.PHONY: ipynbcheckpoints-remove
ipynbcheckpoints-remove:
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

.PHONY: pytestcache-remove
pytestcache-remove:
	find . | grep -E ".pytest_cache" | xargs rm -rf

.PHONY: build-remove
build-remove:
	rm -rf build/

.PHONY: cleanup
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove

help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)
