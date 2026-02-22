from langgraph.types import Command
from langchain_core.messages import AIMessage
from typing import List, Optional

from neo4j_onto2ai_toolset.langgraph_supervisors.supervisors import *
from langgraph.checkpoint.memory import InMemorySaver


def get_last_ai_content(messages: List) -> Optional[str]:
    """Return the content of the last non-empty AIMessage from a LangChain messages list."""
    if not messages:
        return None

    def _content(msg) -> str:
        c = getattr(msg, "content", "")
        return c if isinstance(c, str) else ""

    # Try index -1 first
    last = messages[-1]
    if isinstance(last, AIMessage) and _content(last).strip():
        return _content(last).strip()

    # Fallback: scan in reverse
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and _content(msg).strip():
            return _content(msg).strip()

    return None
config = {"configurable": {"thread_id": "checkpoint-thread-1"}}
def start_cli_chat():
    checkpointer=InMemorySaver()
    app = onto2ai_modeller.compile(checkpointer=checkpointer)
    context = ModelContextSchema(userid='weizhang')
    print("🤖 Chat started. Type `exit` to stop.")
    while True:
        user_input = input("🗨️  You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Exiting chat.")
            break
        state_of_input = {"messages": [{
            "role": "user",
            "content": f"{user_input}"
            }]}
        print(state_of_input)
        response = app.invoke(state_of_input,
                              context=context, config = config)
        # Handle LangGraph interrupt flows (human-in-the-loop)
        if isinstance(response, dict) and response.get("__interrupt__"):
            print(response["__interrupt__"])
            user_action = input("do you accept the change? please type either accept, reject or edit ")
            action = user_action.strip().lower()

            if action in {"accept", "approve", "ok", "yes", "y"}:
                response = app.invoke(Command(resume={"type": "accept"}), config=config)
            elif action in {"reject", "disapprove", "no", "n"}:
                response = app.invoke(Command(resume={"type": "reject"}), config=config)
            else:
                new_content = input("please provide new statement array in format of [statement]")
                response = app.invoke(Command(resume={"type": "edit", "new_content": new_content}), config=config)

        print(get_last_ai_content(response.get("messages", [])))




# start the chat
# create a new human model with namespace my-friend.com
start_cli_chat()
