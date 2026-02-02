fmt:
	python -m ruff check --fix .
	python -m ruff format .

test:
	pytest -q

run:
	uvicorn app.main:app --reload
