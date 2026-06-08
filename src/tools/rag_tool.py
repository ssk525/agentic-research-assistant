from typing import List

from langchain_core.tools import tool
from langchain_cohere import CohereRerank

from src.config import settings
from src.agents.state import Evidence
from src.rag.retriever import get_vectorstore


from functools import lru_cache


@lru_cache(maxsize=1)
def _reranker() -> CohereRerank:
	return CohereRerank(
		model="rerank-english-v3.0",
		cohere_api_key=settings.cohere_api_key,
		top_n=4,
	)


@tool
def rag_search(query: str) -> List[dict]:
	"""Search the indexed corpus for relevant passages.
	Returns up to 4 reranked chunks with source metadata."""
	candidates = get_vectorstore().similarity_search(query, k=20)
	if not candidates:
		return []
	reranked = _reranker().compress_documents(documents=candidates, query=query)
	return [
		Evidence(
			source=doc.metadata.get("source", "unknown"),
			content=doc.page_content,
		).model_dump()
		for doc in reranked
	]
