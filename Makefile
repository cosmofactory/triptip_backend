run:
	uv run uvicorn src.main:app --reload --forwarded-allow-ips='*' --proxy-headers --host 0.0.0.0 --port 8000 --workers 4

run_trip_tip_backend_in_container:
	docker compose build
	docker compose up --abort-on-container-exit && docker compose rm -fsv

lint:
	uv run ruff format .
	uv run ruff check . --fix
	git ls-files -m | xargs git add
	uv run ruff check .

install_dependents:
	uv install
	uv shell
	uv run pre-commit install

# Run pytest with correct environment, otherwise tests will fail:
test:
	MODE=TEST SERVICE_NAME=pytest uv run pytest

# Alembic block:
# To create a new migration, run the following command:
makemigrations:
	uv run alembic revision --autogenerate
# To apply the migration, run the following command:
migrate:
	uv run alembic upgrade head
# To revert last migration, run the following command:
revert_migration:
	uv run alembic downgrade -1