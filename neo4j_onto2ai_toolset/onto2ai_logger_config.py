import logging
import os
from dotenv import load_dotenv

# Find project root (one level up from this file's directory: neo4j_onto2ai_toolset/)
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
dotenv_path = os.path.join(project_root, '.env')

# Explicitly log where we are looking for .env (to stderr)
import sys
# print(f"DEBUG: current_dir={current_dir}", file=sys.stderr)
# print(f"DEBUG: project_root={project_root}", file=sys.stderr)
# print(f"DEBUG: dotenv_path={dotenv_path}", file=sys.stderr)

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
    # print(f"DEBUG: Loaded .env from {dotenv_path}", file=sys.stderr)
else:
    load_dotenv() # Fallback to default
    # print("DEBUG: .env NOT FOUND at path, using default load_dotenv()", file=sys.stderr)

MY_LOG_LEVEL = os.getenv('MY_LOG_LEVEL', 'INFO')
NEO4J_LOG_LEVEL = os.getenv('NEO4J_LOG_LEVEL', 'INFO')

neo4j_logger = logging.getLogger("neo4j")
neo4j_logger.setLevel(NEO4J_LOG_LEVEL)

logger = logging.getLogger("onto2ai-toolset")  # Use project name as the root logger
logger.setLevel(MY_LOG_LEVEL)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler
logger.addHandler(console_handler)

logger.info(f"My Logger Level: {MY_LOG_LEVEL}")
logger.info(f"Neo4j Logger Level: {NEO4J_LOG_LEVEL}")
logger.info(f"Neo4j Model DB Name: {os.getenv('NEO4J_MODEL_DB_NAME')}")
logger.info(f"Neo4j TAX DB Name: {os.getenv('NEO4J_TAX62N_DB_NAME')}")
logger.info(f"Neo4j RDF DB Name: {os.getenv('NEO4J_RDF_DB_NAME')}")
logger.info(f"LLM Model Name (canonical): {os.getenv('LLM_MODEL_NAME')}")
logger.info(f"LLM GPT Model Name: {os.getenv('GPT_MODEL_NAME')}")
logger.info(f"LLM Model Reasoning Effort: {os.getenv('GPT_REASONING_EFFORT')}")

# logger.info("Logging is set up neo4j-onto2ai-toolset")
