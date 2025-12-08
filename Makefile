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

-include scripts/base_env.sh

# Define Variables
ifndef project
    override project = $(PROJECT_ID)
endif

ifndef region
    override region = $(LOCATION)
endif


# Define Variables
VENV = venv
BUILD = build
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip

# Define Timestamped Files
VENV_TIMESTAMP = ${BUILD}/.make.venv.done
INSTALL_TIMESTAMP = ${BUILD}/.make.install.done
HYDRATE_TIMESTAMP = ${BUILD}/.make.hydrate.done


TERRAFORM_FILES := $(wildcard infra/*.tf)
INFRA_DIRS := $(shell find infra -type d)
INFRA_FILES := $(foreach dir,$(INFRA_DIRS),$(wildcard $(dir)/*.tf) $(wildcard $(dir)/*.sh))
INIT_TIMESTAMP := infra/.terraform.initialized
DEPLOY_TIMESTAMP := infra/.terraform.deployed

ASSET_DIRS := $(shell find assets -type d)
ASSETS_FILES := $(foreach dir,$(ASSET_DIRS),$(wildcard $(dir)/*.py) $(wildcard $(dir)/*.sh))

LABS := $(wildcard labs/*)


# Default target
.PHONY: all
all: help


# Check the Active GCloud Login
.PHONY: gcloud-check
gcloud-check:
	@echo -n "Active GCP Login: "
	@gcloud config list account --format "value(core.account)"
	@echo -n "Active GCP Project: "
	@gcloud config get-value project 2>&1 | grep -v 'Your active configuration is: '
	@echo -n "Active Service Account: "
	@curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email" -H "Metadata-Flavor: Google" && echo ""


# Login and Configure GCloud Project
.PHONY: login
login:
	gcloud auth login --update-adc


# Configure GCloud Project
.PHONY: set-project
set-project:
ifndef project
	$(error project is not set!)
endif
	gcloud config set project $(project)
	gcloud auth application-default set-quota-project $(project)


# Fetch the Metadata Service Account
.PHONY: get-sa
get-sa:
	@curl "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/email" -H "Metadata-Flavor: Google" && echo ""


# Update Remote Git Branches
.PHONY: update-branch
update-branch:
	git remote update origin --prune


# Initialize Terraform
$(INIT_TIMESTAMP): infra/*.tf
	terraform -chdir=infra init
	touch $(INIT_TIMESTAMP)

.PHONY: init
init: $(INIT_TIMESTAMP)


# Deploy Terraform infra
$(DEPLOY_TIMESTAMP): $(INIT_TIMESTAMP) $(INFRA_FILES)
ifndef project
	$(error project is not set!)
else
	echo -e "${BLUE}🚀 Deploying Vertex AI L400 Lab 2 Demo Cloud resources...${NC}"
	terraform -chdir=infra apply -var="project_id=$(project)"
	touch $(DEPLOY_TIMESTAMP)
endif

.PHONY: deploy
deploy: $(DEPLOY_TIMESTAMP)


# Describe Terraform Resources
.PHONY: graph
graph: 
ifndef project
	$(error project is not set!)
else
	terraform -chdir=infra plan -out .terraform.plan -var="project_id=$(project)"
	terraform -chdir=infra graph -plan=.terraform.plan | dot -Tpng > ./docs/terraform-graph.png
	terraform -chdir=infra graph -plan=.terraform.plan | dot -Tsvg > ./docs/terraform-graph.svg
endif
	
# Destroy Terraform infra
.PHONY: destroy
destroy: $(INIT_TIMESTAMP)
ifndef project
	$(error project is not set!)
else
	terraform -chdir=infra destroy -var="project_id=$(project)"
	make clean
endif


# Hydrate infra resources
.PHONY: hydrate
hydrate: $(HYDRATE_TIMESTAMP)

$(HYDRATE_TIMESTAMP): $(DEPLOY_TIMESTAMP) $(INSTALL_TIMESTAMP) $(ASSETS_FILES)
	scripts/run_hydrate_infra.sh
	touch $(HYDRATE_TIMESTAMP)


# Create virtual environment
$(VENV_TIMESTAMP):
	@echo "🐍 Creating Python virtual environment in $(VENV)..."
	python3 -m venv $(VENV)
	mkdir -p ${BUILD}
	${PIP} install --upgrade pip
	touch $(VENV_TIMESTAMP)

.PHONY: venv
venv: $(VENV_TIMESTAMP)


# Install dependencies
$(INSTALL_TIMESTAMP): $(VENV_TIMESTAMP) assets/pyproject.toml
	@echo "🐍 Upgrading Python Dependencies in $(VENV)..."
	${PIP} install -e assets
	touch $(INSTALL_TIMESTAMP)

.PHONY: install
install: $(INSTALL_TIMESTAMP)


# Run a phase demo
.PHONY: run
run: $(HYDRATE_TIMESTAMP)
ifndef lab
	$(error lab is not set! e.g., make run lab=phase1)
endif
	@echo "🚀 Starting Local Test Agent for Lab $(lab)"
	make -C labs/$(lab) run

# Run a phase test
.PHONY: test
test: $(HYDRATE_TIMESTAMP)
ifndef lab
	$(error lab is not set! e.g., make test lab=phase1)
endif
	@echo "🔍 Executing Unit Tests for Phase $(lab)"
	make -C labs/$(lab) test


# Run a command in each lab
.PHONY: batch-test
batch-test: $(HYDRATE_TIMESTAMP)
ifndef count
	$(error count is not set! e.g., make batch-test count=1)
endif
	@for lab in $(LABS); do \
		if [ -d "$$lab" ] && [ "$${lab##*/}" != "labs" ]; then \
			echo "🔍 Executing Unit Tests for $$lab"; \
			make -C $$lab test; \
		fi \
	done


