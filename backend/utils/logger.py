import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    """Configure application logging and optionally write logs to file."""
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "sql_migrator.log")

    handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=2)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s"
        )
    )
    handler.setLevel(logging.INFO)

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("SQL Migrator application started.")
