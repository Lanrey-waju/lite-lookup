import logging.config
import json
import logging
import datetime as dt
from pathlib import Path
import atexit
from typing import override
import logging.handlers

from config.directory import get_app_directory

LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class MyJSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: dict[str, str] | None = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord):
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(
                record.created, tz=dt.timezone.utc
            ).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: (
                msg_val
                if (msg_val := always_fields.pop(val, None)) is not None
                else getattr(record, val)
            )
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


def setup_logging():
    log_file_path = get_app_directory()
    log_file = log_file_path / "litelookup.log.jsonl"

    log_file_path.mkdir(parents=True, exist_ok=True)

    base_dir = Path(__file__).resolve().parent.parent
    json_config_path = base_dir / "log" / "config.json"

    with open(json_config_path, "r") as f_in:
        config = json.load(f_in)

    config["handlers"]["file_json"]["filename"] = log_file
    logging.config.dictConfig(config)
    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


class ExcludeFilter(logging.Filter):
    def __init__(self, names: list = None):
        super().__init__()
        self.names = names or []

    @override
    def filter(self, record: logging.LogRecord) -> bool | logging.LogRecord:
        return not any(record.name.startswith(name) for name in self.names)
