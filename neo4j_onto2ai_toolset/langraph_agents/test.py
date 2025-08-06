from langgraph.graph import StateGraph
from langchain.chat_models import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import TypedDict, Optional

# 1. Tools
@tool
def multiply(x: int, y: int) -> int:
    """Multiply two integers"""
    return x * y

@tool
def echo(text: str) -> str:
    """Echo the input text"""
    return f"You said: {text}"

tools = [multiply, echo]

# 2. Prompt for the agent
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Use tools if needed."),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 3. ChatOpenAI (no bind_tools)
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 4. Create tool-using agent
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

# 5. LangGraph state
class AgentState(TypedDict):
    input: str
    output: Optional[str]

# 6. LangGraph node logic
def run_agent(state: AgentState) -> AgentState:
    result = agent.invoke({"input": state["input"]})
    return {"input": state["input"], "output": result}

# 7. Build LangGraph
builder = StateGraph(AgentState)
builder.add_node("agent", run_agent)
builder.set_entry_point("agent")
builder.set_finish_point("agent")
graph = builder.compile()

# 8. Test
result = graph.invoke({"input": "multiply 6 and 7"})
print("Final output:", result["output"])