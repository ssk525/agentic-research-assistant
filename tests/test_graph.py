from langgraph.graph import END

from src.agents.graph import build_graph, route_after_critic


def test_graph_builds():
	g = build_graph()
	assert g is not None


def test_route_loops_when_not_approved():
	class _R:
		approved = False

	state = {"critic_report": _R(), "iterations": 1}
	assert route_after_critic(state) == "worker"


def test_route_stops_when_approved():
	class _R:
		approved = True

	state = {"critic_report": _R(), "iterations": 1}
	assert route_after_critic(state) == END


def test_route_stops_after_max_iters():
	class _R:
		approved = False

	state = {"critic_report": _R(), "iterations": 3}
	assert route_after_critic(state) == END
