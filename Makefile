run_trip_tip_backend_locally:
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