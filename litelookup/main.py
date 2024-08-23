import argparse
from litelookup.log import logger
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
    parser.add_argument(
        "lookup",
        help="look an information up and print it out",
    )
    parser.add_argument("content", nargs="*")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()
    text = " ".join(args.content)
    return validate_input(text)


def validate_input(input: str) -> str:
    if not input:
        raise InvalidInputError(
            "Input cannot be empty. Please provide a concept to check"
        )
    if len(input) > 100:
        raise InputTooLongError("Text input too long. Consider shortening.")
    # ensuring text only contains numbers, letters and one hyphen between words
    if not re.fullmatch(r"[a-zA-Z0-9\s]+(-[a-zA-Z0-9]+)*", input):
        if re.search(r"[^a-zA-Z0-9\s-]", input):
            raise UnsupportedCharactersError(
                "Input contains unsupported characters. Please use only letters, numbers and hyphens."
            )
        if re.search(r"[-]{2,}", input):
            raise UnsupportedCharactersError(
                "Text cannot contain two or more hyphens together."
            )

    output = input.lower().strip()
    return output


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
        logger.info("fetching response...\n\n")
        response = generate_response(input)
        print(response)
        logger.info("Success")
    except (InvalidInputError, InputTooLongError, UnsupportedCharactersError) as e:
        logger.error(f"Invalid input: {e} ")
    except Exception as e:
        print(f"Unexoected error: {e}")


if __name__ == "__main__":
    main()
