from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio

# Initialize the LLM
model = ChatOpenAI(model="gpt-4o")

async def main():
    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Replace with the actual absolute path to your math_server.py file
                "args": ["math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # Ensure your weather server is running and streaming events on this endpoint
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            }
        }
    ) as client:
        # Create the ReAct-style agent with the tools loaded from the servers
        agent = create_react_agent(model, client.get_tools())

        # Ask a math question
        math_response = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})
        print("Math result:", math_response)

        # Ask a weather question
        weather_response = await agent.ainvoke({"messages": "what is the weather in NYC?"})
        print("Weather result:", weather_response)

# Run the async main function
asyncio.run(main())