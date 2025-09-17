# Makefile for AI Content Factory

# Variables
PYTHON = python
PIP = pip
DOCKER = docker
DOCKER_COMPOSE = docker-compose

# Install dependencies
install:
	$(PIP) install -r requirements.txt

# Install dependencies in development mode
install-dev:
	$(PIP) install -r requirements.txt
	$(PIP) install pytest black flake8 mypy

# Run the application
run:
	$(PYTHON) run.py

# Run the application with uvicorn
run-uvicorn:
	uvicorn app.main:app --reload

# Run tests
test:
	pytest tests/ -v

# Run tests with coverage
test-cov:
	pytest tests/ --cov=app --cov-report=html

# Format code with black
format:
	black .

# Check code style with flake8
lint:
	flake8 .

# Type check with mypy
type-check:
	mypy app/

# Run Celery worker
celery-worker:
	celery -A celery_worker.celery_app worker --loglevel=info

# Run Celery beat
celery-beat:
	celery -A celery_worker.celery_app beat --loglevel=info

# Build Docker images
docker-build:
	$(DOCKER_COMPOSE) build

# Start all services with Docker
docker-up:
	$(DOCKER_COMPOSE) up -d

# Stop all services with Docker
docker-down:
	$(DOCKER_COMPOSE) down

# View Docker logs
docker-logs:
	$(DOCKER_COMPOSE) logs -f

# Run database migrations
migrate:
	alembic upgrade head

# Create a new migration
migrate-create:
	alembic revision --autogenerate -m "$(message)"

# Help
help:
	@echo "Available commands:"
	@echo "  install        - Install dependencies"
	@echo "  install-dev    - Install dependencies for development"
	@echo "  run            - Run the application"
	@echo "  run-uvicorn    - Run the application with uvicorn"
	@echo "  test           - Run tests"
	@echo "  test-cov       - Run tests with coverage"
	@echo "  format         - Format code with black"
	@echo "  lint           - Check code style with flake8"
	@echo "  type-check     - Type check with mypy"
	@echo "  celery-worker  - Run Celery worker"
	@echo "  celery-beat    - Run Celery beat"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-up      - Start all services with Docker"
	@echo "  docker-down    - Stop all services with Docker"
	@echo "  docker-logs    - View Docker logs"
	@echo "  migrate        - Run database migrations"
	@echo "  migrate-create - Create a new migration"