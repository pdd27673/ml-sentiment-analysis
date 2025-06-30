.PHONY: venv install run test test-verbose test-coverage clean

venv:
	python -m venv venv

install: venv
	./venv/bin/pip install -r requirements.txt

run:
	./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	./venv/bin/pytest

test-verbose:
	./venv/bin/pytest -v

test-coverage:
	./venv/bin/pytest --cov=app --cov-report=html

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf venv
	rm -rf htmlcov
	rm -rf .pytest_cache