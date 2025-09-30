# __init__.py in neo4j_onto2ai_toolset/schema_chatbot/
# This file makes the directory a package

# You can import chatbot functions here if needed

# setup.py
from setuptools import setup, find_packages

setup(
    name="neo4j-onto2ai-toolset",
    version="0.2.0",
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
            "neo4j-chatbot=neo4j_onto2ai_toolset.schema_chatbot.chatbot:main"
        ],
    },
    author="Wei Zhang",
    author_email="zhang.wei.ny@gmail.com",
    description="A toolset for integrating Neo4j with AI-driven ontology processing",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/lanliwz/neo4j-onto2ai-toolset",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)