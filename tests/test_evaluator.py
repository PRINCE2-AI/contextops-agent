from app.evaluator import ContextEvaluator
from app.privacy_firewall import PrivacyFirewall
from app.context_manager import ContextManager
from app.schemas import MemoryItem, MemoryType, ToolCall


def test_evaluator_scores_required_terms() -> None:
    memories = (MemoryItem("g1", MemoryType.GOAL, "Use OpenAI API and privacy controls.", "user", 1.0, pinned=True),)
    packet = ContextManager().build_packet("Need OpenAI API privacy controls.", memories)
    privacy = PrivacyFirewall().review(ToolCall("tool", {"query": "safe"}, "test"))
    report = ContextEvaluator().evaluate(packet, privacy, ("OpenAI API", "privacy"))
    assert report.task_success_score == 1.0
    assert report.privacy_score == 1.0

