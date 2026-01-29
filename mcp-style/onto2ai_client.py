from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import asyncio
import os
import sys

# Initialize the LLM with the new target model
model = ChatOpenAI(model="gpt-5.2")

async def main():
    # Define the onto2ai server path
    server_path = "/Users/weizhang/github/neo4j-onto2ai-toolset/neo4j_onto2ai_toolset/onto2ai_mcp.py"
    
    # Pre-connection check: ensure required Neo4j credentials are in the environment
    if not os.getenv("NEO4J_MODEL_DB_PASSWORD"):
        print("ERROR: NEO4J_MODEL_DB_PASSWORD not found in environment.")
        print("Please set it before running: export NEO4J_MODEL_DB_PASSWORD=your_password")
        return

    client = MultiServerMCPClient(
        {
            "onto2ai": {
                "command": sys.executable,
                "args": [server_path],
                "transport": "stdio",
                "env": os.environ.copy(),
            }
        }
    )
    
    # Create the agent with the tools loaded from onto2ai_mcp using the modern create_agent factory
    tools = await client.get_tools()
    
    print("\n=== Available Tools ===")
    for tool in tools:
        print(f"- {tool.name}: {tool.description.split('.')[0]}")
    
    agent = create_agent(model, tools)
        
    # Example interaction: Ask to see the schema for a class
    # Note: In a real scenario, this would be invoked by user input
    print("\nOnto2AI Client Ready. Sending test query...")
    
    message = "Get the materialized schema for the 'person' class."
    response = await agent.ainvoke({"messages": [("user", message)]})
    print("\n=== AI Response ===")
    print(response["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())
