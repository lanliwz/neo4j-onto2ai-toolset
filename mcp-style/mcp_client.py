from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
import asyncio

# Initialize the OpenAI model
model = ChatOpenAI(model="gpt-4o")

# Set up server parameters — replace with the absolute path to your math_server.py
server_params = StdioServerParameters(
    command="python",
    args=["math_server.py"]  # <- Change this to your actual file path
)

async def run_agent():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()  # Initialize MCP session

            tools = await load_mcp_tools(session)  # Load available tools from the server

            agent = create_react_agent(model, tools)  # Create the ReAct-style agent

            # Ask the agent a question
            result = await agent.ainvoke({"messages": "what's (3 + 5) x 12?"})

            print(result)

# Run the async function
asyncio.run(run_agent())