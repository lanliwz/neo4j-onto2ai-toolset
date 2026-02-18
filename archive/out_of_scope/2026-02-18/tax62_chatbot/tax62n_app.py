import streamlit as st
import asyncio
import uuid
from langchain_core.messages import HumanMessage, AIMessage
from tax62_chatbot.tax62n_graph import tax_chatbot_graph

# --- Page Configuration ---
st.set_page_config(
    page_title="Tax62-N Chatbot",
    page_icon="💰",
    layout="wide"
)

# --- Custom Styling ---
st.markdown("""
<style>
    .stChatFloatingInputContainer {
        padding-bottom: 2rem;
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .main {
        background-color: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background-color: #343a40;
        color: white;
    }
    h1 {
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# --- Sidebar ---
with st.sidebar:
    st.title("💰 Tax62-N Advisor")
    st.markdown("---")
    st.info("I can help you analyze tax bills, account balances, and payment history.")
    
    if st.button("Reset Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()
    
    st.markdown("---")
    st.subheader("Debug Info")
    st.write(f"Thread ID: `{st.session_state.thread_id}`")

# --- Main Interface ---
st.title("Tax & Payment Intelligent Assistant")
st.caption("Powered by Neo4j & LangGraph 1.2")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "cypher" in message and message["cypher"]:
            with st.expander("Show Generated Cypher"):
                st.code(message["cypher"], language="cypher")

# Chat input
if prompt := st.chat_input("Ask about tax bills or payments..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        status_placeholder = st.empty()
        
        async def get_response():
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            final_content = ""
            final_cypher = ""
            
            async for event in tax_chatbot_graph.astream(
                {"messages": [HumanMessage(content=prompt)]}, 
                config, 
                stream_mode="values"
            ):
                if "messages" in event:
                    last_msg = event["messages"][-1]
                    if isinstance(last_msg, AIMessage):
                        final_content = last_msg.content
                        response_placeholder.markdown(final_content)
                
                # Check for intermediate values in state
                curr_state = await tax_chatbot_graph.aget_state(config)
                if curr_state.values.get("cypher_statement"):
                    final_cypher = curr_state.values["cypher_statement"]
            
            return final_content, final_cypher

        # Run the async graph
        with st.spinner("Analyzing data..."):
            ans, cypher = asyncio.run(get_response())
            
        # Update session state with assistant response
        st.session_state.messages.append({
            "role": "assistant", 
            "content": ans,
            "cypher": cypher
        })
        
        if cypher:
            with st.expander("Show Generated Cypher"):
                st.code(cypher, language="cypher")
