from typing import Any, List, TypedDict


class AgentState(TypedDict, total=False):
    """Lightweight state contract used by prompt-build helpers."""

    input: str
    concept: str
    namespace: str
    cypher_statements: List[str]
    intermediate_steps: List[Any]
    output: Any
    messages: List[Any]
