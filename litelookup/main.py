import argparse
import asyncio
import logging
import os
import re
import sys

import httpx
import redis
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.patch_stdout import patch_stdout
from rich import print

from .chat import start_conversation_session
from .config.config import configure_api_key, configure_model, load_config, reset_config
from .config.directory import history_file
from .format import normal_bottom_toolbar, print_formatted_response
from .log.logging_config import setup_logging
from .responses import (
    generate_nofluff_response,
    generate_programming_response,
    generate_response,
)

if os.environ.get("PYTHON_DEBUG", 0) == "1":
    import debugpy

    debugpy.listen(("127.0.0.1", 5678))
    print("debugpy listening on port 5678")
    debugpy.wait_for_client()

logger = logging.getLogger(__name__)
VERSION = "0.20.4"


class InvalidInputError(Exception):
    pass


class InputTooLongError(InvalidInputError):
    pass


def get_input() -> tuple[str, argparse.Namespace]:
    parser = argparse.ArgumentParser(
        prog="LiteLookup",
        description=f"""LiteLookup: Your lightweight command-line learning companion. 
        Get simplified explanations about any concept, from general knowledge to 
        programming specifics. Use -p for programming-focused information,
        and -i for an interactive shell. Perfect for quick lookups and continuous learning sessions.
        
        version — {VERSION} """,
    )
    group = parser.add_mutually_exclusive_group()
    parser.add_argument("content", nargs="*")
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
    group.add_argument(
        "-c",
        "--chat",
        action="store_true",
        help="enters a conversational mode to brainstorm ideas",
    )
    parser.add_argument(
        "--version", action="version", version=f"{parser.prog} {VERSION}"
    )

    group.add_argument(
        "-p",
        "--programming",
        action="store_true",
        help="optimize response for programming concepts",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset the API key and model configuration",
    )
    args = parser.parse_args()

    if args.reset:
        reset_config()
        return "", args

    if args.interactive and not args.content:
        return "", args

    text = " ".join(args.content)
    return (
        validate_input(text, args.interactive),
        args,
    )


def validate_input(input: str, interactive: bool) -> str:
    if not interactive and not input:
        raise InvalidInputError(
            "Input cannot be empty. Please provide a concept to check"
        )

    if len(input) > 150:
        raise InputTooLongError(
            "Text cannot be more than 150 characters long. Consider shortening."
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


def interactive_session(
    session_interactive: bool,
    chat: bool = False,
    direct: bool = False,
    programming: bool = False,
):
    if chat is True:
        return start_conversation_session()
    else:
        return start_normal_session(
            session_interactive=session_interactive,
            direct=direct,
            programming=programming,
        )


async def start_normal_session(
    session_interactive: bool,
    programming: bool = False,
    direct: bool = False,
):
    session = PromptSession(mouse_support=True, history=FileHistory(str(history_file)))
    with httpx.Client(
        http2=True, limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
    ) as client:
        # Set up Redis connection
        redis_client = redis.Redis(host="localhost", port=6379, db=0)

        session_timeout = 3600  # 1 hour in seconds

        while session_interactive:
            try:
                with patch_stdout():
                    user_input = await asyncio.wait_for(
                        session.prompt_async(
                            ">> lookup: ",
                            bottom_toolbar=normal_bottom_toolbar,
                        ),
                        timeout=session_timeout,
                    )
            except KeyboardInterrupt:
                continue
            except EOFError:
                break
            except asyncio.TimeoutError:
                logger.info("Session timed out due to inactivity")
                break

            text = validate_input(user_input, session_interactive)

            if text.lower() in ("q", "quit", "exit"):
                session_interactive = False
                logger.info("Exiting LiteLookup. Goodbye!")
                break

            if text and direct is True:
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
    user_input, args = get_input()
    if args.reset:
        reset_config()
        return
    api_key, model = load_config()
    if api_key is None or api_key == "":
        api_key = configure_api_key()
        if api_key is None:
            print("API key is required to use this tool. Exiting.")
            sys.exit(1)
        else:
            model = configure_model()
            if model:
                print("API key and model configured. Please run your command again.")
                sys.exit(0)
    try:
        client = httpx.Client(
            http2=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )
        user_input, args = get_input()
        redis_client = redis.Redis()
        if args.interactive:
            if args.programming:
                logger.info(
                    f"Switching to interactive programming mode using {model}...\n"
                )
                interactive_session(
                    args.interactive,
                    programming=True,
                )
            elif args.chat:
                logger.info(f"Switching to conversational mode using {model}...\n\n")
                asyncio.run(interactive_session(args.interactive, chat=True))
            elif args.direct:
                logger.info(
                    f"Switching to interactive no-frills mode using {model}...\n"
                )
                asyncio.run(
                    interactive_session(
                        args.interactive,
                        direct=True,
                    )
                )
            else:
                logger.info(f"Switching to interactive mode using {model}...\n")
                interactive_session(
                    args.interactive,
                    programming=False,
                    direct=False,
                )
        elif args.programming:
            logger.info(f"programming mode using {model} ...\n\n")
            response = generate_programming_response(user_input, client, redis_client)
            print_formatted_response(response)
        elif args.direct:
            logger.info(f"direct mode using {model}...\n\n")
            response = generate_nofluff_response(user_input, client, redis_client)
            print_formatted_response(response)
        else:
            logger.info(f"normal mode using {model}...\n\n")
            response = generate_response(user_input, client, redis_client)
            print_formatted_response(response)
    except (InvalidInputError, InputTooLongError) as e:
        logger.error(f"Invalid input: {str(e)} ")


if __name__ == "__main__":
    main()
