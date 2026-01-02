import requests
import os
from urllib.parse import urlparse
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logger = logging.getLogger(__name__)
ONTO_ROOT = os.getenv('ONTOLOGY_ROOT_PATH')
def get_rdf_data(url, ext='.rdf'):
    file_path = url_to_filepath(url,ext)
    if not os.path.exists(file_path):
        download_as_rdf(url)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        logger.error(f"The file '{file_path}' was not found.")
        return ""
    except IOError:
        logger.exception(f"An error occurred while reading the file '{file_path}'.")
        return ""

def url_to_filepath(url, ext = '.rdf'):
    parsed_url = urlparse(url)

    # Replace '.' in the domain with '_'
    domain = ONTO_ROOT + parsed_url.netloc.replace('.', '_')

    # Use the path and filename from the URL as the file path
    path = parsed_url.path.strip('/')
    if path.endswith('/'):
        path = path.rstrip('/')  # Remove the trailing '/'

    # Extract the last part of the path for the filename
    if '/' in path:
        *dirs, filename = path.split('/')
        path = os.path.join(*dirs, filename + ext)
    else:
        filename = path

    # Construct the save path
    save_path = os.path.join(domain, path or filename)

    return save_path

def download_as_rdf(url):
    # Parse the URL
    save_path = url_to_filepath(url)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    # Fetch and save the content
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we got a successful response
        with open(save_path, 'wb') as file:
            file.write(response.content)
        logger.info(f"Content saved to {save_path}")
    except requests.RequestException as e:
        logger.error(f"Failed to retrieve the URL: {e}")


# print(get_rdf_data('https://spec.edmcouncil.org/fibo/ontology/master/latest/FND/AgentsAndPeople/Agents/'))