from langchain.schema import AIMessage
from langgraph_supervisor import create_supervisor
from typing import List, Optional
from neo4j_onto2ai_toolset.langraph_agents.model_agents import *

from neo4j_onto2ai_toolset.langraph_agents.supervisors import *


def get_last_ai_content(messages: List) -> Optional[str]:
    """
    Returns the content of the last non-empty AIMessage from a LangChain messages list.
    Tries index -1 first, then scans backward as fallback.
    """
    # Try index -1 first
    last = messages[-1]
    if isinstance(last, AIMessage) and last.content.strip():
        return last.content.strip()

    # Fallback: scan in reverse
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content.strip():
            return msg.content.strip()

    return None  # No AIMessage found

def start_cli_chat():
    app = model2schema_supervisor.compile()
    print("🤖 Chat started. Type `exit` to stop.")
    while True:
        user_input = input("🗨️  You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Exiting chat.")
            break
        state_of_input = {"messages": [{"role": "user",
                    "content": f"{user_input}"
                }]}
        response = app.invoke(state_of_input)
        print(get_last_ai_content(response["messages"]))


# start the chat
start_cli_chat()
