from setuptools import setup, find_packages

setup(
    name="onto2ai-engineer",
    version="0.7.0",
    packages=find_packages(),
    install_requires=[
        "neo4j",
        "langchain",
        "langgraph",
        "pyyaml",
        "python-dotenv",
        "fastapi",
        "uvicorn",
        "jinja2",
    ],
    include_package_data=True,
    package_data={
        "onto2ai_modeller": ["static/*", "static/**/*"],
        "onto2ai_entitlement": [
            "ontology/*.rdf",
            "staging/*.json",
            "staging/*.py",
            "staging/*.md",
            "staging/*.cypher",
        ],
    },
    entry_points={
        "console_scripts": [
            "onto2ai-client=neo4j_onto2ai_toolset.onto2ai_client:cli_main",
            "onto2ai-mcp=neo4j_onto2ai_toolset.onto2ai_mcp:cli_main",
            "onto2ai-modeller=onto2ai_modeller.main:cli_main",
        ],
    },
    author="Wei Zhang",
    author_email="zhang.wei.ny@gmail.com",
    description="Onto2AI Engineer for ontology-driven modeling with Neo4j and MCP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lanliwz/onto2ai-engineer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
