from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from app.engine.models import (
    EdgeConfig,
    ExecutionLogEntry,
    GraphConfig,
    GraphRunRequest,
    GraphRunResult,
)
from app.engine.tools import tool_registry


class WorkflowEngine:
    """
    Minimal in-memory workflow / graph engine.
    - stores graphs
    - runs them synchronously
    - stores run results
    """

    def __init__(self) -> None:
        self.graphs: Dict[str, GraphConfig] = {}
        self.runs: Dict[str, GraphRunResult] = {}

    # ---------- Graph management ----------

    def register_graph(self, graph: GraphConfig) -> str:
        self.graphs[graph.id] = graph
        return graph.id

    def get_graph(self, graph_id: str) -> GraphConfig:
        if graph_id not in self.graphs:
            raise KeyError(f"Graph '{graph_id}' not found")
        return self.graphs[graph_id]

    # ---------- Execution ----------

    def run(self, request: GraphRunRequest) -> GraphRunResult:
        graph = self.get_graph(request.graph_id)
        state: Dict[str, Any] = dict(request.initial_state)
        log: list[ExecutionLogEntry] = []

        current_node_id = graph.start_node
        steps = 0

        while current_node_id is not None and steps < graph.max_steps:
            steps += 1

            node_cfg = graph.nodes[current_node_id]
            tool = tool_registry.get(node_cfg.tool)

            # run the node
            state = tool(state)

            # log snapshot
            log.append(
                ExecutionLogEntry(
                    node=current_node_id,
                    state_snapshot=dict(state),
                )
            )

            # find next node via edges
            next_node: str | None = None
            for edge in graph.edges:
                if edge.from_node != current_node_id:
                    continue

                # no condition -> always take this edge
                if edge.condition_key is None:
                    next_node = edge.to_node
                    break

                # conditional edge
                if state.get(edge.condition_key) == edge.condition_value:
                    next_node = edge.to_node
                    break

            current_node_id = next_node

        run_id = uuid4().hex
        result = GraphRunResult(
            run_id=run_id,
            graph_id=graph.id,
            final_state=state,
            log=log,
        )
        self.runs[run_id] = result
        return result

    # ---------- Run lookup ----------

    def get_run(self, run_id: str) -> GraphRunResult:
        if run_id not in self.runs:
            raise KeyError(f"Run '{run_id}' not found")
        return self.runs[run_id]
