# Backend Makefile

PYTHON := venv/bin/python
PIP := venv/bin/pip

.PHONY: help install run test test-ai test-auth test-records test-users demo seed clean verify verify-ai build

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install dependencies
	$(PIP) install -r requirements.txt

run: ## Start the Flask backend server
	./scripts/start_backend.sh

test: ## Run all tests
	./scripts/run_tests.sh $(ARGS)

test-ai: ## Run AI service tests
	./scripts/run_tests.sh tests/test_ai.py

test-auth: ## Run authentication tests
	./scripts/run_tests.sh tests/test_auth.py

test-records: ## Run medical records tests
	./scripts/run_tests.sh tests/test_medical_records.py

test-users: ## Run user profile tests
	./scripts/run_tests.sh tests/test_users.py

demo: ## Run the interactive demo script
	./scripts/run_demo.sh

seed: ## Populate the database with test data
	$(PYTHON) scripts/seed_data.py

clean: ## Remove test data
	$(PYTHON) scripts/clean_data.py

verify: ## Run comprehensive system verification
	$(PYTHON) scripts/verify_all.py

verify-ai: ## Run AI service verification
	$(PYTHON) scripts/verify_ai.py

build: ## Build the Docker image
	docker build -t meta-hack-backend .
	