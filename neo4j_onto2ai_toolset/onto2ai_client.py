from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import asyncio
import os
import sys
import json
from langchain_core.callbacks import BaseCallbackHandler

class ToolLoggingCallbackHandler(BaseCallbackHandler):
    """Callback handler for logging tool usage."""
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "Unknown Tool")
        print(f"\n🛠️  [MCP TOOL CALL] {tool_name}")
        print(f"   Input: {input_str}")

class Onto2AIClient:
    """
    Client for interacting with the Onto2AI MCP server.
    Handles tool discovery and agent creation.
    """
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME", "gemini-3-flash-preview")
        self.llm = self._get_model()
        self.client = None
        self.tools = []
        self.agent = None

    def _get_model(self):
        """Retrieve the LLM based on environment variables or defaults."""
        if "gemini" in self.model_name.lower():
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                print("WARNING: GOOGLE_API_KEY not found. Defaulting to OpenAI (gpt-5.2).")
                self.model_name = "gpt-5.2"
            else:
                return ChatGoogleGenerativeAI(model=self.model_name, google_api_key=api_key)

        # Default/Fallback to OpenAI
        return ChatOpenAI(model=self.model_name)

    async def connect(self):
        """Connect to the MCP server and initialize tools/agent."""
        if self.client:
            return

        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "onto2ai_mcp.py")
        
        self.client = MultiServerMCPClient(
            {
                "onto2ai": {
                    "command": sys.executable,
                    "args": [server_path],
                    "transport": "stdio",
                    "env": os.environ.copy(),
                }
            }
        )
        
        self.tools = await self.client.get_tools()
        self.agent = create_agent(self.llm, self.tools)
        return self

    async def chat(self, message: str):
        """Send a message to the agent and get a response."""
        if not self.agent:
            await self.connect()
        
        callbacks = [ToolLoggingCallbackHandler()]
        response = await self.agent.ainvoke(
            {"messages": [("user", message)]},
            config={"callbacks": callbacks}
        )
        content = response["messages"][-1].content
        if isinstance(content, list):
            # Join text parts if it's a multi-part message (common with some models)
            text_parts = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            return "".join(text_parts)
        return str(content or "")

    async def close(self):
        """Close the MCP client connection."""
        if self.client:
            # MultiServerMCPClient might not have an explicit close in some versions, 
            # but we should handle cleanup if possible.
            self.client = None
            self.agent = None

async def main():
    # Pre-connection check: ensure required Neo4j credentials are in the environment
    if not os.getenv("NEO4J_MODEL_DB_PASSWORD"):
        print("ERROR: NEO4J_MODEL_DB_PASSWORD not found in environment.")
        return

    client = Onto2AIClient()
    await client.connect()
    
    print("\n=== Available Tools ===")
    for tool in client.tools:
        print(f"- {tool.name}: {tool.description.split('.')[0]}")
    
    print("\nOnto2AI Client Ready. Sending test query...")
    message = "Get the materialized schema for the 'person' class."
    response = await client.chat(message)
    
    print("\n=== AI Response ===")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
