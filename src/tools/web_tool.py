from functools import lru_cache

from langchain_core.tools import tool
from tavily import TavilyClient

from src.config import settings


@lru_cache(maxsize=1)
def _client() -> TavilyClient:
	return TavilyClient(api_key=settings.tavily_api_key)


@tool
def web_search(query: str) -> list:
	"""Search the public web for recent information.
	Returns up to 5 results with URL, title, and snippet."""
	resp = _client().search(query=query, max_results=5, search_depth="basic")
	return [
		{"url": r["url"], "title": r["title"], "content": r["content"]}
		for r in resp.get("results", [])
	]
