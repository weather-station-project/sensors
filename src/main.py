import sys

from src.colored_logging.colored_logging import get_logger

logger = get_logger(name=__name__)


def main() -> int:
    try:
        logger.info("Application started")
        return 0
    except Exception as e:
        logger.critical(e, exc_info=True)
        return 1
    finally:
        logger.info("Application finished")


if __name__ == "__main__":
    sys.exit(main())
