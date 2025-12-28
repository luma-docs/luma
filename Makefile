init:
	poetry install
	poetry run pre-commit install

lint:
	poetry run ruff format --check src
	poetry run ruff check src

format:
	poetry run ruff format src

test:
	poetry run pytest tests

release:
	poetry build
	poetry publish

.PHONY: init lint format test
