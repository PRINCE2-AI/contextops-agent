from __future__ import annotations

from app.compressor import ContextCompressor
from app.context_policy import ContextPolicy
from app.memory_graph import MemoryGraph
from app.schemas import ContextAction, ContextPacket, MemoryItem
from app.tokenizer import estimate_tokens


class ContextManager:
    def __init__(self, token_budget: int = 1400) -> None:
        self.token_budget = token_budget
        self.policy = ContextPolicy()
        self.compressor = ContextCompressor()
        self.graph = MemoryGraph()

    def build_packet(self, task: str, memories: tuple[MemoryItem, ...]) -> ContextPacket:
        decisions = []
        selected: list[MemoryItem] = []
        compressed_candidates: list[MemoryItem] = []
        remaining = self.token_budget
        for memory in memories:
            decision = self.policy.decide(task, memory, remaining)
            decisions.append(decision)
            if decision.action in {ContextAction.PIN, ContextAction.KEEP}:
                selected.append(memory)
                remaining -= estimate_tokens(memory.content)
            elif decision.action == ContextAction.COMPRESS:
                compressed_candidates.append(memory)
        reconstructed = self.graph.reconstruct(tuple(memory.id for memory in selected), memories, depth=1)
        for memory in reconstructed:
            if memory not in selected and not memory.private:
                selected.append(memory)
        summary = self.compressor.compress(tuple(compressed_candidates))
        prompt = self._render_prompt(task, tuple(selected), summary)
        raw_memory_dump = "\n".join(
            f"type={memory.type.value}; source={memory.provenance}; tags={','.join(memory.tags)}; content={memory.content}"
            for memory in memories
        )
        full_tokens = estimate_tokens(task) + estimate_tokens(raw_memory_dump) + 60
        packet_tokens = estimate_tokens(prompt)
        compression_ratio = 0.0 if full_tokens == 0 else round(1.0 - min(1.0, packet_tokens / full_tokens), 3)
        return ContextPacket(
            task=task,
            prompt=prompt,
            selected_memories=tuple(selected),
            compressed_summary=summary,
            decisions=tuple(decisions),
            token_estimate=packet_tokens,
            compression_ratio=compression_ratio,
        )

    @staticmethod
    def _render_prompt(task: str, selected: tuple[MemoryItem, ...], summary: str) -> str:
        lines = ["You are a long-horizon AI agent. Use the managed context below.", "", "Task:", task, ""]
        if selected:
            lines.append("Pinned and retrieved memory:")
            for memory in selected:
                lines.append(f"- [{memory.type.value}] {memory.content} (source: {memory.provenance})")
            lines.append("")
        if summary:
            lines.extend(["Compressed older context:", summary, ""])
        lines.append("Answer using only relevant context. Preserve constraints and avoid leaking private data.")
        return "\n".join(lines)
