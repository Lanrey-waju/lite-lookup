# LiteLookup 🔎

![code coverage badge](https://github.com/Lanrey-waju/lite-lookup/actions/workflows/ci_litelookup.yml/badge.svg)

LiteLookup is a command-line tool developed in Python that fetches beginner-level information about any concept directly from the command line. This tool is designed for users who want quick, concise, and accessible explanations without leaving their terminal.

## Features

- **Command-Line Interface (CLI):** Uses `argparse` to handle user inputs.
- **Error Handling:** Validates user input to ensure meaningful queries. Catches special characters and raises appropriate errors.
- **API Integration:** Utilizes the Groq LLM API to generate concise explanations of the concepts provided.
- **Caching:** Implements Redis for persistent caching of API responses, reducing unnecessary API calls and improving response times.
- **Interactive Shell Session:** Launches an intractive shell for faster, continuous lookups after the initial connection establishment. This mode is ideal for making multiple queries in a single session without the overhead of reconnecting for each request.
- **Verbose Mode:** Use the `-v` flag for more detailed explanations, including examples or code snippets when applicable.
- **HTTP/2 Support:** Uses `httpx` with connection pooling and HTTP/2 for efficient API communication.
- **Expandable:** Designed to be easily extended with new features and enhancements.

## Installation

### Prerequisites

- Python 3.8 or higher
- Redis server installed and running
- Groq LLM API access — You will need to store a valid Groq API Key as a secret. You can generate one for free [here](https://console.groq.com/keys).

### Setup

1. **Install LiteLookup via pip:**

   `pip install litelookup`

2. **Configure the environment variables:**

    Export the API Key from [Groq](https://console.groq.com/keys) like so:
    `export GROQ_API_KEY=your_api_key_here`

3. Ensure Redis is running:

    `redis-cli ping`

    You should get `PONG` which indicates redis is up and running.
 
## Usage

### Basic Usage
To fetch information about a concept, use the following command:

`lookup "concept"`

For example, `lookup "git rebase"`

### Verbose Mode
For a more detailed response, including examples or code snippets:

`lookup "git rebase" -v'

### Interactive Shell Mode
Enter the interactive mode for continuous lookups without reconnecting:

- `litelookup -i`

While in the interactive mode, you can toggle verbosity:

- `litelookup -i -v`

To exit the interactive mode, type:

- `quit` or `q`

## Contributing
If you'd like to contribute to LiteLookup, please fork the repository and submit a pull request. For any issues or suggestions, feel free to open an issue on the GitHub repository.

## Contact
For any questions or support, please contact Abdulmumin at [lanreywaju97@gmail.com]