from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.config import settings
from src.agents.state import AgentState, Plan


@lru_cache(maxsize=1)
def _planner_llm():
	llm = ChatOpenAI(
		model=settings.llm_model,
		api_key=settings.openai_api_key,
		temperature=0,
	)
	return llm.with_structured_output(Plan)


PLANNER_SYSTEM = """You are a research planner.
Given the user's question, break it into 2-4 focused sub-questions.
For each, assign the BEST tool:
- rag_search: for domain-specific knowledge already in our indexed corpus
- sql_query: for structured facts (entities, attributes, values)
- web_search: for recent or external information
Return ONLY the structured plan."""


def planner_node(state: AgentState) -> dict:
	plan = _planner_llm().invoke(
		[
			{"role": "system", "content": PLANNER_SYSTEM},
			{"role": "user", "content": state["question"]},
		]
	)
	return {"plan": plan, "iterations": 0, "evidence": []}
