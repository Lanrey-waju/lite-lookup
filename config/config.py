import configparser
import os
import platform
import sys
from pathlib import Path

from model import GroqModel
from prompt_toolkit import prompt
from prompt_toolkit.validation import Validator


def is_valid_APIkey(api_key: str):
    return api_key.strip().startswith("gsk_")


def is_valid_model(model_input: str) -> bool:
    # Check if model is a valid GroqModel
    return any(model_input == model.value for model in GroqModel)

def list_available_models() -> list(str):
    return [model.value for model in GroqModel]

apikey_validator = Validator.from_callable(
    is_valid_APIkey,
    error_message="API key should start with 'gsk_'.",
    move_cursor_to_end=True,
)

model_validator = Validator.from_callable(
    is_valid_model,
    error_message="Model must be one of: " + ", ".join(list_available_models()),
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
    print("Get your free API key from https://console.groq.com/keys")
    try:
        api_key = prompt(
            "Paste API key here: ", validator=apikey_validator, validate_while_typing=False
        ).strip()
        return api_key if api_key else None
    except (KeyboardInterrupt, EOFError):
        return None


def create_config_file(config_dir: Path) -> Path:
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / "config.ini"
    return config_file


def store_api_key(api_key: str) -> bool:
    config_file = create_config_file(get_config_dir())

    try:
        with config_file.open("w") as f:
            f.write(f"[env]\nGROQ_API_KEY={api_key}\n")
        os.chmod(config_file, 0o600)
        return True
    except Exception as e:
        print(f"Error storing API key: {str(e)}")
        return False


def store_model(model: str) -> bool:
    config_file = create_config_file(get_config_dir())

    try:
        with config_file.open("a") as f:
            f.write(f"[env]\nGROQ_MODEL={model}\n")
        os.chmod(config_file, 0o600)
        return True
    except Exception as e:
        print(f"error storing model: {str(e)}")
        return False


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
    while True:
        api_key = get_user_key()
        if api_key is None:
            print("API key configuration cancelled.")
            return None
        if store_api_key(api_key):
            return api_key
        print("Error storing API key. Please try again.")


# set the apikey entry to an empty string
def reset_config():
    config = configparser.ConfigParser()
    config_file = get_config_dir() / "config.ini"
    config.read(config_file)
    with config_file.open("w+") as cf:
        cf.write("[env]\nGROQ_API_KEY=")

def configure_model():
    while True:
        model = prompt(
            "Paste model here: ",
            validator=model_validator,
            validate_while_typing=False,
        ).strip()
        if model is None:
            print("Model configuration cancelled.")
            return None
        if store_model(model):
            return model
        print("Error storing model. Please try again."
