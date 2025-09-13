import uuid
from langgraph.types import Command
from langchain.schema import AIMessage
from typing import List, Optional

from neo4j_onto2ai_toolset.langgraph_supervisors.supervisors import *
from langgraph.runtime import get_runtime


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
config = {"configurable": {"thread_id": "checkpoint-thread-1"}}
def start_cli_chat():
    checkpointer=InMemorySaver()
    app = model_manager.compile(checkpointer=checkpointer)
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
        print(response['__interrupt__'])
        user_action =  input("do you accept the change? please type either accept or edit")
        if user_action.strip().lower() in {"accept", "approve","ok","yes"}:
            response = app.invoke(Command(resume={"type":"accept"}),config=config)
            print(get_last_ai_content(response["messages"]))
        else:
            new_content = input("please provide new statement array in format of [statement]")
            response = app.invoke(Command(resume={"type": "edit","new_content":f"\"{new_content}\""}), config=config)
            print(get_last_ai_content(response["messages"]))


# start the chat
# create a new human model with namespace my-friend.com
start_cli_chat()
