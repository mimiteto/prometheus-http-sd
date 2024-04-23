TEST_CASE ?=
APP_NAME := prom-http-sd
APP_NAME_UNDERSCORE := prom_http_sd
red = \033[31m
color_reset = \033[0m
SHELL := /bin/bash
OS := $(shell uname -s)
TEST_TRESHOLD := 95
CI ?= false
NEW_PROJECT_NAME ?=

ifeq ($(CI),true)
	OPEN := echo
else ifeq ($(OS),Linux)
	OPEN := xdg-open
else ifeq ($(OS),Darwin)
	OPEN := open
else ifeq ($(OS),Windows_NT)
	OPEN := start
else
	OPEN := echo
endif

.PHONY: init
init:
	@echo "Initializing project..."
	@echo "Renaming project..."
	@bash hacks/rename-project.sh "$(NEW_PROJECT_NAME)"
	@echo "Creating virtual environment..."
	@make venv
	@echo "Installing dependencies..."
	@make venv-update
	@echo "Project initialized!"

.PHONY: venv
venv: venv-build venv-update # env-build

.PHONY: venv-build
venv-build:
	python3 -m venv .venv

.PHONY: venv-destroy
venv-destroy:
	deactivate || true
	rm -rf .venv

.PHONY: ensure-venv
ensure-venv:
	@if [ -z "$$VIRTUAL_ENV" ]; then \
		echo "$(red)Activate yout venv with:$(color_reset) source .venv/bin/activate"; \
		exit 1; \
	fi

.PHONY: venv-update
venv-update:
	source .venv/bin/activate && pip install -r requirements.txt -r resources/dev-requirements.txt --upgrade

.PHONY: lint
lint: ensure-venv lint-python lint-helm
	@flake8 --exclude=.venv,dist,docs,resources --ignore=E501

.PHONY: lint-python
lint-python: ensure-venv
	flake8 --exclude=htmlcov,.venv,dist,docs,resources .
	find . -name "*.py" -not -path "./.venv/*" | xargs pylint
	radon cc . --min B -j -s | jq .
	radon mi . --min B --max F

.PHONY: lint-helm
lint-helm:
	@helm lint deploy/prom-http-sd
	@helm template deploy/prom-http-sd

.PHONY: qtest
qtest: ensure-venv
	rm -rf htmlcov
	pytest --cov=$(APP_NAME_UNDERSCORE) --cov=tests --cov-report=html:htmlcov tests/
	@$(OPEN) htmlcov/index.html

.PHONY: build-py
build-py: ensure-venv
	@hatch build

.PHONY: build-docker
build-docker:
	@docker build -t $(APP_NAME):latest .

.PHONY: build
build: build-py build-docker

.PHONY: test
test: lint qtest

.PHONY: env-build
env-build:
	@bash hacks/env-build.sh

.PHONY: run
run: ensure-venv
	@touch $(CONF_FILE)
	@python3 -m $(APP_NAME) $(CONF_FILE)

.PHONY: prepare-pr
prepare-pr: test
	@bash hacks/bump-version.sh
