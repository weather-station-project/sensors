import asyncio
from typing import List

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.controllers.controllers import (
    Controller,
    AirMeasurementsController,
    GroundTemperatureController,
    RainfallController,
    WindMeasurementController,
)

logger = get_logger(name="main")


def get_enabled_controllers() -> List[Controller]:
    controllers: List[Controller] = []

    if global_config.device.bme280_sensor_enabled:
        logger.info(msg=f"Adding {AirMeasurementsController.__name__}")
        controllers.append(AirMeasurementsController())

    if global_config.device.ground_temperature_sensor_enabled:
        logger.info(msg=f"Adding {GroundTemperatureController.__name__}")
        controllers.append(GroundTemperatureController())

    if global_config.device.rain_gauge_enabled:
        logger.info(msg=f"Adding {RainfallController.__name__}")
        controllers.append(RainfallController())

    if global_config.device.anemometer_enabled:
        logger.info(msg=f"Adding {WindMeasurementController.__name__}")
        controllers.append(WindMeasurementController())

    return controllers


async def main() -> int:
    try:
        logger.info(msg="Application started")

        logger.info(msg="Getting controllers to be initiated")
        controllers: List[Controller] = get_enabled_controllers()
        logger.debug(msg=f"Controllers to be initiated: {[controller.__class__.__name__ for controller in controllers]}")

        while True:
            if global_config.environment.is_production:
                seconds_waiting: int = global_config.device.minutes_between_readings * 60
            elif global_config.environment.is_testing:
                seconds_waiting: int = 1
            else:
                seconds_waiting: int = 20

            logger.debug(msg=f"Sleeping {seconds_waiting} seconds while sensors are getting readings")
            await asyncio.sleep(delay=seconds_waiting)

            try:
                for controller in controllers:
                    await controller.execute()

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
    exit(asyncio.run(main()))
