.PHONY: dev install lint format test clean

install:
	pip install -e ".[dev]"

dev:
	python -m pytest -xvs

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

test:
	pytest tests/ -v --cov=src

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
