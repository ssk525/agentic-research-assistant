from langgraph.graph import StateGraph, END

from src.agents.state import AgentState
from src.agents.planner import planner_node
from src.agents.worker import worker_node
from src.agents.critic import critic_node


def route_after_critic(state: AgentState) -> str:
	if state["critic_report"].approved or state["iterations"] >= 3:
		return END
	return "worker"


def build_graph():
	g = StateGraph(AgentState)
	g.add_node("planner", planner_node)
	g.add_node("worker", worker_node)
	g.add_node("critic", critic_node)
	g.set_entry_point("planner")
	g.add_edge("planner", "worker")
	g.add_edge("worker", "critic")
	g.add_conditional_edges(
		"critic", route_after_critic, {"worker": "worker", END: END}
	)
	return g.compile()


graph = build_graph()
