import logging
import os

from rich.logging import RichHandler

DEFAULT_LOG_LEVEL = int(os.getenv("LUMA_LOG_LEVEL", logging.INFO))

logger = logging.getLogger(__name__)


def setup_logger(level: int) -> None:
    # Taken from https://github.com/fastapi/fastapi-cli/blob/main/src/fastapi_cli/logging.py#L8
    rich_handler = RichHandler(
        show_time=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_path=False,
    )
    rich_handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(rich_handler)

    logger.setLevel(level)


setup_logger(DEFAULT_LOG_LEVEL)