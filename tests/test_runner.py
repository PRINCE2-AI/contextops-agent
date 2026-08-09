from pathlib import Path

from app.config import Settings
from app.memory_store import MemoryStore
from app.runner import ContextOpsRunner


def test_runner_produces_eval_and_privacy_review(tmp_path: Path) -> None:
    settings = Settings(database_path=tmp_path / "contextops.db", token_budget=180)
    runner = ContextOpsRunner(settings=settings, store=MemoryStore(settings.resolved_database_path))
    run = runner.run(
        "Use OpenAI API and preserve privacy while compressing context.",
        {"query": "email prince@example.com and token=sk-test-private"},
        ("OpenAI API", "privacy"),
    )
    assert run.evaluation.plan_retention_score == 1.0
    assert run.privacy.leak_count >= 1
    assert run.packet.selected_memories

