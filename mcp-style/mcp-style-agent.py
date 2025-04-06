from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType, Tool
from langchain.memory import ConversationBufferMemory


# Step 1: Define Tools — Like MCP Tool Registry
def get_weather(location: str) -> str:
    """Get weather for a given location."""
    return f"🌤️ Simulated sunny weather in {location}"

def summarize_text(text: str) -> str:
    """Summarize the provided text."""
    return f"Summary: {text[:50]}..."

tools = [
    Tool(
        name="get_weather",
        func=get_weather,
        description="Get weather for a given location. Input: a city name."
    ),
    Tool(
        name="summarize_text",
        func=summarize_text,
        description="Summarize the provided text. Input: a long string of text."
    ),
]

# Step 2: Create memory for persistent context — Like MCP Context State
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# Step 3: Initialize the LLM
llm = ChatOpenAI(temperature=0)

# Step 4: Build the agent with memory and tools
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
    memory=memory,
    verbose=True,
)

# Step 5: Run an example task
response = agent.run(
    "Check the weather in San Francisco and summarize this: 'LangChain makes working with LLMs much easier by abstracting common tasks and allowing flexible chaining of steps.'"
)

print("\n🔁 Agent Response:\n", response)