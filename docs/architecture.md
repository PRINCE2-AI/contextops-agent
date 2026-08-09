# Architecture

ContextOps Agent is a context engineering layer that sits between a long-horizon agent and its model/tool calls.

```text
Task -> Memory Store -> Context Policy -> Graph Reconstruction -> Compression -> Privacy Firewall -> Eval Report
```

## Components

| Component | Role |
| --- | --- |
| `memory_store.py` | SQLite-backed typed memory with provenance |
| `context_policy.py` | Keep, compress, drop, pin, retrieve decisions |
| `memory_graph.py` | Lightweight tag graph for memory reconstruction |
| `context_manager.py` | Builds the managed prompt packet |
| `privacy_firewall.py` | Redacts or blocks sensitive tool payloads |
| `evaluator.py` | Scores task retention, memory precision, privacy, and token savings |
| `runner.py` | End-to-end demo orchestration |
| `api.py` | FastAPI service |
| `ui.py` | Streamlit dashboard |

## Design Principle

The project avoids raw transcript stuffing. Important facts are typed, attributed, scored, and either pinned, retrieved, compressed, or dropped.

