from __future__ import annotations

from app.schemas import MemoryItem
from app.tokenizer import truncate_words


class ContextCompressor:
    def compress(self, memories: tuple[MemoryItem, ...], max_words: int = 90) -> str:
        if not memories:
            return ""
        bullets = []
        for memory in memories:
            label = memory.type.value.replace("_", " ")
            bullets.append(f"- {label}: {truncate_words(memory.content, max_words // max(1, len(memories)))}")
        return "\n".join(bullets)

