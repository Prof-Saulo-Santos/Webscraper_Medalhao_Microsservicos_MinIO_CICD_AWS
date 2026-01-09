.PHONY: install test format lint run clean bump-minor

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
	# Roda apenas o banco/infra se necessário, ou o serviço completo
	docker compose up --build -d

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

bump-minor:
	# Sobe versão 0.1.0 -> 0.2.0
	poetry run bump2version minor --verbose
