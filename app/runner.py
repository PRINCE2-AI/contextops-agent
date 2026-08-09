from __future__ import annotations

import uuid

from app.config import Settings, get_settings
from app.context_manager import ContextManager
from app.evaluator import ContextEvaluator
from app.memory_store import MemoryStore
from app.privacy_firewall import PrivacyFirewall
from app.schemas import ContextOpsRun, MemoryType, ToolCall


class ContextOpsRunner:
    def __init__(self, settings: Settings | None = None, store: MemoryStore | None = None) -> None:
        self.settings = settings or get_settings()
        self.store = store or MemoryStore(self.settings.resolved_database_path)
        self.manager = ContextManager(token_budget=self.settings.token_budget)
        self.firewall = PrivacyFirewall()
        self.evaluator = ContextEvaluator()

    def seed_demo_memory(self) -> None:
        if self.store.list():
            return
        self.store.add("Build a ContextOps Agent demo that proves context compression, plan retention, and privacy-safe tool use.", MemoryType.GOAL, "demo", 0.95, pinned=True, tags=("demo", "agent"))
        self.store.add("Use OpenAI API as the optional model provider; do not depend on Ollama.", MemoryType.CONSTRAINT, "user", 0.9, pinned=True, tags=("api", "constraint"))
        self.store.add("Never send API keys, private email addresses, or local Windows paths to external tools.", MemoryType.CONSTRAINT, "privacy-policy", 0.92, pinned=True, tags=("privacy", "tools"))
        self.store.add("Earlier baseline agents repeated work after context exceeded the budget.", MemoryType.FAILURE, "baseline-run", 0.7, tags=("context", "failure"))
        self.store.add("User email prince@example.com and OPENAI_API_KEY=sk-test-private should remain private.", MemoryType.PRIVATE_DATA, "synthetic-secret", 1.0, private=True, tags=("privacy",))
        self.store.add("Tool result: LangChain describes context engineering as write, select, compress, and isolate.", MemoryType.TOOL_RESULT, "research-note", 0.72, tags=("context", "research"))

    def run(self, task: str, tool_payload: dict[str, str] | None = None, required_terms: tuple[str, ...] = ()) -> ContextOpsRun:
        self.seed_demo_memory()
        packet = self.manager.build_packet(task, self.store.list())
        call = ToolCall("research_tool", tool_payload or {"query": packet.prompt}, "Demonstrate privacy-aware tool payload review.")
        privacy = self.firewall.review(call, strict=self.settings.privacy_strict)
        evaluation = self.evaluator.evaluate(packet, privacy, required_terms=required_terms)
        trace = (
            {"event": "context_packet", "token_estimate": packet.token_estimate, "compression_ratio": packet.compression_ratio},
            {"event": "privacy_review", "decision": privacy.decision.value, "leaks": privacy.leak_count},
            {"event": "evaluation", "task_success": evaluation.task_success_score, "memory_precision": evaluation.memory_precision},
        )
        return ContextOpsRun(uuid.uuid4().hex[:12], task, packet, privacy, evaluation, trace)

