.PHONY: install download ingest seed run eval test docker-up

install:
	pip install -r requirements.txt

download:
	python scripts/download_corpus.py

ingest:
	python -m src.rag.ingest

seed:
	python -m src.db.seed

run:
	streamlit run src/app.py

eval:
	PYTHONPATH=. python evals/run_eval.py

test:
	pytest

docker-up:
	docker compose up --build
