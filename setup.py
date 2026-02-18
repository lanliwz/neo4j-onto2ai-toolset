from setuptools import setup, find_packages

setup(
    name="onto2ai-toolset",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "neo4j",
        "langchain",
        "langgraph",
        "pyyaml",
        "python-dotenv"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "onto2ai-client=neo4j_onto2ai_toolset.onto2ai_client:cli_main",
            "onto2ai-mcp=neo4j_onto2ai_toolset.onto2ai_mcp:cli_main"
        ],
    },
    author="Wei Zhang",
    author_email="zhang.wei.ny@gmail.com",
    description="Onto2AI toolset for ontology-driven modeling with Neo4j and MCP",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lanliwz/onto2ai-toolset",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
