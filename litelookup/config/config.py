import configparser
import os
import platform
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator
from pydantic import SecretStr

from .model import GroqModel


def is_valid_APIkey(api_key: str):
    return api_key.strip().startswith("gsk_")


def is_valid_model(model_input: str) -> bool:
    # Check if model is a valid GroqModel
    return any(model_input == model.value for model in GroqModel)


def list_available_models() -> list[str]:
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


async def get_user_key():
    print("Get your free API key from https://console.groq.com/keys")
    session = PromptSession()
    try:
        api_key = await session.prompt_async(
            "Paste API key here: ",
            is_password=True,
            validator=apikey_validator,
            validate_while_typing=False,
        )
        return api_key.strip() if api_key else None
    except (KeyboardInterrupt, EOFError):
        return None


async def get_user_model() -> str:
    model_choices = [(model, model.value) for model in GroqModel]

    custom_style = Style.from_dict(
        {
            "dialog": "bg:#2b2b2b",
            "dialog frame.label": "bg:#333333 #ffffff bold",
            "dialog.body": "bg:#2b2b2b #ffffff",
            "dialog shadow": "bg:#1c1c1c",
            "radio": "bg:#2b2b2b #ffffff",
            "radio-selected": "bg:#005fff #ffffff",
            "button": "bg:#555555 #ffffff",
            "button.focused": "bg:#005fff #ffffff",
            "text-area": "bg:#2b2b2b #ffffff",
        }
    )
    result = await radiolist_dialog(
        title="Select a Groq model",
        text="Choose one of the available models:",
        values=model_choices,
        style=custom_style,
    ).run_async()
    if result:
        return result.value
    else:
        print("No model selected... defaulting to gemma2-9b-it")
        return model_choices[1][1]


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
            f.write(f"GROQ_MODEL={model}\n")
        os.chmod(config_file, 0o600)
        return True
    except Exception as e:
        print(f"error storing model: {str(e)}")
        return False


def get_config_file() -> Path:
    return get_config_dir() / "config.ini"


def load_api_key() -> SecretStr:
    api_key = ""
    config = configparser.ConfigParser()
    config_file = get_config_file()
    config.read(config_file)
    try:
        api_key = config["env"]["GROQ_API_KEY"]
    except KeyError:
        return SecretStr(api_key)
    return SecretStr(api_key)


def load_model() -> str:
    model = ""
    config = configparser.ConfigParser()
    config_file = get_config_file()
    config.read(config_file)
    try:
        model = config["env"]["GROQ_MODEL"]
    except KeyError:
        return model
    return model


def load_config():
    api_key = load_api_key()
    model = load_model()
    return api_key, model


async def configure_api_key():
    while True:
        api_key = await get_user_key()
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
    if config_file.exists():
        config.read(config_file)
        with config_file.open("w+") as cf:
            cf.write("[env]\nGROQ_API_KEY=")
    else:
        return


async def configure_model():
    while True:
        model = await get_user_model()
        if model is None:
            print("Model configuration cancelled.")
            return None
        if store_model(model):
            return model
        print("Error storing model. Please try again.")
