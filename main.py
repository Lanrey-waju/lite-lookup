import argparse
import os

from groq import Groq, GroqError


try:
    client = Groq(api_key=os.environ.get("GROQ_KEY"))
except GroqError:
    print("Ensure the API key is set and valid")


parser = argparse.ArgumentParser(
    prog="LiteLookup",
    description="Fetches a beginner infornation about any concept you want to learn about right from the comfort of your command line",
)

parser.add_argument(
    "lookup",
    help="look an information up and print it out",
)
parser.add_argument(
    "-v", "--verbose", help="increase output verbosity", action="count", default=0
)
parser.add_argument("content", nargs="*")

parser.add_argument("--version", action="version", version="%(prog)s 1.0")
args = parser.parse_args()

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": " ".join(args.content),
        }
    ],
    model="llama3-8b-8192",
)

if args.verbose >= 2:
    print(chat_completion.choices[0].message.content)
elif args.verbose >= 1:
    print("Normal verbosity turned on")
else:
    print(" ".join(args.content))
