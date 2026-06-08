from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.config import settings
from src.agents.state import AgentState, Evidence
from src.tools.rag_tool import rag_search
from src.tools.sql_tool import sql_query
from src.tools.web_tool import web_search

_TOOL_MAP = {
	"rag_search": rag_search,
	"sql_query": sql_query,
	"web_search": web_search,
}

FACTS_SCHEMA = (
	"facts(id INT, entity TEXT, attribute TEXT, value TEXT, "
	"source TEXT, updated_at TIMESTAMP)"
)

SQL_GEN_SYSTEM = f"""You translate a natural-language question into a single
read-only SQL SELECT statement against this table:
{FACTS_SCHEMA}
Rules:
- Only query the `facts` table.
- Return ONLY the SQL statement. No markdown fences, no explanation.
"""

WORKER_SYSTEM = """You are a research worker.
Given a question and a body of evidence, write a concise, grounded answer.
RULES:
- Use ONLY the evidence provided.
- Cite every claim inline as [source_name] or [url].
- If evidence is insufficient, say so explicitly."""


@lru_cache(maxsize=1)
def _worker_llm():
	return ChatOpenAI(
		model=settings.llm_model,
		api_key=settings.openai_api_key,
		temperature=0.2,
	)


@lru_cache(maxsize=1)
def _sql_llm():
	return ChatOpenAI(
		model=settings.llm_model,
		api_key=settings.openai_api_key,
		temperature=0,
	)


def _to_sql(question: str) -> str:
	"""Translate a natural-language sub-question into a SELECT statement."""
	raw = _sql_llm().invoke(
		[
			{"role": "system", "content": SQL_GEN_SYSTEM},
			{"role": "user", "content": question},
		]
	).content.strip()
	if raw.startswith("```"):
		raw = raw.strip("`")
		if "\n" in raw:
			_, raw = raw.split("\n", 1)
	return raw.strip().rstrip(";")


def _run_tool(sub_question) -> list:
	tool = _TOOL_MAP.get(sub_question.tool)
	if not tool:
		return []
	if sub_question.tool == "sql_query":
		sql = _to_sql(sub_question.question)
		return tool.invoke({"sql": sql}) or []
	return tool.invoke({"query": sub_question.question}) or []


def worker_node(state: AgentState) -> dict:
	new_evidence = []
	for sq in state["plan"].sub_questions:
		for r in _run_tool(sq):
			if not isinstance(r, dict):
				r = {"content": str(r)}
			new_evidence.append(
				Evidence(
					source=r.get("source") or r.get("url") or sq.tool,
					content=r.get("content") or str(r),
					url=r.get("url"),
				)
			)

	all_ev = state.get("evidence", []) + new_evidence
	evidence_block = "\n\n".join(f"[{e.source}] {e.content}" for e in all_ev[:30])
	prior = state.get("critic_report")
	critic_fb = prior.feedback if prior else ""

	draft = (
		_worker_llm()
		.invoke(
			[
				{"role": "system", "content": WORKER_SYSTEM},
				{
					"role": "user",
					"content": (
						f"Question: {state['question']}\n\n"
						f"Evidence:\n{evidence_block}\n\n"
						f"Prior critique (if any): {critic_fb}"
					),
				},
			]
		)
		.content
	)

	return {
		"evidence": new_evidence,
		"draft": draft,
		"iterations": state.get("iterations", 0) + 1,
	}
