import argparse
import re
import logging
from log.logging_config import setup_logging

import redis
import httpx
from rich.padding import Padding
from rich import print
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory

# from . import log
from .responses import (
    generate_response,
    generate_programming_response,
    generate_verbose_response,
    generate_nofluff_response,
)
from config.config import configure_api_key, load_api_key


logger = logging.getLogger(__name__)


class InvalidInputError(Exception):
    pass


class InputTooLongError(InvalidInputError):
    pass


class UnsupportedCharactersError(InvalidInputError):
    pass


def get_input() -> tuple[str, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="LiteLookup",
        description="""LiteLookup: Your lightweight command-line learning companion. 
        Get simplified explanations about any concept, from general knowledge to 
        programming specifics. Use -v for more detailed responses, -p for 
        programming-focused information, and -i for an interactive shell. 
        Perfect for quick lookups and continuous learning sessions.""",
    )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("content", nargs="*")
    group.add_argument(
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
    group.add_argument(
        "-d",
        "--direct",
        action="store_true",
        help="returns a no-fluff response on a programming query",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.2.3")

    group.add_argument(
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


def print_formatted_response(response: str):
    output = Padding(response, (1, 1), style="green", expand=False)
    print(output)


def bottom_toolbar():
    return HTML(
        ' Press <i>"q", "quit", or "exit"</i> to <style bg="ansired">quit</style> <b>litelookup</b>'
    )


def interactive_session(
    session_interactive: bool,
    verbosity: bool = False,
    programming: bool = False,
    direct: bool = False,
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
                    ">> lookup: ", bottom_toolbar=bottom_toolbar
                ).strip()
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            text = validate_input(user_input, session_interactive)

            if text.lower() in ("q", "quit", "exit"):
                session_interactive = False
                logger.info("Exiting LiteLookup. Goodbye!")
                break

            if text and verbosity is True:
                response = generate_verbose_response(text, client, redis_client)
                print_formatted_response(response)
            elif text and direct is True:
                response = generate_nofluff_response(text, client, redis_client)
                print_formatted_response(response)
            elif text and programming is True:
                response = generate_programming_response(text, client, redis_client)
                print_formatted_response(response)
            else:
                response = generate_response(text, client, redis_client)
                print_formatted_response(response)


def main():
    setup_logging()
    if load_api_key() is None:
        configure_api_key()
    try:
        client = httpx.Client(
            http2=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        redis_client = redis.Redis()
        user_input, args = get_input()
        if args.interactive:
            if args.programming:
                logger.info("Switching to interactive programming mode...\n")
                interactive_session(
                    args.interactive, verbosity=False, programming=True, direct=False
                )
            elif args.direct:
                logger.info("Switching to interactive no-frills mode...\n")
                interactive_session(
                    args.interactive, verbosity=False, programming=False, direct=True
                )
            else:
                match args.verbose:
                    case True:
                        logger.info("Switching to verbose interactive mode...\n")
                        interactive_session(
                            args.interactive,
                            verbosity=True,
                            programming=False,
                            direct=False,
                        )
                    case False:
                        logger.info("Switching to interactive mode...\n")
                        interactive_session(
                            args.interactive,
                            verbosity=False,
                            programming=False,
                            direct=False,
                        )
        elif args.verbose:
            logger.info("verbose mode...\n\n")
            response = generate_verbose_response(user_input, client, redis_client)
            print_formatted_response(response)
        elif args.programming:
            logger.info("programming mode...\n\n")
            response = generate_programming_response(user_input, client, redis_client)
            print_formatted_response(response)
        elif args.direct:
            logger.info("direct mode...\n\n")
            response = generate_nofluff_response(user_input, client, redis_client)
            print_formatted_response(response)
        else:
            logger.info("normal mode...\n\n")
            response = generate_response(user_input, client, redis_client)
            print_formatted_response(response)
    except (InvalidInputError, InputTooLongError, UnsupportedCharactersError) as e:
        logger.error(f"Invalid input: {str(e)} ")


if __name__ == "__main__":
    main()
