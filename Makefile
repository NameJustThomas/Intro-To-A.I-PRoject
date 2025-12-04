.PHONY: help build up down restart logs test lint format clean init-db import-data

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker containers
	cd infra && docker compose build

up: ## Start all services
	cd infra && docker compose up -d

down: ## Stop all services
	cd infra && docker compose down

restart: ## Restart all services
	cd infra && docker compose restart

logs: ## View logs from all services
	cd infra && docker compose logs -f

test: ## Run backend tests
	cd backend && pytest

lint: ## Run linters
	cd backend && black --check . && isort --check-only . && flake8 .

format: ## Format code
	cd backend && black . && isort .

init-db: ## Initialize database with migrations
	python scripts/init_db.py

import-data: ## Import sample data from CSV
	python scripts/import_sample_data.py

clean: ## Clean up Docker volumes and containers
	cd infra && docker compose down -v

setup: build up init-db import-data ## Full setup: build, start, init DB, import data

