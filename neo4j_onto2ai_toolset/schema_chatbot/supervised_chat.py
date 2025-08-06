from langchain.schema import AIMessage
from langgraph_supervisor import create_supervisor
from typing import List, Optional
from neo4j_onto2ai_toolset.langraph_agents.model_agents import *



supervisor = create_supervisor(
    # Each message in messages should follow the Chat Message format:
    # {
    # "role": "user" | "assistant" | "system" | "tool",
    # "content": str
    # }
    #
    agents=[model_qa_agent,rdb_ddl_agent,pydantic_class_agent],
    model=llm,
    prompt=(
    "You are a team supervisor managing all models."
    "For question about model, extract key concept from the question first"
    "If the quest is about validation of the model, then use model_qa_agent"
    "If the quest is about generate relational database schema of the model, then use rdb_ddl_agent"
    "If the quest is about generate python or pydantic class or schema of the model, then use pydantic_class_agent"
    )
)



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
    app = supervisor.compile()
    print("🤖 Chat started. Type `exit` to stop.")
    while True:
        user_input = input("🗨️  You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Exiting chat.")
            break
        state_of_input = {"messages": [{"role": "user",
                    # "content": "find person model and check any duplication?"
                    "content": f"{user_input}"
                }]}
        response = app.invoke(state_of_input)
        print(get_last_ai_content(response["messages"]))


# start the chat
start_cli_chat()
