.PHONY: dev test lint

dev:
	docker-compose up --build

test:
	pip install -e ".[dev]"
	pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

lint:
	ruff check app/ tests/
	ruff format app/ tests/ --check