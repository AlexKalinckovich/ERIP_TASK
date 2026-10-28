import os
def get_logging_config() -> dict:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "plain": {
                "format": "%(asctime)s %(levelname)-8s %(name)s | %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "plain",
                "level": log_level,
            },
        },
        "root": {
            "level": log_level,
            "handlers": ["console"],
        },
        "loggers": {
            "app": {"level": log_level, "propagate": True},
            "uvicorn": {"level": log_level, "propagate": True},
            "sqlalchemy.engine": {"level": "WARNING", "propagate": True},
            "httpx": {"level": "WARNING", "propagate": True},
            "apscheduler": {"level": "WARNING", "propagate": True},
        },
    }


LOG_CONFIG = get_logging_config()