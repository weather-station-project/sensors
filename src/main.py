import asyncio
from typing import List

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.controllers.controllers import Controller, AmbientTemperatureController

logger = get_logger(name="main")


def get_enabled_controllers() -> List[Controller]:
    controllers: List[Controller] = []

    if global_config.device.bme280_sensor_enabled:
        logger.info(msg=f"Adding {AmbientTemperatureController.__name__}")
        controllers.append(AmbientTemperatureController())

    return controllers


async def main() -> int:
    try:
        logger.info(msg="Application started")

        logger.info(msg="Getting controllers to be initiated")
        controllers: List[Controller] = get_enabled_controllers()
        logger.debug(msg=f"Controllers to be initiated: {[controller.__class__.__name__ for controller in controllers]}")

        while True:
            logger.debug(msg=f"Sleeping {global_config.device.minutes_between_readings} minutes while sensors are getting readings")
            await asyncio.sleep(global_config.device.minutes_between_readings * 60)

            try:
                for controller in controllers:
                    controller.execute()

                if global_config.environment.is_testing:
                    break
            except Exception:
                pass

        return 0
    except Exception as e:
        logger.critical(e, exc_info=True)
        return 1
    finally:
        logger.info(msg="Application finished")


if __name__ == "__main__":
    asyncio.run(main())
