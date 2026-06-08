import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure project root is importable when run as `python evals/run_eval.py`.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets import Dataset  # noqa: E402
from ragas import evaluate  # noqa: E402
from ragas.metrics import (  # noqa: E402
	answer_relevancy,
	context_precision,
	faithfulness,
)

from src.agents.graph import graph  # noqa: E402


def run():
	eval_set = json.loads(Path("evals/eval_set.json").read_text())
	rows = []
	for item in eval_set:
		state = graph.invoke({"question": item["question"], "evidence": []})
		rows.append(
			{
				"question": item["question"],
				"answer": state.get("final_answer") or state.get("draft") or "",
				"contexts": [e.content for e in state.get("evidence", [])[:5]],
				"ground_truth": " ".join(item.get("expected_keywords", [])),
			}
		)

	ds = Dataset.from_list(rows)
	result = evaluate(
		ds, metrics=[faithfulness, answer_relevancy, context_precision]
	)
	print(result)

	out = Path("evals/results") / f"run_{datetime.now(timezone.utc).isoformat()}.json"
	out.parent.mkdir(parents=True, exist_ok=True)
	out.write_text(json.dumps(getattr(result, "scores", str(result)), indent=2, default=str))


if __name__ == "__main__":
	run()
