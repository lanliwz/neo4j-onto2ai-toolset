from pathlib import Path

from setuptools import find_packages, setup


PACKAGES = find_packages(exclude=["onto2ai_entitlement*", "onto2ai_parcel*"]) + [
    "onto2ai_modeller.static",
    "onto2ai_modeller.static.css",
    "onto2ai_modeller.static.js",
]

setup(
    name="onto2ai-engineer",
    version="1.1.0",
    packages=PACKAGES,
    install_requires=[
        "fastapi",
        "jinja2",
        "langchain>=0.3.27",
        "langchain-community>=0.3.27",
        "langchain-core>=0.3.15",
        "langchain-google-genai",
        "langchain-mcp-adapters",
        "langchain-neo4j",
        "langchain-openai",
        "langgraph>=0.3.27",
        "langgraph-prebuilt>=0.0.8",
        "mcp",
        "neo4j==5.28.1",
        "pydantic>=2",
        "pyyaml",
        "python-dotenv",
        "rdflib",
        "rdflib-neo4j",
        "typing-extensions",
        "uvicorn",
    ],
    include_package_data=True,
    package_data={
        "onto2ai_modeller": ["config.yaml", "static/*", "static/**/*"],
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
    description="Onto2AI Toolset for ontology-driven modeling with Neo4j and MCP",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    url="https://github.com/lanliwz/neo4j-onto2ai-toolset",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
