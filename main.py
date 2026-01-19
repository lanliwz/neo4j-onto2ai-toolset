import asyncio
from neo4j_onto2ai_toolset.schema_chatbot.chatbot import graph_app

async def main():
    print("--- Neo4j Onto2Schema Chatbot ---")
    # Note: input() is blocking, but in a local CLI script it's expected.
    # In an agent environment, we might prefer a hardcoded question or argument.
    # However, to satisfy 'execute chatbot', we make it interactive for the user.
    question = input("What is your schema/ontology question? ")
    input_data = {"question": question}
    
    result = await graph_app.ainvoke(input_data)
    
    print("\n--- Result ---")
    if "database_records" in result:
        print(f"Outcome: {result['database_records']}")
    if "cypher_statement" in result and result["cypher_statement"]:
        print(f"Generated Code:\n{result['cypher_statement']}")
    print(f"Steps taken: {result.get('steps', [])}")

if __name__ == "__main__":
    asyncio.run(main())