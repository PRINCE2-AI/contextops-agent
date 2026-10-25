from __future__ import annotations

from app.schemas import ContextPacket, EvaluationReport, MemoryType, PrivacyReview


class ContextEvaluator:
    def evaluate(self, packet: ContextPacket, privacy: PrivacyReview, required_terms: tuple[str, ...] = ()) -> EvaluationReport:
        required = [term.lower() for term in required_terms if term]
        plan_memories = [memory for memory in packet.selected_memories if memory.type in {MemoryType.GOAL, MemoryType.CONSTRAINT, MemoryType.DECISION}]
        relevant_memories = [decision for decision in packet.decisions if decision.score >= 0.45]
        selected_relevant = [memory for memory in packet.selected_memories if any(decision.item_id == memory.id and decision.score >= 0.45 for decision in packet.decisions)]
        plan_score = 1.0 if plan_memories else 0.0
        precision = 1.0 if not packet.selected_memories else len(selected_relevant) / len(packet.selected_memories)

        retained_text = "\n".join(
            [f"{memory.type.value} {memory.content} {memory.provenance}" for memory in packet.selected_memories]
            + ([packet.compressed_summary] if packet.compressed_summary else [])
        ).lower()
        retained = sum(1 for term in required if term in retained_text)
        task_success = 1.0 if not required else retained / len(required)

        privacy_score = max(0.0, 1.0 - privacy.leak_count * 0.25)
        notes = []
        if not relevant_memories:
            notes.append("No relevant memories were available.")
        if required and retained < len(required):
            notes.append("Some required terms were missing from selected and compressed memory.")
        if privacy.leak_count:
            notes.append(f"{privacy.leak_count} privacy finding(s) were detected.")
        return EvaluationReport(
            task_success_score=round(task_success, 3),
            plan_retention_score=round(plan_score, 3),
            memory_precision=round(precision, 3),
            privacy_score=round(privacy_score, 3),
            token_savings_ratio=packet.compression_ratio,
            notes=tuple(notes),
        )

