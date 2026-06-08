from functools import lru_cache

from langchain_openai import ChatOpenAI

from src.config import settings
from src.agents.state import AgentState, CriticReport


@lru_cache(maxsize=1)
def _critic_llm():
	llm = ChatOpenAI(
		model=settings.llm_model,
		api_key=settings.openai_api_key,
		temperature=0,
	)
	return llm.with_structured_output(CriticReport)


CRITIC_SYSTEM = """You are a strict research critic. Score the draft on:
- faithfulness (0-1): are all claims supported by the evidence?
- citation_coverage (0-1): does every non-trivial claim have an inline citation?
- completeness (0-1): does it fully address the user's question?
- overall (0-1): weighted average.
Approve only if overall >= 0.8. Give concrete, actionable feedback if not approved."""


def critic_node(state: AgentState) -> dict:
	evidence_block = "\n".join(
		f"[{e.source}] {e.content[:200]}" for e in state["evidence"][:30]
	)
	report = _critic_llm().invoke(
		[
			{"role": "system", "content": CRITIC_SYSTEM},
			{
				"role": "user",
				"content": (
					f"Question: {state['question']}\n\n"
					f"Draft:\n{state['draft']}\n\n"
					f"Evidence:\n{evidence_block}"
				),
			},
		]
	)
	done = report.approved or state["iterations"] >= 3
	final = state["draft"] if done else None
	return {"critic_report": report, "final_answer": final}
