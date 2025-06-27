# Makefile for easy development workflows.
# GitHub Actions call uv directly.

# .DEFAULT_GOAL is the target that will be executed when `make` is run without any arguments.
.DEFAULT_GOAL := default

# A phony target is a target that is not a file. It is used to define commands that should always be executed, regardless of whether a file with the same name exists.
# This is useful for commands like `make clean`, `make install`, etc., which do not produce an output file.
.PHONY: 

default: install check

install:
	uv sync

build:
	uv build

dev-setup: install
	uv sync --all-extras --dev
	uv pip install -e .
	@echo "Development environment ready!"

lint:
	uv run devtools/lint.py

check:
	uv run ruff check src/
	uv run ruff format src/ --check
	uv run ty check src/

test:
	uv run pytest

upgrade:
	uv sync --upgrade

clean:
	-rm -rf dist/
	-rm -rf */*.egg-info/
	-rm -rf .pytest_cache
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +
	-rm -rf .ruff_cache/
