import os
import sys
import uuid

# Ensure the project root is importable when run via `streamlit run src/app.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st  # noqa: E402

from src.agents.graph import graph  # noqa: E402
from src.observability.tracing import get_langfuse_handler  # noqa: E402

st.set_page_config(
	page_title="Agentic Research Assistant", page_icon="\U0001F916", layout="wide"
)
st.title("\U0001F916 Agentic Research Assistant")
st.caption("Planner -> Worker -> Critic | RAG + SQL + Web | LangGraph + Langfuse")

q = st.text_area("Ask a research question:", height=100)

if st.button("Run", type="primary") and q.strip():
	session_id = str(uuid.uuid4())
	handler = get_langfuse_handler(session_id=session_id)
	config = {"callbacks": [handler]} if handler else {}

	with st.status("Running 3-agent pipeline...", expanded=True) as status:
		seen = set()
		final_state = None
		for state in graph.stream(
			{"question": q, "evidence": []}, config=config, stream_mode="values"
		):
			final_state = state
			if state.get("plan") and "plan" not in seen:
				seen.add("plan")
				st.write("\u2705 **planner** completed")
			if state.get("draft") and "draft" not in seen:
				seen.add("draft")
				st.write("\u2705 **worker** produced a draft")
			if state.get("critic_report") and "critic" not in seen:
				seen.add("critic")
				st.write("\u2705 **critic** scored the draft")
		status.update(label="Done", state="complete")

	if final_state:
		st.markdown("### Final Answer")
		st.markdown(final_state.get("final_answer") or final_state.get("draft") or "")

		cr = final_state.get("critic_report")
		if cr:
			col1, col2, col3, col4 = st.columns(4)
			col1.metric("Faithfulness", f"{cr.faithfulness:.2f}")
			col2.metric("Citations", f"{cr.citation_coverage:.2f}")
			col3.metric("Completeness", f"{cr.completeness:.2f}")
			col4.metric("Iterations", final_state.get("iterations", 1))
