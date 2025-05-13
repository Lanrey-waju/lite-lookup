import asyncio
import logging

import httpx
from groq import APIConnectionError

from .config.config import load_api_key, load_model
from .log.logging_config import setup_logging

GROQ_MODEL = load_model()
GROQ_API_KEY = load_api_key()
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


logger = logging.getLogger(__name__)
setup_logging()


async def async_groq_api_call(message: str, client: httpx.AsyncClient) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.get_secret_value()}",
        "Content-Type": "application/json",
    }
    data = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 400,
        "temperature": 0.7,
    }
    max_retries, retry_delay = 3, 1
    for attempt in range(max_retries):
        try:
            response = await client.post(
                GROQ_API_URL, headers=headers, json=data, timeout=15.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (httpx.ConnectError, httpx.TimeoutException, APIConnectionError) as e:
            if attempt == max_retries - 1:
                logger.error(f"Connection error occurred: {e}", exc_info=True)
            # Exponential backoff
            await asyncio.sleep(retry_delay * (2**attempt))
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay * (2**attempt))  # Exponential backoff
            else:
                raise  # Client errors should not be retried
    return "Sorry, there was a problem connecting to the server. Please try again"
