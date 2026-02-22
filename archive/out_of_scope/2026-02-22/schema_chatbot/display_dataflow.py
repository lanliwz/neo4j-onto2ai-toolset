import matplotlib.pyplot as plt
import io
from neo4j_onto2ai_toolset.schema_chatbot.chatbot import lg as mygraph
from neo4j_onto2ai_toolset.onto2ai_logger_config import logger as mylogger


def display():
    try:
        # Assuming mygraph.get_graph().draw_mermaid_png() returns binary PNG data
        binary_png = mygraph.get_graph().draw_mermaid_png()
        if not binary_png:
            raise ValueError("Received empty binary data from draw_mermaid_png()")

        image = plt.imread(io.BytesIO(binary_png))
        plt.imshow(image)
        plt.axis('off')  # Hide axes
        plt.show()

    except ValueError as ve:
        mylogger.error(f"ValueError: {ve}")

    except IOError as ioe:
        mylogger.error(f"IOError: Failed to read image data - {ioe}")

    except Exception as e:
        mylogger.error(f"Unexpected error in display(): {e}", exc_info=True)

def save_image(file_path="../resource/images/schema_chatbot_dataflow.png"):
    """
    Saves the generated graph as an image file.

    :param file_path: The file path where the image will be saved.
    """
    try:
        binary_png = mygraph.get_graph().draw_mermaid_png()
        if not binary_png:
            raise ValueError("Received empty binary data from draw_mermaid_png()")

        with open(file_path, "wb") as f:
            f.write(binary_png)

        mylogger.info(f"Graph image successfully saved to {file_path}")

    except ValueError as ve:
        mylogger.error(f"ValueError: {ve}")

    except IOError as ioe:
        mylogger.error(f"IOError: Failed to save image - {ioe}")

    except Exception as e:
        mylogger.error(f"Unexpected error in save_image(): {e}", exc_info=True)


# display()
save_image()

