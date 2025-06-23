.PHONY: help build test lint format clean start stop restart logs

# Colors
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=20

## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST) | sort -u

## Build all services
build:
	@echo "${GREEN}Building all services...${RESET}"
	docker-compose build

## Start all services
dev:
	@echo "${GREEN}Starting all services in development mode...${RESET}"
	docker-compose up -d

## Stop all services
stop:
	@echo "${GREEN}Stopping all services...${RESET}"
	docker-compose down

## Restart all services
restart: stop dev

## View logs
logs:
	docker-compose logs -f

## Run tests
test:
	@echo "${GREEN}Running tests...${RESET}"
	docker-compose run --rm printers-service pytest /app/tests -v

test-monitoring:
	@echo "${GREEN}Running monitoring service tests...${RESET}"
	docker-compose run --rm monitoring-service pytest /app/tests -v

## Run linter
lint:
	@echo "${GREEN}Running linter...${RESET}"
	docker-compose run --rm printers-service flake8 /app

dev-printers:
	@echo "${GREEN}Starting printers service in development mode...${RESET}"
	docker-compose up -d postgres
	cd services/printers-service && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

## Format code
format:
	@echo "${GREEN}Formatting code...${RESET}"
	docker-compose run --rm printers-service black /app

## Clean up
clean:
	@echo "${GREEN}Cleaning up...${RESET}"
	docker-compose down -v

db-shell:
	docker-compose exec postgres psql -U postgres -d printing_db

## Initialize Terraform
init-tf:
	@echo "${GREEN}Initializing Terraform...${RESET}"
	cd terraform && terraform init

## Apply Terraform configuration
apply-tf:
	@echo "${GREEN}Applying Terraform configuration...${RESET}"
	cd terraform && terraform apply -auto-approve

## Destroy Terraform resources
destroy-tf:
	@echo "${YELLOW}Destroying Terraform resources...${RESET}"
	cd terraform && terraform destroy -auto-approve

## Run integration tests
integration-test:
	@echo "${GREEN}Running integration tests...${RESET}"
	python scripts/test_services.py
