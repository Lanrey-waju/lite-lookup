import logging

import httpx
import redis.asyncio as redis

from .llm import async_groq_api_call
from .log.logging_config import setup_logging

logger = logging.getLogger(__name__)
setup_logging()


async def generate_response(
    concept: str, client: httpx.AsyncClient, redis_client: redis.Redis
) -> str:
    try:
        cached_response = await redis_client.get(concept)
        if cached_response:
            logger.info("Got a cached response\n")
            return cached_response.decode("utf-8")

        user_message = f"""Provide a concise, valuable, beginner-friendly response to the query: '{concept}'
        Your response should:
        1. Directly address the main point
        2. Offer key information or steps if applicable
        3. Be immediately useful without unnecessary background

        Adapt your response style to the query type (definition, process, comparison, etc.).
        Aim for clarity and brevity. Avoid speculation.

        Begin your response immediately without preamble.
        """
        response = await async_groq_api_call(user_message, client)

        try:
            await redis_client.set(concept, response, ex=3600)
            return response
        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            return "An error occured wjile retrieving query. Please try again"
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        return "An error occured wjile retrieving query. Please try again"
    except Exception as e:
        logger.error(f"An unexpected error occured: {e}.")
        return "An unexpected error occured. Check your connection and retry"


async def generate_programming_response(
    concept: str, client: httpx.AsyncClient, redis_client: redis.Redis
) -> str:
    try:
        cached_response = await redis_client.get(concept + "_p")  # Correct
        if cached_response:
            logger.info("Got a cached response\n")
            return cached_response.decode("utf-8")
        user_message = f"""Provide a concise yet comprehensive answer to the following programming question: '{concept}'
        Guidelines:
        1. Begin with the most relevant information directly addressing the question.
        2. Offer a brief technical explanation (2-3 sentences).
        3. List key points using numbers, covering:
           a. Basic concept or implementation
           b. Common variations or options
           c. Use cases or best practices
        4. Include short, relevant code examples where applicable.
        5. Mention a best practice or common pitfall if relevant.
        Use Markdown for code blocks. Be direct and avoid unnecessary preambles, question repetition, or filler phrases. Focus solely on the specific information requested.
        """
        response = await async_groq_api_call(user_message, client)
        if response is None:
            return (
                "Sorry, there was a problem connecting to the server. Please try again"
            )
        try:
            await redis_client.set(concept + "_p", response, ex=3600)
            return response
        except redis.RedisError as e:
            logger.error(f"Failed to cache response: {e}")
            return "An error occured wjile retrieving query. Please try again"
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        return "An error occured wjile retrieving query. Please try again"
    except Exception as e:
        logger.error(f"An unexpected error occured: {e}.")
        return "An unexpected error occured. Check your connection and retry"


async def generate_nofluff_response(
    concept: str, client: httpx.AsyncClient, redis_client: redis.Redis
) -> str:
    try:
        cached_response = await redis_client.get(concept + "_d")
        if cached_response:
            logger.info("Got a cached response\n")
            return cached_response.decode("utf-8")
        user_message = f"""Directly answer "{concept}" in 1-2 crisp sentences. Include only essential information. Adapt to query type (definition, step, fact, etc.) without explanation."""
        response = await async_groq_api_call(user_message, client)

        try:
            await redis_client.set(concept + "_d", response, ex=3600)
            return response
        except redis.RedisError as e:
            logger.error(f"Redis error: {e}")
            return "An error occured wjile retrieving query. Please try again"
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        return "An error occured wjile retrieving query. Please try again"
    except Exception as e:
        logger.error(f"An unexpected error occured: {e}.")
        return "An unexpected error occured. Check your connection and retry"
