import asyncio
import argparse
import json
import os
import sys

from langchain.agents import create_agent
from langchain_core.callbacks import BaseCallbackHandler
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

class ToolLoggingCallbackHandler(BaseCallbackHandler):
    """Callback handler for logging tool usage."""
    def on_tool_start(self, serialized: dict, input_str: str, **kwargs) -> None:
        tool_name = serialized.get("name", "Unknown Tool")
        print(f"\n[MCP TOOL CALL] {tool_name}")
        print(f"   Input: {input_str}")

class Onto2AIClient:
    """
    Client for interacting with the Onto2AI MCP server.
    Handles tool discovery and agent creation.
    """
    
    def __init__(self, model_name: str = None, *, log_tools: bool = True):
        self.model_name = model_name or os.getenv("LLM_MODEL_NAME", "gemini-3.5-flash")
        self.log_tools = log_tools
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

    async def chat(self, message: str) -> dict:
        """
        Send a message to the agent and get a response.
        Returns a dict with 'response' (text) and optional 'data_model' (dict).
        """
        if not self.agent:
            await self.connect()
        
        callbacks = [ToolLoggingCallbackHandler()] if self.log_tools else []
        response = await self.agent.ainvoke(
            {"messages": [("user", message)]},
            config={"callbacks": callbacks}
        )
        
        # 1. Extract the final text response
        last_message = response["messages"][-1]
        content = last_message.content
        text_response = ""
        
        if isinstance(content, list):
            # Join text parts if it's a multi-part message
            text_parts = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                elif isinstance(part, dict) and part.get("type") == "text":
                    text_parts.append(part.get("text", ""))
            text_response = "".join(text_parts)
        else:
            text_response = str(content or "")
            
        # 2. Extract DataModel if any tool called it
        data_model = None
        # Iterate backwards to find the latest tool output
        for msg in reversed(response["messages"]):
            # More robust check: look for specific tool output
            if getattr(msg, "name", None) == "extract_data_model" or \
               (hasattr(msg, "tool_call_id") and getattr(msg, "name", None) == "onto2ai:extract_data_model"):
                try:
                    raw_content = msg.content
                    
                    if isinstance(raw_content, str):
                        data_model = json.loads(raw_content)
                    elif isinstance(raw_content, dict):
                        data_model = raw_content
                    elif isinstance(raw_content, list):
                        # MCP often returns a list of blocks
                        for block in raw_content:
                            if isinstance(block, dict) and block.get("type") == "text":
                                try:
                                    data_model = json.loads(block.get("text", "{}"))
                                    break
                                except:
                                    continue
                            elif isinstance(block, str):
                                try:
                                    data_model = json.loads(block)
                                    break
                                except:
                                    continue
                    break
                except Exception:
                    continue

        return {
            "response": text_response,
            "data_model": data_model
        }

    async def close(self):
        """Close the MCP client connection."""
        if self.client:
            # MultiServerMCPClient might not have an explicit close in some versions, 
            # but we should handle cleanup if possible.
            self.client = None
            self.agent = None

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Onto2AI ontology workbench client.")
    parser.add_argument(
        "--message",
        "-m",
        help="Run one ontology workbench prompt and exit.",
    )
    parser.add_argument(
        "--model",
        help="LLM model to use. Defaults to LLM_MODEL_NAME or gemini-3.5-flash.",
    )
    parser.add_argument(
        "--quiet-tools",
        action="store_true",
        help="Do not print MCP tool-call traces.",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List available MCP tools and exit.",
    )
    return parser.parse_args()


async def main():
    args = parse_args()

    # Pre-connection check: ensure required Neo4j credentials are in the environment
    if not os.getenv("NEO4J_MODEL_DB_PASSWORD"):
        print("ERROR: NEO4J_MODEL_DB_PASSWORD not found in environment.")
        return

    client = Onto2AIClient(model_name=args.model, log_tools=not args.quiet_tools)
    await client.connect()
    
    print("\n=== Available Tools ===")
    for tool in client.tools:
        print(f"- {tool.name}: {tool.description.split('.')[0]}")

    if args.list_tools:
        await client.close()
        return

    if args.message:
        response = await client.chat(args.message)
        print("\n=== AI Response ===")
        print(response["response"])
        if response.get("data_model"):
            print("\n=== Data Model ===")
            print(json.dumps(response["data_model"], indent=2))
        await client.close()
        return
    
    print("\nOnto2AI Client Ready. Type a question, or 'exit' to quit.")
    while True:
        try:
            message = input("\nonto2ai> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not message:
            continue
        if message.lower() in {"exit", "quit", ":q"}:
            break
        response = await client.chat(message)
        print("\n" + response["response"])
        if response.get("data_model"):
            print("\nData model returned. Use --message for JSON output in one-shot mode.")

    await client.close()

def cli_main():
    """Synchronous CLI entrypoint for console_scripts."""
    asyncio.run(main())

if __name__ == "__main__":
    cli_main()
