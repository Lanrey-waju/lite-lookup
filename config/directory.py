import os
import platform
from pathlib import Path


def get_app_directory():
    system = platform.system()
    if system == "Windows":
        return Path(os.getenv("APPDATA")) / "LiteLookup"
    elif system in ["Darwin", "Linux"]:
        return Path(os.path.expanduser("~/.local/share/litelookup"))
    else:
        return Path(os.path.expanduser("~/.litelookup"))


app_dir = get_app_directory()

# create the app directory if it doesn't exist
app_dir.mkdir(parents=True, exist_ok=True)

# command history file
history_file = app_dir / "litelookup_history"
