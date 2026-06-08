from functools import lru_cache

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from src.config import settings


@lru_cache(maxsize=1)
def get_embeddings() -> OpenAIEmbeddings:
	return OpenAIEmbeddings(
		model="text-embedding-3-small",
		api_key=settings.openai_api_key,
	)


@lru_cache(maxsize=1)
def get_vectorstore() -> Chroma:
	return Chroma(
		persist_directory=settings.chroma_persist_dir,
		embedding_function=get_embeddings(),
	)
