from functools import lru_cache

from langchain_core.tools import tool
from sqlalchemy import create_engine, text

from src.config import settings

ALLOWED_TABLES = {"facts"}


@lru_cache(maxsize=1)
def _engine():
	return create_engine(settings.database_url)


@tool
def sql_query(sql: str) -> list:
	"""Run a read-only SQL query against the `facts` table.
	Schema: facts(id INT, entity TEXT, attribute TEXT, value TEXT, source TEXT,
	updated_at TIMESTAMP). Only SELECT statements over the `facts` table are allowed."""
	sql_lower = sql.strip().lower()
	if not sql_lower.startswith("select"):
		return [{"error": "Only SELECT queries allowed"}]
	if not any(t in sql_lower for t in ALLOWED_TABLES):
		return [{"error": "Query must target the facts table"}]
	with _engine().connect() as conn:
		rows = conn.execute(text(sql)).mappings().all()
		return [dict(r) for r in rows]
