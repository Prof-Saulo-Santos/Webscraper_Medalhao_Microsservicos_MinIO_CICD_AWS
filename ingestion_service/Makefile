.PHONY: install test format lint run clean

install:
	poetry install

test:
	poetry run pytest tests/ -v

format:
	poetry run ruff check --fix .
	poetry run black .

lint:
	poetry run ruff check . 
	poetry run black --check .

run:
	docker compose up --build -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

bump-patch:
	poetry run bump2version patch --verbose

bump-minor:
	poetry run bump2version minor --verbose

bump-major:
	poetry run bump2version major --verbose
