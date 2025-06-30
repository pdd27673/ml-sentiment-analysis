.PHONY: venv install run test clean

venv:
	python -m venv venv

install: venv
	./venv/bin/pip install -r requirements.txt

run:
	./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	./venv/bin/pytest

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf venv