from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
import os
import sys

def get_model():
    """Retrieve the LLM based on environment variables or defaults."""
    # Default to gemini-2.0-flash (per user request for Gemini 3 Flash / latest)
    model_name = os.getenv("LLM_MODEL_NAME", "gemini-3-flash-preview")
    
    if "gemini" in model_name.lower():
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY not found. Defaulting to OpenAI (gpt-5.2).")
            print("To use Gemini, please: export GOOGLE_API_KEY=your_key")
            model_name = "gpt-5.2"
        else:
            print(f"Using Gemini model: {model_name}")

            return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)

    # Default/Fallback to OpenAI
    print(f"Using OpenAI model: {model_name}")
    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model=model_name)
    
# Initialize the LLM with the new target model
model = get_model()

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
