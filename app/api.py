from __future__ import annotations

from typing import Any

try:
    from fastapi import FastAPI
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install API dependencies with `pip install -r requirements.txt`.") from exc

from app.config import get_settings
from app.runner import ContextOpsRunner


class RunRequest(BaseModel):
    task: str
    tool_payload: dict[str, str] | None = Field(default=None)
    required_terms: list[str] = Field(default_factory=list)


api = FastAPI(
    title="ContextOps Agent",
    description="Context engineering, memory, privacy firewall, and eval harness for long-horizon agents.",
    version="0.1.0",
)


@api.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "openai_enabled": settings.openai_enabled,
        "model": settings.openai_model,
        "token_budget": settings.token_budget,
        "database_path": str(settings.resolved_database_path),
    }


@api.post("/run-contextops")
def run_contextops(request: RunRequest) -> dict[str, Any]:
    run = ContextOpsRunner().run(request.task, request.tool_payload, tuple(request.required_terms))
    return run.to_dict()

