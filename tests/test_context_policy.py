from app.context_policy import ContextPolicy
from app.schemas import MemoryItem, MemoryType


def test_pinned_goal_is_retained() -> None:
    memory = MemoryItem("m1", MemoryType.GOAL, "Use OpenAI API and preserve privacy constraints.", "user", 0.9, pinned=True)
    decision = ContextPolicy().decide("Build an OpenAI API agent", memory, 100)
    assert decision.action.value == "pin"

