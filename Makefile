run_trip_tip_backend_locally:
	cp .env_sample .env
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