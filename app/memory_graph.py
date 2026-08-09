from __future__ import annotations

from collections import defaultdict

from app.schemas import MemoryItem


class MemoryGraph:
    def build_edges(self, memories: tuple[MemoryItem, ...]) -> dict[str, list[str]]:
        tags_by_id = {memory.id: set(memory.tags) for memory in memories}
        edges: dict[str, list[str]] = defaultdict(list)
        for left in memories:
            for right in memories:
                if left.id == right.id:
                    continue
                if tags_by_id[left.id] & tags_by_id[right.id]:
                    edges[left.id].append(right.id)
        return dict(edges)

    def reconstruct(self, seed_ids: tuple[str, ...], memories: tuple[MemoryItem, ...], depth: int = 1) -> tuple[MemoryItem, ...]:
        by_id = {memory.id: memory for memory in memories}
        edges = self.build_edges(memories)
        seen = set(seed_ids)
        frontier = list(seed_ids)
        for _ in range(depth):
            next_frontier: list[str] = []
            for item_id in frontier:
                for linked in edges.get(item_id, []):
                    if linked not in seen:
                        seen.add(linked)
                        next_frontier.append(linked)
            frontier = next_frontier
        return tuple(by_id[item_id] for item_id in seen if item_id in by_id)

