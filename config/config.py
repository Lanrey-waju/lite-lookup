from prompt_toolkit import prompt


def get_user_key():
    api_key = prompt("Enter your api key here: ")
    api_key = api_key.strip()
    return api_key


def store_api_key(api_key: str):
    try:
        with open(".env", "w") as f:
            f.write(f"GROQ_API_KEY={api_key}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


def configure_api_key():
    store_api_key(get_user_key())
