from typing import Any, Dict, List, Optional
from pydantic import BaseModel


# ---------- Graph definition models ----------

class NodeConfig(BaseModel):
    """A single node in the workflow graph."""
    id: str                # e.g. "extract_functions"
    tool: str              # which tool to call, e.g. "extract_functions"


class EdgeConfig(BaseModel):
    """A directed edge between two nodes, with optional simple condition."""
    from_node: str
    to_node: str
    # If condition_key is set, we only follow this edge when:
    #   state[condition_key] == condition_value
    condition_key: Optional[str] = None
    condition_value: Optional[Any] = None


class GraphConfig(BaseModel):
    """Full workflow graph description."""
    id: str
    start_node: str
    nodes: Dict[str, NodeConfig]
    edges: List[EdgeConfig]
    max_steps: int = 50  # safety to avoid infinite loops


# ---------- Run models ----------

class GraphRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]


class ExecutionLogEntry(BaseModel):
    node: str
    state_snapshot: Dict[str, Any]


class GraphRunResult(BaseModel):
    run_id: str
    graph_id: str
    final_state: Dict[str, Any]
    log: List[ExecutionLogEntry]
