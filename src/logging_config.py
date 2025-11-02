import logging
import sys


LOG_FORMAT = "%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.getLogger("aiogram").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.ERROR)

    return logging.getLogger("bot"), logging.getLogger("dream_core")

bot_logger, ml_logger = setup_logging()