# Generate a test summary report
.PHONY: test-summary
test-summary:
	@echo "📊 Generating test summary report..."
	@$(VENV)/bin/python scripts/generate_test_summary.py $(foreach lab,$(LABS),$(wildcard workspace/$(lab)/tests/latest-test-results.xml))
	@echo "✅ Report saved to ./workspace/LATEST_TEST_RESULTS.md"


# Clean the Environment
.PHONY: clean
clean:
ifndef lab
	@echo "🗑️  Executing Clean for ALL Lab Phases"
	rm -rf $(VENV) $(BUILD)
	find . -type d -name "build" -exec rm -rf {} +
#	find . -type d -name ".terraform" -exec rm -rf {} +
#	find . -name ".terraform.*" -exec rm -f {} +
#	find . -name "terraform.tfstate*" -exec rm -f {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name ".coverage" -exec rm -f {} +
else
	@echo "🗑️  Executing Clean for labs/$(lab)"
	make -C labs/$(lab) clean
endif


# Help
.PHONY: help
help:
	@echo "Usage:"
	@echo "  make init                     - Initialize Terraform"
	@echo "  make deploy                   - Deploy Terraform infra"
	@echo "  make destroy                  - Destroy Terraform infra"
	@echo "  make update-branch            - Refreshes remote Git branches into workspace"
	@echo "  make get-sa                   - Fetch the service account associated with the environment"
	@echo "  make gcloud-check             - Check the active GCloud login and project"
	@echo "  make login                    - Login to GCloud"
	@echo "  make set-project              - Configure GCloud project"
	@echo "  make graph                    - Update /docs/ PNG and SVG for Terraform resources"
	@echo "  make clean                    - Clean environment"
	@echo "  make help                     - Show help"
	@echo "  make venv                     - Create virtual environment"
	@echo "  make install                  - Install runtime dependencies"
	@echo "  make hydrate                  - Hydrate infrastructure resources"
	@echo "  make run lab=<lab>            - Run a lab demo (e.g., make run lab=phase1)"
	@echo "  make test lab=<lab>           - Run a lab test (e.g., make test lab=phase1)"
	@echo "  make batch-test count=<count> - Run a batch test for all labs (e.g., make batch-test count=10)"
