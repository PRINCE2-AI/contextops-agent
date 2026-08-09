from __future__ import annotations

from app.schemas import ContextAction, ContextDecision, MemoryItem, MemoryType
from app.tokenizer import estimate_tokens


class ContextPolicy:
    def score(self, task: str, memory: MemoryItem) -> float:
        task_terms = {term.strip(".,:;()[]{}").lower() for term in task.split() if len(term) > 3}
        content = memory.content.lower()
        overlap = sum(1 for term in task_terms if term in content)
        type_bonus = {
            MemoryType.GOAL: 0.22,
            MemoryType.CONSTRAINT: 0.2,
            MemoryType.DECISION: 0.16,
            MemoryType.FAILURE: 0.12,
            MemoryType.USER_PREFERENCE: 0.1,
            MemoryType.TOOL_RESULT: 0.08,
            MemoryType.PRIVATE_DATA: -0.3,
            MemoryType.NOTE: 0.0,
        }[memory.type]
        pinned_bonus = 0.35 if memory.pinned else 0.0
        score = memory.importance + type_bonus + pinned_bonus + min(0.35, overlap * 0.07)
        return round(max(0.0, min(1.0, score)), 3)

    def decide(self, task: str, memory: MemoryItem, remaining_budget: int) -> ContextDecision:
        score = self.score(task, memory)
        token_cost = estimate_tokens(memory.content)
        if memory.pinned:
            return ContextDecision(memory.id, ContextAction.PIN, "Pinned memory is always retained.", score)
        if memory.private and score < 0.95:
            return ContextDecision(memory.id, ContextAction.DROP, "Private memory is excluded unless explicitly required.", score)
        if score >= 0.74 and token_cost <= remaining_budget:
            return ContextDecision(memory.id, ContextAction.KEEP, "High relevance and fits context budget.", score)
        if score >= 0.45:
            return ContextDecision(memory.id, ContextAction.COMPRESS, "Moderate relevance; compress before inclusion.", score)
        return ContextDecision(memory.id, ContextAction.DROP, "Low relevance for this task.", score)

