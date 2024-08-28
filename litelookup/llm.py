import os
import time

import httpx
from dotenv import load_dotenv

from groq import APIConnectionError

ConnectionError = APIConnectionError

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def groq_api_call(message: str, client: httpx.Client) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 300,
        "temperature": 0.7,
    }

    max_retries, retry_delay = 3, 1
    for attempt in range(max_retries):
        try:
            response = client.post(
                GROQ_API_URL, headers=headers, json=data, timeout=15.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (httpx.ConnectError, httpx.TimeoutException):
            if attempt == max_retries - 1:
                raise
            # Exponential backoff
            time.sleep(retry_delay * (2**attempt))
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay * (2**attempt))  # Exponential backoff
            else:
                raise  # Client errors should not be retried
