"""define the log used globally"""
import contextvars
import logging.config
import os
import random
import string
from datetime import datetime

from core import settings

log_id_context = contextvars.ContextVar('log_id')


class LogIdFilter(logging.Filter):
    def filter(self, record):
        tags = getattr(record, "tags", None)
        if tags is None:
            setattr(record, "tags", {})
        log_id = get_context_log_id()
        getattr(record, "tags", {})["_logid"] = log_id
        record._logid = log_id
        return True


def get_context_log_id():
    """ get unique log id for current context.

    Context environment can be thread or coroutine.
    Returns:
        str: log id for current context
    """

    log_id = log_id_context.get(None)
    if log_id:
        return log_id
    else:
        time_id = datetime.now().strftime("%Y%m%d%H%M%S")
        ip_id = "010010010010"
        random_id = str("".join([random.choice(string.hexdigits).capitalize() for s in range(6)]))
        new_log_id = time_id + ip_id + random_id
        log_id_context.set(new_log_id)
        return new_log_id


config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s %(levelname)s %(_logid)s "
                      "[%(filename)s][%(funcName)s][%(lineno)d] > %(message)s"
        }
    },
    "filters": {
        "logid_filter": {
            "()": LogIdFilter,
        }
    },
    "handlers": {
        "log_agent": {
            "level": "INFO",
            "class": "bytedlogger.StreamLogHandler",
            "tags": {},
            "filters": ["logid_filter"],
        },
        # "console": {
        #     "level": "INFO",
        #     "class": "logging.StreamHandler",
        #     "formatter": "default",
        #     "filters": ["logid_filter"],
        # },
        "file_handler_info": {
            "level": "INFO",
            "class": "utils.log_handler.ConcurrentTimedRotatingFileHandler",
            "filename": os.path.join(settings.LOG_DIR,
                                     "info.log"),
            "formatter": "default",
            "encoding": "utf-8",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "filters": ["logid_filter"],
        },
        "file_handler_error": {
            "level": "ERROR",
            "class": "utils.log_handler.ConcurrentTimedRotatingFileHandler",
            "filename": os.path.join(settings.LOG_DIR,
                                     "error.log"),
            "formatter": "default",
            "encoding": "utf-8",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "filters": ["logid_filter"]
        },
        "request_handler": {
            "level": "INFO",
            "class": "utils.log_handler.ConcurrentTimedRotatingFileHandler",
            "filename": os.path.join(settings.LOG_DIR,
                                     "request.log"),
            "formatter": "default",
            "encoding": "utf-8",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "filters": ["logid_filter"]
        },
        "aiohttp_handler": {
            "level": "INFO",
            "class": "utils.log_handler.ConcurrentTimedRotatingFileHandler",
            "filename": os.path.join(settings.LOG_DIR,
                                     "aiohttp.log"),
            "formatter": "default",
            "encoding": "utf-8",
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
            "filters": ["logid_filter"]
        }
    },
    "loggers": {
        "request": {
            "handlers": ["request_handler", "log_agent"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["file_handler_info", "file_handler_error", "log_agent"],
            "level": "INFO"
        },
        "aiohttp": {
            "handlers": ["aiohttp_handler", "log_agent"],
            "level": "INFO"
        }
    }
}

logging.config.dictConfig(config)
app_logger = logging.getLogger("app")
request_logger = logging.getLogger("request")
aiohttp_logger = logging.getLogger("aiohttp")
