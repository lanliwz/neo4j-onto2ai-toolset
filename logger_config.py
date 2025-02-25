import logging
import os
from dotenv import load_dotenv

load_dotenv()
MY_LOG_LEVEL = os.getenv('MY_LOG_LEVEL')
NEO4J_LOG_LEVEL = os.getenv('NEO4J_LOG_LEVEL')

logging.getLogger("neo4j").setLevel(NEO4J_LOG_LEVEL)

logger = logging.getLogger("neo4j-onto2ai-toolset")  # Use project name as the root logger
# default log level as INFO
logger.setLevel(MY_LOG_LEVEL)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler
logger.addHandler(console_handler)

# logger.info("Logging is set up neo4j-onto2ai-toolset")