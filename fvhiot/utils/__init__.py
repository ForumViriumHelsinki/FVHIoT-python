import os
import logging
from logging.config import dictConfig

import sentry_sdk


def init_script():
    """Do all necessary stuff to initialize a script (endpoint, parser, etc.)"""
    dictConfig(
        {
            "version": 1,
            "formatters": {"default": {"format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"}},
            "handlers": {"wsgi": {"class": "logging.StreamHandler", "formatter": "default"}},
            "root": {"level": os.getenv("LOG_LEVEL", "INFO"), "handlers": ["wsgi"]},
        }
    )

    if os.getenv("SENTRY_DSN"):
        logging.info("Initializing sentry: {}".format(os.getenv("SENTRY_DSN")))
        sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"))
    else:
        logging.info("Initializing sentry: SENTRY_DSN is not set!")
