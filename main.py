import argparse
import logging
import re

from llm import client, ConnectionError

logger = logging.getLogger(__name__)


class InvalidInputError(Exception):
    pass


class InputTooLongError(InvalidInputError):
    pass


class Unsupportedcharacterserror(InvalidInputError):
    pass


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
    # ensuring text only contains numbers, letters and hyphen
    if not re.match(r"[a-zA-Z0-9\-\s]+", input):
        raise ValueError(
            "Input contains unsupported characters. Please use only letters and numbers"
        )
    if re.match(r"[\-]{2,}", input):
        raise Unsupportedcharacterserror(
            "Text cannot contain two or more hyphens together."
        )

    output = input.lower().strip()
    return output


def generate_response(concept) -> str:
    user_message = f"""
Return a very concise information about the concept that I will provide
you with. It should generally be like the most important information
about the concept and should be enough to at least educate someone that
has never heard the concept before. You do not need to add
any preamble. Just provide the information from the first line.
The concept is {concept}.
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
        return chat_completion.choices[0].message.content
    except ConnectionError:
        return "Error connecting to server. Check your connection and retry"


def main():
    try:
        input = get_input()
        response = generate_response(input)
        print(response)
    except (InvalidInputError, InputTooLongError, Unsupportedcharacterserror) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexoected error: {e}")


main()
