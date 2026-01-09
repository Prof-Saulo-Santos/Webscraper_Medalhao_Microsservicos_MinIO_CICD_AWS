.PHONY: install test format lint run run-local clean bump-minor

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
	# Roda via Docker Compose (Produção/Homologação)
	docker compose up --build -d

run-local:
	# Roda nativamente para desenvolvimento rápido
	poetry run streamlit run app/main.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

bump-minor:
	poetry run bump2version minor --verbose
