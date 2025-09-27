
all: build

lint:
	poetry run ruff check .

test:
	poetry run pytest -s tests/

