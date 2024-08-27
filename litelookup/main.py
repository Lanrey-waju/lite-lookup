import argparse
import re
import os
import time

from rich.padding import Padding
from rich import print
import redis
import httpx
from dotenv import load_dotenv

from .llm import client, ConnectionError
from litelookup import log


class InvalidInputError(Exception):
    pass


class InputTooLongError(InvalidInputError):
    pass


class UnsupportedCharactersError(InvalidInputError):
    pass


r = redis.Redis()
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def get_input() -> tuple[str, bool, bool]:
    parser = argparse.ArgumentParser(
        prog="LiteLookup",
        description="""Fetches a beginner infornation about any concept you
        want to learn about right from the comfort of your command line""",
    )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("content", nargs="*")
    group.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="provides a detailed accessible information on the arguments passed",
    )
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Enters a shell session for faster lookups",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()
    text = " ".join(args.content)
    return validate_input(text, args.interactive), args.verbose, args.interactive


def validate_input(input: str, interactive: bool) -> str:
    if not interactive and not input:
        raise InvalidInputError(
            "Input cannot be empty. Please provide a concept to check"
        )

    if len(input) > 100:
        raise InputTooLongError("Text input too long. Consider shortening.")

    # Validate content inside the quotes
    if not re.fullmatch(r"[a-zA-Z0-9\s.,';:!?-]+", input):
        raise UnsupportedCharactersError(
            "Input contains unsupported characters. Please use only letters, numbers, spaces, hyphens, and basic punctuation."
        )
    # Input cannot contain two or more hyphens together
    if re.search(r"[-]{2,}", input):
        raise UnsupportedCharactersError(
            "Text cannot contain two or more hyphens together."
        )

    # preserve words that are ALL CAPS
    if input.isupper() or input.islower():
        return input.strip()

    return input.lower().strip()


def generate_response(concept: str) -> str:
    cached_response = r.get(concept)
    if cached_response:
        return cached_response.decode("utf-8")
    user_message = (
        user_message
    ) = f"""Provide a concise, beginner-friendly explanation of '{concept}' in 2-3 sentences. Include:
1. A clear definition
2. Its primary significance or use
3. One key fact or example (if relevant)

Begin your response immediately without any preamble. Do not hallucinate.""
"""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        r.set(concept, response, ex=3600)
        return response
    except ConnectionError:
        return "Error connecting to server. Check your connection and retry"


def generate_verbose_response(concept) -> str:
    cached_response = r.get(concept)
    if cached_response:
        return cached_response.decode("utf-8")
    user_message = (
        user_message
    ) = f""""Provide a detailed, beginner-friendly explanation of '{concept}' in 4-6 sentences. Include:
1. A clear definition
2. Its primary significance or use
3. Two key facts or examples
4. Common pitfalls or best practices (if applicable)

If this is a programming-related concept, please include a brief, illustrative code example.

Begin your response immediately without any preamble. Ensure the explanation remains accessible to beginners while providing more depth than a basic description. Do not hallucinate."""
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content
        r.set(concept, response, ex=3600)
        return response
    except ConnectionError:
        return "Error connecting to server. Check your connection and retry"


def groq_api_call(message: str, client: httpx.Client) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "text/plain",
    }
    data = {
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": message}],
        "max_tokens": 100,
        "temperature": 0.7,
    }

    max_retries, retry_delay = 3, 1
    for attempt in range(max_retries):
        try:
            response = client.post(
                GROQ_API_URL, headers=headers, json=data, timeout=10.0
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except (httpx.ConnectError, httpx.TimeoutException):
            if attempt == max_retries - 1:
                raise
            time.sleep(retry_delay * (2**attempt))  # Exponential backoff
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay * (2**attempt))  # Exponential backoff
            else:
                raise  # Client errors should not be retried


def interactive_session(interactive: bool):
    # Set up connection pool
    with httpx.Client(
        http2=True, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    ) as client:
        # Set up Redis connection
        redis_client = redis.Redis(host="localhost", port=6379, db=0)

        while True:
            user_input = input(
                "Enter a concept to lookup (or 'quit' to exit): "
            ).strip()
            text = validate_input(user_input, interactive)

            if not interactive:
                print("Exiting LiteLookup. Goodbye!")
                break

            if text:
                response = generate_response_interactive(text, client, redis_client)
                print(response)
                # if interactive:
                #     print(f"Verbose info: Lookup performed for '{text}'")
            else:
                print("Please enter a valid concept.")


def generate_response_interactive(
    concept: str, client: httpx.Client, redis_client: redis.Redis
):
    cached_response = redis_client.get(concept)
    if cached_response:
        return cached_response.decode("utf-8")

    user_message = f"""Provide a concise, beginner-friendly explanation of '{concept}' in 3-4 sentences. Include:
1. A clear definition
2. Its primary significance or use
3. One key fact or example (if relevant)

Begin your response immediately without any preamble. Do not hallucinate.""
"""
    response = groq_api_call(user_message, client)
    redis_client.set(concept, response, ex=3600)

    return response


def main():
    try:
        input, verbosity, interactivity = get_input()
        if verbosity:
            log.logger.info("fetching verbose response...\n\n")
            response = generate_verbose_response(input)
            output = Padding(response, (1, 1), style="magenta", expand=False)
            print(output)
        elif interactivity:
            log.logger.info("fetching response...\n\n")
            log.logger.info("Switching to interactive mode...\n")
            interactive_session(interactivity)
        else:
            log.logger.info("fetching response...\n\n")
            response = generate_response(input)
            output = Padding(response, (1, 1), style="magenta", expand=False)
            print(output)
    except (InvalidInputError, InputTooLongError, UnsupportedCharactersError) as e:
        log.logger.error(f"Invalid input: {e} ")
    except Exception as e:
        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
