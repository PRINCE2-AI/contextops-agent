from __future__ import annotations

import json
import tempfile
from pathlib import Path

from app.config import Settings
from app.memory_store import MemoryStore
from app.runner import ContextOpsRunner


def main() -> None:
    task = "Use OpenAI API, keep the privacy constraint, and summarize why context compression helps long-horizon agents."
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        settings = Settings(database_path=Path(tmp) / "contextops.db", token_budget=180)
        runner = ContextOpsRunner(settings=settings, store=MemoryStore(settings.resolved_database_path))
        run = runner.run(
            task,
            tool_payload={"query": "Research context engineering. Email prince@example.com and token=sk-test-private"},
            required_terms=("OpenAI API", "privacy", "compression"),
        )
        print(
            json.dumps(
                {
                    "run_id": run.run_id,
                    "selected_memories": len(run.packet.selected_memories),
                    "token_estimate": run.packet.token_estimate,
                    "compression_ratio": run.packet.compression_ratio,
                    "privacy_decision": run.privacy.decision.value,
                    "leak_count": run.privacy.leak_count,
                    "task_success_score": run.evaluation.task_success_score,
                    "plan_retention_score": run.evaluation.plan_retention_score,
                    "memory_precision": run.evaluation.memory_precision,
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    main()

