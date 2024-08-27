# LiteLookup 🔎

![code coverage badge](https://github.com/Lanrey-waju/lite-lookup/actions/workflows/ci.yml/badge.svg)

LiteLookup is a command-line tool developed in Python that fetches beginner-level information about any concept directly from the command line. This tool is designed for users who want quick, concise, and accessible explanations without leaving their terminal.

## Features

- **Command-Line Interface (CLI):** Uses `argparse` to handle user inputs.
- **Error Handling:** Validates user input to ensure meaningful queries. Catches special characters and raises appropriate errors.
- **API Integration:** Utilizes the Groq LLM API to generate concise explanations of the concepts provided.
- **Caching:** Implements Redis for persistent caching of API responses, reducing unnecessary API calls and improving response times.
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

To fetch information about a concept, use the following command:

`lookup "concept"`
