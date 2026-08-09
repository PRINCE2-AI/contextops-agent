from app.context_manager import ContextManager
from app.schemas import MemoryItem, MemoryType


def test_context_manager_compresses_and_selects_memory() -> None:
    memories = (
        MemoryItem("g1", MemoryType.GOAL, "Build a context engineering agent with OpenAI API.", "user", 0.95, pinned=True),
        MemoryItem("n1", MemoryType.NOTE, "Unrelated old note about frontend colors.", "scratch", 0.1),
        MemoryItem("f1", MemoryType.FAILURE, "The baseline forgot privacy constraints after many turns.", "eval", 0.7, tags=("privacy",)),
    )
    packet = ContextManager(token_budget=80).build_packet("Keep privacy constraints for the OpenAI API agent.", memories)
    assert packet.selected_memories
    assert "OpenAI API" in packet.prompt
    assert packet.compression_ratio >= 0

