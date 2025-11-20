# Workspaces3 Makefile

.PHONY: check test install clean

check: ## Format, lint, and type-check code
	@echo "Formatting code with ruff..."
	@uv run ruff format .
	@echo "Linting code with ruff..."
	@uv run ruff check . --fix
	@echo "Type-checking code with pyright..."
	@uv run pyright
	@echo "All checks passed!"

test: ## Run all tests
	@echo "Running tests..."
	@uv run pytest

install: ## Install dependencies
	@echo "Installing dependencies..."
	@uv sync --group dev
	@uv pip install -e .
	@echo "✅ Dependencies installed!"

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	@rm -rf .venv
	@rm -rf build dist *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Cleaned!"
