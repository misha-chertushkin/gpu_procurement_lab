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


# Upgrade Dependencies
.PHONY: upgrade
upgrade: $(VENV_TIMESTAMP) upgrade-pip
	${PIP} install --upgrade -e .


# Run and Test
.PHONY: run
run: $(INSTALL_TIMESTAMP)
	@./scripts/run.sh


.PHONY: test
test: $(INSTALL_TIMESTAMP)
	@./scripts/test.sh


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
	@echo "  make venv                 - Create virtual environment"
	@echo "  make install              - Install runtime dependencies"
	@echo "  make run                  - Run the demo in the foreground"
	@echo "  make test                 - Run the demo unit tests"
	@echo "  make upgrade              - Install upgraded runtime dependencies"
	@echo "  make upgrade-pip          - Install upgraded runtime dependencies"
	@echo "  make clean                - Clean environment"
	@echo "  make help                 - Show help"
