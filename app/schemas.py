from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class MemoryType(str, Enum):
    GOAL = "goal"
    CONSTRAINT = "constraint"
    DECISION = "decision"
    TOOL_RESULT = "tool_result"
    FAILURE = "failure"
    USER_PREFERENCE = "user_preference"
    PRIVATE_DATA = "private_data"
    NOTE = "note"


class ContextAction(str, Enum):
    KEEP = "keep"
    COMPRESS = "compress"
    DROP = "drop"
    PIN = "pin"
    RETRIEVE = "retrieve"


class PrivacyDecision(str, Enum):
    ALLOW = "allow"
    REDACT = "redact"
    BLOCK = "block"


@dataclass(frozen=True)
class AgentEvent:
    role: str
    content: str
    source: str = "conversation"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class MemoryItem:
    id: str
    type: MemoryType
    content: str
    provenance: str
    importance: float = 0.5
    private: bool = False
    pinned: bool = False
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextDecision:
    item_id: str
    action: ContextAction
    reason: str
    score: float


@dataclass(frozen=True)
class ContextPacket:
    task: str
    prompt: str
    selected_memories: tuple[MemoryItem, ...]
    compressed_summary: str
    decisions: tuple[ContextDecision, ...]
    token_estimate: int
    compression_ratio: float


@dataclass(frozen=True)
class ToolCall:
    name: str
    payload: dict[str, Any]
    purpose: str


@dataclass(frozen=True)
class PrivacyFinding:
    kind: str
    message: str
    field: str


@dataclass(frozen=True)
class PrivacyReview:
    decision: PrivacyDecision
    safe_payload: dict[str, Any]
    findings: tuple[PrivacyFinding, ...]
    leak_count: int


@dataclass(frozen=True)
class EvaluationReport:
    task_success_score: float
    plan_retention_score: float
    memory_precision: float
    privacy_score: float
    token_savings_ratio: float
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextOpsRun:
    run_id: str
    task: str
    packet: ContextPacket
    privacy: PrivacyReview
    evaluation: EvaluationReport
    trace: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        for item in data["packet"]["selected_memories"]:
            item["type"] = item["type"].value
        for decision in data["packet"]["decisions"]:
            decision["action"] = decision["action"].value
        data["privacy"]["decision"] = self.privacy.decision.value
        return data

