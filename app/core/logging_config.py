import logging
import sys


def configure_logging(environment: str) -> None:
    level = logging.INFO if environment != "development" else logging.DEBUG
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # Quiet noisy libraries in development
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
