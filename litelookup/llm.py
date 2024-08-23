import os
import sys

from dotenv import load_dotenv

from groq import Groq, GroqError, APIConnectionError
from log import logger

ConnectionError = APIConnectionError

load_dotenv()


def initiate_client():
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    except GroqError:
        logger.warning("Ensure the API key is set and valid")
        sys.exit(1)

    return client


client = initiate_client()
