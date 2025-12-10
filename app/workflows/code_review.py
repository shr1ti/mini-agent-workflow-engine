from app.engine.engine import WorkflowEngine
from app.engine.models import EdgeConfig, GraphConfig, NodeConfig


def build_code_review_graph(engine: WorkflowEngine) -> str:
    """
    Build the example 'Code Review Mini-Agent' workflow.

    Nodes:
      1. extract_functions
      2. check_complexity
      3. detect_issues
      4. suggest_improvements
      5. evaluate_quality (loops until quality_score >= threshold)
    """

    nodes = {
        "extract_functions": NodeConfig(
            id="extract_functions",
            tool="extract_functions",
        ),
        "check_complexity": NodeConfig(
            id="check_complexity",
            tool="check_complexity",
        ),
        "detect_issues": NodeConfig(
            id="detect_issues",
            tool="detect_issues",
        ),
        "suggest_improvements": NodeConfig(
            id="suggest_improvements",
            tool="suggest_improvements",
        ),
        "evaluate_quality": NodeConfig(
            id="evaluate_quality",
            tool="evaluate_quality",
        ),
    }

    edges = [
        EdgeConfig(from_node="extract_functions", to_node="check_complexity"),
        EdgeConfig(from_node="check_complexity", to_node="detect_issues"),
        EdgeConfig(from_node="detect_issues", to_node="suggest_improvements"),
        EdgeConfig(from_node="suggest_improvements", to_node="evaluate_quality"),

        # Loop edge: if done == False, go back to detect_issues
        EdgeConfig(
            from_node="evaluate_quality",
            to_node="detect_issues",
            condition_key="done",
            condition_value=False,
        ),
        # Exit edge: if done == True, stop (no further edges from here)
        # (we simply don't add any outgoing edges for the True case)
    ]

    graph = GraphConfig(
        id="code_review",
        start_node="extract_functions",
        nodes=nodes,
        edges=edges,
        max_steps=20,
    )

    return engine.register_graph(graph)
