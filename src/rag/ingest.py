from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_chroma import Chroma

from src.config import settings
from src.rag.chunker import get_splitter
from src.rag.retriever import get_embeddings


def ingest(corpus_dir: str = "data/corpus") -> int:
	docs = []
	for path in Path(corpus_dir).rglob("*"):
		if path.suffix.lower() == ".pdf":
			loader = PyPDFLoader(str(path))
		elif path.suffix.lower() in {".txt", ".md"}:
			loader = TextLoader(str(path))
		else:
			continue
		for d in loader.load():
			d.metadata["source"] = path.name
			docs.append(d)

	if not docs:
		print(f"No documents found in {corpus_dir}. Add .pdf/.md/.txt files first.")
		return 0

	chunks = get_splitter().split_documents(docs)
	print(f"Ingesting {len(chunks)} chunks from {len(docs)} documents...")

	Chroma.from_documents(
		chunks,
		get_embeddings(),
		persist_directory=settings.chroma_persist_dir,
	)
	print("Ingestion complete.")
	return len(chunks)


if __name__ == "__main__":
	ingest()
