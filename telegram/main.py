import logging

import sentry_sdk
from modules.db import Database
from modules.utils import load_config
from sentry_sdk.integrations.logging import LoggingIntegration

if __name__ == "__main__":
    config = load_config()
    logging_fmt = "%(name)s - %(levelname)s - %(message)s"
    DEBUG = config["MAIN"].getboolean("debug")

    if DEBUG:
        logging.basicConfig(level=logging.INFO, format=logging_fmt)
    else:
        SENTRY_DSN = config["SENTRY"]["dsn"]
        SENTRY_LOG_LEVEL = int(config["SENTRY"]["log_level"])
        sentry_logging = LoggingIntegration(
            level=SENTRY_LOG_LEVEL,  # Capture info and above as breadcrumbs
            event_level=None,  # Send no events from log messages
        )
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[sentry_logging],
        )

    # Database init
    db = Database()
    db_conn = db.create_connection()
    db.create_table(db_conn, sql=db.sql_create_users_table)
