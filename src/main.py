import sys
from typing import List

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.controllers.controllers import Controller, AmbientTemperatureController

logger = get_logger(name=__name__)


def get_controllers() -> List[Controller]:
    controllers: List[Controller] = []

    if global_config.device.bme280_sensor_enabled:
        logger.info(msg=f"Adding {AmbientTemperatureController.__name__}")
        controllers.append(AmbientTemperatureController())

    return controllers


def get_true():
    # Stupid method for the UTs to avoid infinite loop
    return True


def main() -> int:
    try:
        logger.info(msg="Application started")

        logger.info(msg="Getting controllers to be initiated")
        controllers: List[Controller] = get_controllers()
        controllers.pop()
        controllers.pop()

        return 0
    except Exception as e:
        logger.critical(e, exc_info=True)
        return 1
    finally:
        logger.info(msg="Application finished")


if __name__ == "__main__":
    sys.exit(main())
