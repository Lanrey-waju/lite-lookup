import argparse

from llm import client, ConnectionError


def get_input():
    parser = argparse.ArgumentParser(
        prog="LiteLookup",
        description="Fetches a beginner infornation about any concept you want to learn about right from the comfort of your command line",
    )
    parser.add_argument(
        "lookup",
        help="look an information up and print it out",
    )
    parser.add_argument("content", nargs="*")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0")
    args = parser.parse_args()
    return " ".join(args.content)


def generate_response():
    user_message = f"""
Return a very concise information about the concept that I will provide
you with. It should generally be like the most important information
about the concept and should be enough to at least educate someone that
has never heard the concept before. You do not need to add
any preamble. Just provide the information from the first line.
The concept is {get_input()}.
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


print(generate_response())
