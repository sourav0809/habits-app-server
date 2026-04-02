.PHONY: dev

dev:
	./venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

install:
	python3 -m venv venv
	./venv/bin/pip install -e .
