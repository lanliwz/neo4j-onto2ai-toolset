from typing import Any, List, TypedDict


class AgentState(TypedDict, total=False):
    input: str
    concept: str
    namespace: str
    cypher_statements: List[str]
    intermediate_steps: List[Any]
    output: Any
