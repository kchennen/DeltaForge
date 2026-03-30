# DeltaForge — Project management tasks
.PHONY: install dev lint format typecheck test test-verbose ci clean


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
UV         := uv
ENV_FILE   := $(wildcard .env)
UV_RUN     := $(UV) run $(if $(ENV_FILE),--env-file $(ENV_FILE))
PYTHON     := $(UV_RUN) python


# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------

## Show this help
help:
	@echo ""
	@echo "🧰 DeltaForge — Makefile targets"
	@echo "================================"
	@awk '/^## / {desc = substr($$0, 4)} \
		/^[a-zA-Z_-]+:/ && desc {gsub(/:.*/, "", $$1); printf "  \033[36m%-14s\033[0m %s\n", $$1, desc; desc=""}' \
		$(MAKEFILE_LIST)
	@echo ""


## Install production dependencies
install:
	$(UV) sync --all-packages

## Run the dev server
dev: install
	$(PYTHON) main.py

## Start app with Gunicorn (production)
run: install
	$(UV_RUN) gunicorn -c gunicorn.conf.py "app.web:server"

## Lint code with Ruff
lint:
	$(UV) run ruff check .

## Format code and fix lint issues
format:
	$(UV) run ruff format .
	$(UV) run ruff check . --fix

## Type-check with mypy
typecheck:
	$(UV) run mypy apps/

## Run tests
test:
	$(UV) run pytest tests/ -v

## Run tests with full tracebacks
test-verbose:
	$(UV) run pytest tests/ -v --tb=long

## Run lint, typecheck, and tests
ci: lint typecheck test

## Remove cache directories
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null; \
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
