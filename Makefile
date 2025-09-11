.PHONY: setup ingest api demo test lint fmt compose clean archive docker-build docker-push tag

# Create virtual environment and install dependencies
setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && pre-commit install

# Ingest data (synthetic or real)
ingest:
	. .venv/bin/activate && python scripts/ingest.py

# Run FastAPI server
api:
	. .venv/bin/activate && uvicorn app.api:app --reload --port $${PORT:-8000}

# Run Streamlit demo UI
demo:
	. .venv/bin/activate && streamlit run app/demo_ui.py

# Run tests
test:
	. .venv/bin/activate && pytest -q

# Lint code
lint:
	ruff app scripts tests

# Format code
fmt:
	ruff --fix app scripts tests && black app scripts tests

# Docker compose up
compose:
	docker compose up --build

# Build distribution archive
archive:
	mkdir -p dist && zip -r dist/crypto-rag-copilot-`git describe --tags --abbrev=0 --tags 2>/dev/null || echo 0.1.0`.zip . -x '*.venv*' -x 'index/*' -x 'data/processed/*' -x '__pycache__/*'

# Build docker image
docker-build:
	docker build -t crypto-rag-copilot:latest .

# Push docker image (requires IMAGE and RELEASE env)
docker-push:
	docker build -t $$IMAGE:$$RELEASE . && docker push $$IMAGE:$$RELEASE

# Tag release
tag:
	git tag -a v$${RELEASE} -m "release $${RELEASE}" && git push origin v$${RELEASE}

clean:
	rm -rf .venv dist
