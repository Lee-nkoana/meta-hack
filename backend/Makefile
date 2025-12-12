# Backend Makefile

PYTHON := venv/bin/python
PIP := venv/bin/pip

.PHONY: help install run test test-ai test-auth test-records test-users demo seed seed-medications clean verify verify-ai build

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

demo: ## Run the interactive API demo script
	./scripts/run_demo.sh

demo-training: ## Run training data upload demo
	$(PYTHON) scripts/demo_training.py

batch-upload: ## Batch upload training images from folder
	@echo "Usage: make batch-upload FOLDER=/path/to/images"
	@echo "Example: make batch-upload FOLDER=./training_images TYPE=handwritten"
	$(PYTHON) scripts/batch_upload_training.py $(FOLDER) $(if $(TYPE),--type $(TYPE))

load-prescription-data: ## Load handwritten prescription training data
	$(PYTHON) scripts/load_prescription_training.py --split Training --limit 100

load-all-prescription-data: ## Load ALL prescription training data (Training, Testing, Validation)
	$(PYTHON) scripts/load_prescription_training.py --all

seed: ## Populate the database with test data
	$(PYTHON) scripts/seed_data.py

seed-medications: ## Populate medications table from JSON training data
	$(PYTHON) scripts/seed_medications.py

clean: ## Remove test data
	$(PYTHON) scripts/clean_data.py

verify: ## Run comprehensive system verification
	$(PYTHON) scripts/verify_all.py

verify-ai: ## Run AI service verification
	$(PYTHON) scripts/verify_ai.py

build: ## Build the Docker image
	docker build -t meta-hack-backend .
	