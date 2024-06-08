run:
	uvicorn src.main:app --port 8000 --reload

run_trip_tip_backend_in_container:
	docker compose build
	docker compose up --abort-on-container-exit && docker compose rm -fsv

lint:
	poetry run ruff format .
	poetry run ruff check . --fix
	git ls-files -m | xargs git add
	poetry run ruff check .

install_dependents:
	poetry install
	poetry shell
	poetry run pre-commit install

# Run pytest with correct environment, otherwise tests will fail:
test:
	MODE=TEST poetry run pytest

# Alembic block:
# To create a new migration, run the following command:
makemigrations:
	poetry run alembic revision --autogenerate -m `date +%Y%m%d%H%M%S`
# To apply the migration, run the following command:
migrate:
	poetry run alembic upgrade head
# To revert last migration, run the following command:
revert_migration:
	poetry run alembic downgrade -1
