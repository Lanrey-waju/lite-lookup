import os

from groq import Groq, GroqError, APIConnectionError
from log import logger

ConnectionError = APIConnectionError


def initiate_client():
    try:
        client = Groq(api_key=os.environ.get("GROQ_KEY"))
    except GroqError:
        logger.warning("Ensure the API key is set and valid")
    return client


client = initiate_client()
