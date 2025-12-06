# Copyright 2025 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

-include ../../scripts/base_env.sh

# Define Variables
ifndef project
    override project = $(GCP_PROJECT)
endif

ifndef region
    override region = $(GCP_REGION)
endif


# Define Variables
VENV = venv
BUILD = build
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
RUFF = $(VENV)/bin/ruff
SPHINX = $(VENV)/bin/sphinx
COVERAGE = $(VENV)/bin/coverage


# Define Timestamped Files
VENV_TIMESTAMP = ${BUILD}/.make.venv.done
INSTALL_TIMESTAMP = ${BUILD}/.make.install.done


# Default target
.PHONY: all
all: help


# Create virtual environment
$(VENV_TIMESTAMP):
	@echo "🐍 Creating Python virtual environment for Phase..."
	python3 -m venv $(VENV)
	mkdir -p ${BUILD}
	${PIP} install --upgrade pip
	touch $(VENV_TIMESTAMP)

.PHONY: venv
venv: $(VENV_TIMESTAMP)


# Upgrade Dependencies
.PHONY: upgrade-pip
upgrade-pip: $(VENV_TIMESTAMP)
	${PIP} install --upgrade pip


# Install dependencies
$(INSTALL_TIMESTAMP): $(VENV_TIMESTAMP) pyproject.toml
	${PIP} install -e .
	touch $(INSTALL_TIMESTAMP)

.PHONY: install
install: $(INSTALL_TIMESTAMP)


# Install all dependencies
.PHONY: install-all
install-all: install


# Upgrade Dependencies
.PHONY: upgrade
upgrade: $(VENV_TIMESTAMP) upgrade-pip
	${PIP} install --upgrade -e .

# Clean Environment
.PHONY: clean
clean:
	rm -rf $(VENV) $(BUILD) $(INSTALL_TIMESTAMP) $(VENV_TIMESTAMP)
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name ".coverage" -exec rm -f {} +

# Help
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make docs                 - Create doc documentation"
	@echo "  make venv                 - Create virtual environment"
	@echo "  make install              - Install runtime dependencies"
	@echo "  make install-dev          - Install test and development dependencies"
	@echo "  make install-docs         - Install documentation dependencies"
	@echo "  make install-all          - Install all dependencies"
	@echo "  make run                  - Interactive - Run an ADK Agent local development test instance with all environment variables and secrets"
	@echo "  make run-adk-background   - Non-interactive - Start an ADK Agent local development test instance with all environment variables and secrets"
	@echo "  make stop-adk-background  - Non-interactive - Stop an ADK Agent local development test instance that's running in the background"
	@echo "  make deploy               - Deploy ADK Agent to Agent Engine"
	@echo "  make update-branch        - Refreshes remote Git branches into workspace"
	@echo "  make upgrade              - Install upgraded runtime dependencies"
	@echo "  make upgrade-pip          - Install upgraded runtime dependencies"
	@echo "  make tests                - Run tests"
	@echo "  make coverage             - Run tests and code coverage"
	@echo "  make lint                 - Run linting"
	@echo "  make format               - Run code formatting"
	@echo "  make get-sa               - Fetch the service account associated with the environment"
	@echo "  make add-license          - Applies the Google LLC Apache-2.0 license to all applicable files"
	@echo "  make readme-toc           - Output a generated TOC from the repository README.md"
	@echo "  make clean                - Clean environment"
	@echo "  make help                 - Show help"
