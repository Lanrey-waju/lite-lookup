import os

from groq import Groq, GroqError, APIConnectionError

ConnectionError = APIConnectionError

try:
    client = Groq(api_key=os.environ.get("GROQ_KEY"))
except GroqError:
    print("Ensure the API key is set and valid")
