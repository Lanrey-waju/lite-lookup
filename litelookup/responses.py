import redis
import httpx
import logging
from log.logging_config import setup_logging

from litelookup.llm import groq_api_call

logger = logging.getLogger(__name__)
setup_logging()


def generate_response(
    concept: str, client: httpx.Client, redis_client: redis.Redis
) -> str:
    try:
        cached_response = redis_client.get(concept)
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
        response = groq_api_call(user_message, client)
        if response is None:
            return (
                "Sorry, there was a problem connecting to the server. Please try again"
            )
        try:
            redis_client.set(concept, response, ex=3600)
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


def generate_verbose_response(
    concept: str, client: httpx.Client, redis_client: redis.Redis
) -> str:
    try:
        cached_response = redis_client.get(f"{concept}_v")
        if cached_response:
            logger.info("Got a cached response\n")
            return cached_response.decode("utf-8")
        user_message = f""""Provide a detailed, beginner-friendly explanation of the query: '{concept}' in 5-6 sentences. Include:
    1. A clear definition
    2. Its primary significance or use
    3. Two key facts or examples
    4. Common pitfalls or best practices (if applicable)

    Begin your response immediately without any preamble. Be direct and provide more depth than a basic description.
    Do not hallucinate.
    """
        response = groq_api_call(user_message, client)
        if response is None:
            return (
                "Sorry, there was a problem connecting to the server. Please try again"
            )
        try:
            redis_client.set(f"{concept}_v", response, ex=3600)
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


def generate_programming_response(
    concept: str, client: httpx.Client, redis_client: redis.Redis
) -> str:
    try:
        cached_response = redis_client.get(concept + "_p")  # Correct
        if cached_response:
            logger.info("Got a cached response\n")
            return cached_response.decode("utf-8")
        user_message = f"""Respond to query: '{concept}' in programming context:
        1. Technical definition (1-2 sentences)
        2. Primary use case (1 sentence)
        3. Code example with brief, clear explanation
        4. Key pitfall or best practice (1 sentence amd only if applicable)

        Always include code with explanation.
        If requested for specific info, focus solely on that.
        Use code blocks for examples. No preamble. Be concise yet comprehensive."""
        response = groq_api_call(user_message, client)
        if response is None:
            return (
                "Sorry, there was a problem connecting to the server. Please try again"
            )
        try:
            redis_client.set(concept + "_p", response, ex=3600)
            return response
        except redis.RedisError as e:
            logger.error(f"Failed to cache response: {e}")
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        return "An error occured wjile retrieving query. Please try again"
    except Exception as e:
        logger.error(f"An unexpected error occured: {e}.")
        return "An unexpected error occured. Check your connection and retry"


def generate_nofluff_response(
    concept: str, client: httpx.Client, redis_client: redis.Redis
) -> str:
    try:
        cached_response = redis_client.get(concept + "_d")
        if cached_response:
            logger.info("Got a cached response\n")
            return cached_response.decode("utf-8")
        user_message = f"""Directly answer "{concept}" in 1-2 crisp sentences. Include only essential information. Adapt to query type (definition, step, fact, etc.) without explanation."""
        response = groq_api_call(user_message, client)
        if response is None:
            return (
                "Sorry, there was a problem connecting to the server. Please try again"
            )
        try:
            redis_client.set(concept + "_d", response, ex=3600)
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
