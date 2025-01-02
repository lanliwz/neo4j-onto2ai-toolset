from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import OpenAI


# Initialize LLM
llm = OpenAI(temperature=0)


# Custom function to extract a knowledge graph
def extract_knowledge_graph(texts, llm):
    knowledge_graphs = []
    for text in texts:
        # Define a prompt to extract entities and relationships
        prompt = f"""
        Extract entities and their relationships from the following text as a knowledge graph. 
        Format the output as a list of triples (entity1, relationship, entity2):

        Text: {text}
        """
        response = llm(prompt)
        knowledge_graphs.append(response)
    return knowledge_graphs

def ask_question(knowledge_graphs, question, llm):
    # Combine knowledge graphs into a single prompt
    graph_text = "\n".join(knowledge_graphs)
    prompt = f"""
    Use the following knowledge graph to answer the question:

    Knowledge Graph:
    {graph_text}

    Question: {question}

    Answer:
    """
    response = llm(prompt)
    return response

# Sample text to process
texts = [
    """Sarah is an employee at prismaticAI, a leading technology company based in Westside Valley. 
    She has been working there for the past three years as a software engineer.
    Michael is also an employee at prismaticAI, where he works as a data scientist."""
]
# Process texts and extract knowledge graphs
knowledge_graphs = extract_knowledge_graph(texts, llm)

# Print the results
for idx, graph in enumerate(knowledge_graphs, 1):
    print(f"Knowledge Graph {idx}:\n{graph}\n")

# Ask questions based on the knowledge graph
# Does Michael work for the same company as Sarah?
# Who works for prismaticAI?
while True:

    question = input("Enter your question (or type 'exit' to quit): ")
    if question.lower() == 'exit':
        break
    answer = ask_question(knowledge_graphs, question, llm)
    print(f"Answer: {answer}\n")