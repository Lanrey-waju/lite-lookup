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
        user_message = f"""Provide a concise, beginner-friendly explanation of '{concept}' in 3-4 sentences. Include:
    1. A clear definition
    2. Its primary significance or use
    3. One key fact or example (if relevant)

    Begin your response immediately without any preamble. Do not hallucinate.
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
        user_message = f""""Provide a detailed, beginner-friendly explanation of '{concept}' in 5-6 sentences. Include:
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
        user_message = f"""Provide a concise, practical explanation of the programming concept '{concept}' in 4-6 sentences. Include:
    1. A clear, technical definition
    2. Its primary use case or significance in programming
    3. A brief, illustrative code example (if applicable)
    4. One common pitfall or best practice

    Begin your response immediately without any preamble. Focus on practical application. Separate code examples from body of text. If relevant, mention the programming language(s) where this concept is most commonly used.
    Be direct and concise. Do not hallucinate.
    """
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
        user_message = f""""Provide a crisp, 1-2 sentence response that directly answers the query: {concept}. Do not include any additional explanation or context - just the essential information needed to address the request."
    """
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
