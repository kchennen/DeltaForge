.PHONY: install dev lint format typecheck test test-verbose ci clean

install:
	uv sync --all-packages

dev: install
	uv run python main.py

serve: install
	uv run gunicorn -c gunicorn.conf.py "app.web.app:server"

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check . --fix

typecheck:
	uv run mypy apps/

test:
	uv run pytest tests/ -v

test-verbose:
	uv run pytest tests/ -v --tb=long

ci: lint typecheck test

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
