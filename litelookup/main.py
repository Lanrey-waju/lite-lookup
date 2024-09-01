import argparse
import re

import redis
import httpx
from rich.padding import Padding
from rich import print
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from .llm import groq_api_call, ConnectionError
from litelookup import log


class InvalidInputError(Exception):
    pass


class InputTooLongError(InvalidInputError):
    pass


class UnsupportedCharactersError(InvalidInputError):
    pass


def get_input() -> tuple[str, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="LiteLookup",
        description="""Fetches a beginner infornation about any concept you
        want to learn about right from the comfort of your command line""",
    )
    parser.add_argument("content", nargs="*")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="provides a detailed accessible information on the arguments passed",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Enters a shell session for faster lookups",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.8")

    parser.add_argument(
        "-p",
        "--programming",
        action="store_true",
        help="optimize response for programming concepts",
    )
    args = parser.parse_args()

    if args.interactive and not args.content:
        return "", args

    text = " ".join(args.content)
    return validate_input(text, args.interactive), args


def validate_input(input: str, interactive: bool) -> str:
    if not interactive and not input:
        raise InvalidInputError(
            "Input cannot be empty. Please provide a concept to check"
        )

    if len(input) > 100:
        raise InputTooLongError("Text input too long. Consider shortening.")

    # Validate content inside the quotes
    if not re.fullmatch(r"[a-zA-Z0-9\s.,\")(q';:!?-]+", input):
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


def generate_response(
    concept: str, client: httpx.Client, redis_client: redis.Redis
) -> str:
    cached_response = redis_client.get(concept)
    if cached_response:
        return cached_response.decode("utf-8")
    user_message = f"""Provide a concise, beginner-friendly explanation of '{concept}' in 3-4 sentences. Include:
1. A clear definition
2. Its primary significance or use
3. One key fact or example (if relevant)

Begin your response immediately without any preamble. Do not hallucinate.""
"""
    try:
        response = groq_api_call(user_message, client)
        redis_client.set(concept, response, ex=3600)
        return response
    except ConnectionError:
        return "Error connecting to server. Check your connection and retry"


def generate_verbose_response(
    concept: str, client: httpx.Client, redis_client: redis.Redis
) -> str:
    cached_response = redis_client.get(f"{concept}_v")
    if cached_response:
        return cached_response.decode("utf-8")
    user_message = f""""Provide a detailed, beginner-friendly explanation of '{concept}' in 5-6 sentences. Include:
1. A clear definition
2. Its primary significance or use
3. Two key facts or examples
4. Common pitfalls or best practices (if applicable)

Begin your response immediately without any preamble. Be direct and provide more depth than a basic description.
Do not hallucinate.
"""
    try:
        response = groq_api_call(user_message, client)
        redis_client.set(f"{concept}_v", response, ex=3600)
        return response
    except ConnectionError:
        return "Error connecting to server. Check your connection and retry"


def generate_programming_response(
    concept: str, client: httpx.Client, redis_client: redis.Redis
) -> str:
    cached_response = redis_client.get(concept + "_p")  # Correct
    if cached_response:
        return cached_response.decode("utf-8")
    user_message = f"""Provide a concise, practical explanation of the programming concept '{concept}' in 4-6 sentences. Include:
1. A clear, technical definition
2. Its primary use case or significance in programming
3. A brief, illustrative code example (if applicable)
4. One common pitfall or best practice

Begin your response immediately without any preamble. Focus on practical application. Separate code examples from body of text. If relevant, mention the programming language(s) where this concept is most commonly used.
Be direct and concise. Do not hallucinate.
"""
    try:
        response = groq_api_call(user_message, client)
        redis_client.set(concept + "_p", response, ex=3600)
        return response
    except ConnectionError:
        return "Error connecting to server. Check your connection and retry"


def print_formatted_response(response: str):
    output = Padding(response, (1, 1), style="white", expand=False)
    print(output)


def interactive_session(
    session_interactive: bool, verbosity: bool = False, programming: bool = False
):
    session = PromptSession(history=FileHistory(".litelookup_history"))
    # Set up connection pool
    with httpx.Client(
        http2=True, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    ) as client:
        # Set up Redis connection
        redis_client = redis.Redis(host="localhost", port=6379, db=0)

        while session_interactive:
            try:
                user_input = session.prompt(
                    "Enter a concept to lookup (enter 'q' , 'quit' or 'exit' to exit): "
                ).strip()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            text = validate_input(user_input, session_interactive)

            if text.lower() in ("q", "quit", "exit"):
                session_interactive = False
                print("Exiting LiteLookup. Goodbye!")
                break

            if text and verbosity is True:
                response = generate_verbose_response(text, client, redis_client)
                print_formatted_response(response)
            elif text and programming is True:
                response = generate_programming_response(text, client, redis_client)
                print_formatted_response(response)
            else:
                response = generate_response(text, client, redis_client)
                print_formatted_response(response)


def main():
    try:
        client = httpx.Client(
            http2=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        redis_client = redis.Redis()
        user_input, args = get_input()
        if args.interactive:
            if args.programming:
                log.logger.info("Switching to interactive programming mode...\n")
                interactive_session(args.interactive, verbosity=False, programming=True)
            else:
                match args.verbose:
                    case True:
                        log.logger.info("Switching to verbose interactive mode...\n")
                        interactive_session(
                            args.interactive, verbosity=True, programming=False
                        )
                    case False:
                        log.logger.info("Switching to interactive mode...\n")
                        interactive_session(
                            args.interactive, verbosity=False, programming=False
                        )
        elif args.verbose:
            log.logger.info("fetching verbose response...\n\n")
            response = generate_verbose_response(user_input, client, redis_client)
            print_formatted_response(response)
        elif args.programming:
            log.logger.info("programming mode...\n\n")
            response = generate_programming_response(user_input, client, redis_client)
            print_formatted_response(response)
        else:
            log.logger.info("fetching response...\n\n")
            response = generate_response(user_input, client, redis_client)
            print_formatted_response(response)
    except (InvalidInputError, InputTooLongError, UnsupportedCharactersError) as e:
        log.logger.error(f"Invalid input: {str(e)} ")
    # except Exception as e:
    #     print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
