from langchain_google_vertexai import VertexAI


# Initialize LangChain with Vertex AI
llm = VertexAI(
    model="gemini-1.5-pro",       # Specify the model (e.g., "text-bison" for text generation)
    temperature=0.7,          # Optional: Set model parameters
    max_output_tokens=256,    # Optional: Limit the output size
    top_k=40,                 # Optional: Number of top-k probabilities to consider
    top_p=0.95                # Optional: Cumulative probability threshold

)

# Use the LLM
# response = llm.invoke("Explain the concept of LangChain and Vertex AI integration.")
# print(response)