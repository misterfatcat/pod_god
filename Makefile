.PHONY: install dev test

install:
	uv sync
	cd frontend && npm install

dev:
	uv run uvicorn backend.main:app --reload --port 8000 &
	cd frontend && npm run dev

test:
	uv run pytest backend/tests/ -v
	cd frontend && npm run test -- --run
