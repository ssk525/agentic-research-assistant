from src.agents.planner import PLANNER_SYSTEM, planner_node
from src.agents.state import Plan, SubQuestion


class FakePlannerLLM:
    def __init__(self, plan: Plan) -> None:
        self.plan = plan
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return self.plan


def test_planner_splits_question_and_assigns_tools(monkeypatch):
    plan = Plan(
        sub_questions=[
            SubQuestion(question="What PSNR did SwinIR report?", tool="rag_search", rationale="in corpus"),
            SubQuestion(question="When was ESRGAN released?", tool="sql_query", rationale="facts table"),
            SubQuestion(question="Any 2026 follow-up papers?", tool="web_search", rationale="recent"),
        ]
    )
    fake = FakePlannerLLM(plan)

    monkeypatch.setattr("src.agents.planner._planner_llm", lambda: fake)

    out = planner_node({"question": "Compare ESRGAN and SwinIR"})

    assert len(out["plan"].sub_questions) == 3
    assert {sq.tool for sq in out["plan"].sub_questions} == {"rag_search", "sql_query", "web_search"}
    assert out["iterations"] == 0
    assert out["evidence"] == []
    assert fake.calls[0][0]["content"] == PLANNER_SYSTEM
    assert fake.calls[0][1]["content"] == "Compare ESRGAN and SwinIR"


def test_planner_keeps_two_to_four_sub_questions(monkeypatch):
    plan = Plan(
        sub_questions=[
            SubQuestion(question="A", tool="rag_search", rationale="corpus"),
            SubQuestion(question="B", tool="rag_search", rationale="corpus"),
        ]
    )
    monkeypatch.setattr("src.agents.planner._planner_llm", lambda: FakePlannerLLM(plan))
    out = planner_node({"question": "What is SRGAN?"})
    n = len(out["plan"].sub_questions)
    assert 2 <= n <= 4
