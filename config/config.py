import os
from pathlib import Path
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator
import configparser
import platform


def is_valid_APIkey(api_key: str):
    return api_key.strip().startswith("gsk_")


validator = Validator.from_callable(
    is_valid_APIkey,
    error_message="API key should start with 'gsk_'.",
    move_cursor_to_end=True,
)


def get_config_dir():
    system = platform.system()
    if system == "Windows":
        return Path(os.getenv("LOCALAPPDATA", os.path.expanduser("~"))) / "litelookup"
    elif system in ["Linux", "Darwin"]:
        return Path(os.path.expanduser("~/.config/litelookup"))
    else:
        # fallback
        return Path(os.path.expanduser("~/.litelookup"))


def get_user_key():
    print(f"Get your free API key from https://console.groq.com/keys")
    api_key = prompt(
        "Paste API key here: ", validator=validator, validate_while_typing=False
    )
    api_key = api_key.strip()
    return api_key


def store_api_key(api_key: str):
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.ini"

    try:
        with config_file.open("w") as f:
            f.write(f"[env]\nGROQ_API_KEY={api_key}\n")
        os.chmod(config_file, 0o600)
    except Exception as e:
        print(f"Error storing API key: {str(e)}")
        raise


def load_api_key():
    config = configparser.ConfigParser()
    config_file = get_config_dir() / "config.ini"
    config.read(config_file)
    try:
        api_key = config["env"]["GROQ_API_KEY"]
    except KeyError:
        return None
    return api_key


def configure_api_key():
    store_api_key(get_user_key())
    print("API key stored successfully.")
