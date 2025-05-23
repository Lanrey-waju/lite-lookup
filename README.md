# LiteLookup 🔎

![code coverage badge](https://github.com/Lanrey-waju/lite-lookup/actions/workflows/ci_litelookup.yml/badge.svg)

LiteLookup is a command-line tool developed in Python that fetches beginner-level information about any concept directly from the command line.

When working on the terminal, I often had the need for quick references about concepts or commands depending on what I'm working on. I didn't like the idea of having to juggle browser tabs and context-switch because of some beginner information. I built LiteLookup so I could access quick, concise information and accessible explanations without leaving the terminal.

## Features

- **Command-Line Interface (CLI):** Uses `argparse` to handle user inputs.
- **Error Handling:** Validates user input to ensure meaningful queries. Catches special characters and raises appropriate errors.
- **API Integration:** Utilizes the Groq LLM API to generate concise explanations of the concepts provided.
- **Caching:** Implements Redis for persistent caching of API responses, reducing unnecessary API calls and improving response times.
- **Interactive Shell Session:** Launches an intractive shell for faster, continuous lookups after the initial connection establishment. This mode is ideal for making multiple queries in a single session without the overhead of reconnecting for each request.
- **HTTP/2 Support:** Uses `httpx` with connection pooling and HTTP/2 for efficient API communication.
- **Expandable:** Designed to be easily extended with new features and enhancements.

## Installation

### Prerequisites

- Python 3.11 or higher
- Redis server installed and running
- Groq LLM API access — You will need to store a valid Groq API Key as a secret. You can generate one for free [here](https://console.groq.com/keys).

### Setup

1. **Install LiteLookup via pip or pipx:**

   `pip install litelookup`

   Check if LiteLookup is correctly installed with
   `lookup --version`

2. **Configure the environment variables:**

   Enter the API Key from [Groq](https://console.groq.com/keys) in the prompt from the first usage:

   `>>Enter API KEY here: your-api_key here`

   Replace "your_api_key_here" with the API key to begin interacting with the tool.

   Select the desired model from the list of available models as shown below:

   ![custom model](./assets/custom-groq_model.png)

   pick one of the models using the arrow keys and press enter. Press tab to move to the OK button and press enter to confirm your choice.

3. \*_Ensure Redis is running:_

   `redis-cli ping`

   You should get `PONG` which indicates redis is up and running.

## Usage

### Basic Usage

To fetch information about a concept, use the following command:

`lookup "concept"`

For example, `lookup "git rebase"`

For queries with special characters (such as '&', '|', '\', etc), please make sure to wrap your queries in quotes. Otherwise, the shell may interprete these characters.

### Programming Mode

lookup "programming concept" -p

For example, `lookup "print() in python" -p`

### Interactive Shell Mode

Enter the interactive mode for continuous lookups without reconnecting:

- `lookup -i`

If you wish to generate verbose responses while in the interactive mode, use

- `lookup -i -p` or `lookup -ip
  The responses you get with this will be more finetuned for programming.

- `lookup -i -d` or `lookup -id`
  This combines interactive mode with direct mode for quick, concise command-related answers.

To exit the interactive mode, type:

- `quit` or `q`

### Direct Mode

Get concise, direct answers for command-related queries:

- `lookup -d "command to ..."` or `lookup --direct "how to ..."`

For example, lookup -d "command to delete a file in Linux" or lookup -d "how to rollback a commit in Git"

This mode provides brief, actionable responses without additional explanations. For best results, start your query with "command to" or "how to".

### Conversational or Chat Mode

Get conversational with the tool! LiteLookup offers a chat feature that allows you to go back and forth with it on an idea. To toggle this mode, use:

`lookup -ic`

Now you have a terminal buddy to brainstorm with.

## Flags

- -p or --programming: Programming-focused responses
- -d or --direct: Concise, command-related answers
- -i or --interactive: Interactive shell mode
- -ic or --interactive --chat: conversational mode

## Contributing

If you'd like to contribute to LiteLookup, please fork the repository and submit a pull request. For any issues or suggestions, feel free to open an issue on the GitHub repository. Also, please submit any issue you encounter using the tool and I'll be happy to discuss and fix it.

## Contact

For any questions or support, please contact Abdulmumin at [lanreywaju97@gmail.com]
