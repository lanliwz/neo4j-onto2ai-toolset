from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, tool as lc_tool
from langgraph.types import interrupt

# LangGraph deprecated HumanInterrupt / HumanInterruptConfig classes.
# Use lightweight, forward-compatible structural typing instead.
HumanInterrupt = dict[str, Any]
HumanInterruptConfig = dict[str, Any]


def add_human_in_the_loop(
    tool: BaseTool | Callable[..., Any],
    *,
    interrupt_config: HumanInterruptConfig | None = None,
    review_prompt: str = "Please review the tool call",
) -> BaseTool:
    """Wrap a tool to support human-in-the-loop review (LangChain 1.2 compatible).

    The returned object is a LangChain tool that will:
      1) request approval/edit/feedback via LangGraph `interrupt`,
      2) execute the underlying tool only if approved (or edited),
      3) return user feedback directly to the graph if the reviewer responds.
    """

    # Normalize callable -> BaseTool
    if not isinstance(tool, BaseTool):
        tool = lc_tool(tool)

    # Avoid mutable defaults and allow callers to pass their own config
    if interrupt_config is None:
        interrupt_config = {
            "allow_accept": True,
            "allow_edit": True,
            "allow_respond": True,
        }

    tool_name = tool.name
    tool_description = tool.description
    tool_args_schema = tool.args_schema

    # LangChain tooling has evolved; support both `args_schema=` and `schema=` kwarg names.
    try:
        _tool_decorator = lc_tool(tool_name, description=tool_description, args_schema=tool_args_schema)
    except TypeError:
        _tool_decorator = lc_tool(tool_name, description=tool_description, schema=tool_args_schema)

    @_tool_decorator
    def call_tool_with_interrupt(config: RunnableConfig | None = None, **tool_input: Any) -> Any:
        """Tool wrapper that pauses for human review before invoking the underlying tool."""

        request: HumanInterrupt = {
            "action_request": {"action": tool_name, "args": tool_input},
            "config": interrupt_config,
            "description": review_prompt,
        }

        # `interrupt` returns a list; we send a single request
        response = interrupt([request])[0]
        response_type = response.get("type")

        if response_type == "accept":
            # Execute with original args
            return tool.invoke(tool_input, config=config)

        if response_type == "edit":
            # Update tool args from editor payload
            edited = response.get("args") or {}
            # LangGraph typically nests edited args under args['args']
            new_args = edited.get("args") if isinstance(edited, Mapping) else None
            if not isinstance(new_args, Mapping):
                raise ValueError(f"Invalid edit payload for tool '{tool_name}': {edited!r}")
            return tool.invoke(dict(new_args), config=config)

        if response_type == "response":
            # Human provided feedback to the LLM/graph; return it directly
            return response.get("args")

        raise ValueError(
            f"Unsupported interrupt response type for tool '{tool_name}': {response_type!r}"
        )

    return call_tool_with_interrupt