from app.evaluator import ContextEvaluator
from app.privacy_firewall import PrivacyFirewall
from app.context_manager import ContextManager
from app.schemas import ContextPacket, MemoryItem, MemoryType, ToolCall


def test_evaluator_scores_required_terms() -> None:
    memories = (MemoryItem("g1", MemoryType.GOAL, "Use OpenAI API and privacy controls.", "user", 1.0, pinned=True),)
    packet = ContextManager().build_packet("Need OpenAI API privacy controls.", memories)
    privacy = PrivacyFirewall().review(ToolCall("tool", {"query": "safe"}, "test"))
    report = ContextEvaluator().evaluate(packet, privacy, ("OpenAI API", "privacy"))
    assert report.task_success_score == 1.0
    assert report.privacy_score == 1.0


def test_task_echo_alone_is_not_retained_memory() -> None:
    packet = ContextPacket(
        task="Need OpenAI API and privacy controls.",
        prompt="Task:\nNeed OpenAI API and privacy controls.",
        selected_memories=(),
        compressed_summary="",
        decisions=(),
        token_estimate=8,
        compression_ratio=0.0,
    )
    privacy = PrivacyFirewall().review(ToolCall("tool", {"query": "safe"}, "test"))
    report = ContextEvaluator().evaluate(packet, privacy, ("OpenAI API", "privacy"))
    assert report.task_success_score == 0.0


def test_task_success_scores_selected_memory_not_task_echo() -> None:
    memory = MemoryItem("g1", MemoryType.GOAL, "Use OpenAI API.", "user", 1.0, pinned=True)
    packet = ContextPacket(
        task="Need privacy controls.",
        prompt="Task:\nNeed privacy controls.\n- [goal] Use OpenAI API. (source: user)",
        selected_memories=(memory,),
        compressed_summary="",
        decisions=(),
        token_estimate=12,
        compression_ratio=0.0,
    )
    privacy = PrivacyFirewall().review(ToolCall("tool", {"query": "safe"}, "test"))
    report = ContextEvaluator().evaluate(packet, privacy, ("OpenAI API", "privacy"))
    assert report.task_success_score == 0.5


def test_compressed_summary_counts_as_retained_memory() -> None:
    packet = ContextPacket(
        task="Need privacy controls.",
        prompt="Task:\nNeed privacy controls.",
        selected_memories=(),
        compressed_summary="- constraint: never leak privacy data.",
        decisions=(),
        token_estimate=10,
        compression_ratio=0.5,
    )
    privacy = PrivacyFirewall().review(ToolCall("tool", {"query": "safe"}, "test"))
    report = ContextEvaluator().evaluate(packet, privacy, ("privacy",))
    assert report.task_success_score == 1.0


def test_no_required_terms_does_not_require_memory() -> None:
    packet = ContextPacket(
        task="Summarize the conversation.",
        prompt="Task:\nSummarize the conversation.",
        selected_memories=(),
        compressed_summary="",
        decisions=(),
        token_estimate=6,
        compression_ratio=0.0,
    )
    privacy = PrivacyFirewall().review(ToolCall("tool", {"query": "safe"}, "test"))
    report = ContextEvaluator().evaluate(packet, privacy)
    assert report.task_success_score == 1.0

