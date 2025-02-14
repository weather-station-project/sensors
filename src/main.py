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
from src.exceptions.exceptions import GettingMeasurementException, AddingMeasurementException
from src.model.models import Measurement

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
    exit_code = 0

    try:
        logger.info(msg="Application started")

        logger.info(msg="Getting controllers to be initiated")
        controllers: List[Controller] = get_enabled_controllers()
        logger.debug(msg=f"Controllers to be initiated: {[controller.__class__.__name__ for controller in controllers]}")

        if len(controllers) == 0:
            raise Exception("No controllers were enabled. Please enable at least one controller in the configuration")

        while True:
            if global_config.environment.is_production:
                seconds_waiting: int = global_config.device.minutes_between_readings * 60
            elif global_config.environment.is_testing:
                seconds_waiting: int = 1
            else:
                seconds_waiting: int = 20

            logger.info(msg=f"Sleeping {seconds_waiting} seconds while sensors are getting readings")
            await asyncio.sleep(delay=seconds_waiting)

            try:
                measurements: List[Measurement] = await asyncio.gather(*(controller.get_measurement() for controller in controllers))

                # TODO ADD EMIT SOCKET SERVER

                if global_config.environment.read_only:
                    logger.info(msg="Read only mode enabled. Measurements will not be added to the API")
                else:
                    await asyncio.gather(
                        *(controller.add_measurement(measurement) for controller, measurement in zip(controllers, measurements) if measurement)
                    )

                if global_config.environment.is_testing:
                    break
            except GettingMeasurementException as e:
                logger.error(msg=f"Error getting a measurement from the service {e.service_name}", exc_info=e)
            except AddingMeasurementException as e:
                logger.error(msg=f"Error adding a measurement with the response ({e.response_status}) {e.response_message}", exc_info=e)
            except Exception as e:
                logger.exception(msg="Unexpected error getting or adding a measurement", exc_info=e)
    except Exception as e:
        logger.critical(e, exc_info=True)
        exit_code = 1
    finally:
        logger.info(msg="Application finished")
        return exit_code


if __name__ == "__main__":
    exit(asyncio.run(main()))
