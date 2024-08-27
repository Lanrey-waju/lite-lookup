import os
import sys

import httpx
from dotenv import load_dotenv

from groq import Groq, GroqError, APIConnectionError
from litelookup.log import logger

ConnectionError = APIConnectionError

load_dotenv()


def initiate_client():
    try:
        persistent_client = httpx.Client()
        client = Groq(api_key=os.getenv("GROQ_API_KEY"), http_client=persistent_client)
    except GroqError:
        logger.warning("Ensure the API key is set and valid")
        sys.exit(1)

    return client


client = initiate_client()
