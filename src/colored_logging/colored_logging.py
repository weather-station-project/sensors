import logging
import colorlog

from src.config.global_config import global_config


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    color_formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s%(asctime)s - [%(levelname)s] [%(name)s] - %(message)s",
        log_colors={
            "DEBUG": "white",
            "INFO": "blue",
            "WARNING": "bold_yellow",
            "ERROR": "bold_red",
            "CRITICAL": "bold_red,bg_white",
        },
    )
    handler.setFormatter(color_formatter)

    logger.handlers = [handler]
    logger.setLevel(logging.getLevelName(global_config.log.level.upper()))

    return logger
