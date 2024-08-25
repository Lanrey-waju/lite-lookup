import argparse
from litelookup import log
import re

import redis

from .llm import client, ConnectionError


class InvalidInputError(Exception):
    pass


class InputTooLongError(InvalidInputError):
    pass


class UnsupportedCharactersError(InvalidInputError):
    pass


r = redis.Redis()


def get_input() -> str:
    parser = argparse.ArgumentParser(
        prog="LiteLookup",
        description="""Fetches a beginner infornation about any concept you
        want to learn about right from the comfort of your command line""",
    )
    parser.add_argument("content", nargs="*")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()
    text = " ".join(args.content)
    return validate_input(text)


def validate_input(input: str) -> str:
    if not input or input == "":
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


def generate_response(concept) -> str:
    cached_response = r.get(concept)
    if cached_response:
        return cached_response.decode("utf-8")
    user_message = (
        user_message
    ) = f"""Provide a concise, beginner-friendly explanation of '{concept}' in 2-3 sentences. Include:
1. A clear definition
2. Its primary significance or use
3. One key fact or example (if relevant)

Begin your response immediately without any preamble.""
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


def main():
    try:
        input = get_input()
        log.logger.info("fetching response...\n\n")
        response = generate_response(input)
        print(response)
    except (InvalidInputError, InputTooLongError, UnsupportedCharactersError) as e:
        log.logger.error(f"Invalid input: {e} ")
    except Exception as e:
        print(f"Unexoected error: {e}")


if __name__ == "__main__":
    main()
