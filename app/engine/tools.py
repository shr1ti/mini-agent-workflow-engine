from typing import Any, Callable, Dict


State = Dict[str, Any]


class ToolRegistry:
    """Very small registry mapping tool names -> Python callables."""

    def __init__(self) -> None:
        self._tools: Dict[str, Callable[[State], State]] = {}

    def register(self, name: str, func: Callable[[State], State]) -> None:
        self._tools[name] = func

    def get(self, name: str) -> Callable[[State], State]:
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered")
        return self._tools[name]


# Single global registry used by the engine
tool_registry = ToolRegistry()


# --------- Code review tools (Option A) ---------


def extract_functions(state: State) -> State:
    """Fake function extractor: counts 'def ' occurrences."""
    code: str = state.get("code", "")
    functions = [line for line in code.splitlines() if line.strip().startswith("def ")]
    state["functions"] = functions
    state["num_functions"] = len(functions)
    return state


def check_complexity(state: State) -> State:
    """
    Very silly complexity checker:
    - counts lines and if > 30 sets complexity to 'high'
    """
    code: str = state.get("code", "")
    num_lines = len(code.splitlines())
    state["num_lines"] = num_lines
    state["complexity"] = "high" if num_lines > 30 else "low"
    return state


def detect_issues(state: State) -> State:
    """
    Fake issue detector:
    - counts TODOs as issues
    """
    code: str = state.get("code", "")
    issues = [line for line in code.splitlines() if "TODO" in line]
    state["issues"] = issues
    state["issue_count"] = len(issues)
    return state


def suggest_improvements(state: State) -> State:
    """Generate simple text suggestions based on issues & complexity."""
    suggestions = []

    if state.get("complexity") == "high":
        suggestions.append("Consider splitting large functions into smaller ones.")

    if state.get("issue_count", 0) > 0:
        suggestions.append("Resolve TODO comments before merging.")

    if not suggestions:
        suggestions.append("Code looks clean. No major improvements needed.")

    state["suggestions"] = suggestions
    return state


def evaluate_quality(state: State) -> State:
    """
    Turn our heuristic signals into a 'quality_score' between 0 and 1
    and set 'done' flag for looping.
    """
    score = 1.0

    if state.get("complexity") == "high":
        score -= 0.3

    issue_count = state.get("issue_count", 0)
    if issue_count > 0:
        score -= min(0.5, 0.1 * issue_count)

    # clamp
    score = max(0.0, min(1.0, score))

    state["quality_score"] = score

    # threshold we want to reach
    threshold = state.get("quality_threshold", 0.7)
    state["done"] = score >= threshold
    return state


# Register tools at import time
tool_registry.register("extract_functions", extract_functions)
tool_registry.register("check_complexity", check_complexity)
tool_registry.register("detect_issues", detect_issues)
tool_registry.register("suggest_improvements", suggest_improvements)
tool_registry.register("evaluate_quality", evaluate_quality)
