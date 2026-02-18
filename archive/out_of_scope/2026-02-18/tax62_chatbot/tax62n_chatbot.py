import asyncio
import uuid
from langchain_core.messages import HumanMessage, AIMessage
from tax62_chatbot.tax62n_graph import tax_chatbot_graph

async def run_test_conversation():
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    questions = [
        "What are the account payments in the year 2024?",
        "Which ones are for accounts in high property tax areas?"
    ]
    
    for q in questions:
        print(f"\nUser: {q}")
        async for event in tax_chatbot_graph.astream(
            {"messages": [HumanMessage(content=q)]}, 
            config, 
            stream_mode="values"
        ):
            if "messages" in event:
                last_msg = event["messages"][-1]
                if isinstance(last_msg, (HumanMessage, AIMessage)):
                    # Only print AI messages as the final output in this simplified test
                    pass
        
        # Get final state to show results
        final_state = await tax_chatbot_graph.aget_state(config)
        print(f"AI: {final_state.values['messages'][-1].content}")
        if final_state.values.get("cypher_statement"):
            print(f"Generated Cypher: {final_state.values['cypher_statement']}")

if __name__ == "__main__":
    asyncio.run(run_test_conversation())