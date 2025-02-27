import asyncio
from typing import List

from src.clients.clients import ApiClient, SocketClient
from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.controllers.controllers import (
    Controller,
    AirMeasurementsController,
    GroundTemperatureController,
    RainfallController,
    WindMeasurementController,
)
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
    api_client = ApiClient(auth_url=global_config.api.auth_url, user=global_config.api.user, password=global_config.api.password)
    socket_client = SocketClient(
        socket_url=global_config.socket.socket_url,
        auth_url=global_config.api.auth_url,
        user=global_config.api.user,
        password=global_config.api.password,
    )

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
                seconds_waiting: int = 10

            logger.info(msg=f"Sleeping {seconds_waiting} seconds while sensors are getting readings")
            await asyncio.sleep(delay=seconds_waiting)

            try:
                measurements: List[Measurement] = await asyncio.gather(*(controller.get_measurement() for controller in controllers))

                if global_config.environment.read_only:
                    logger.info(msg="Read only mode enabled. Measurements will not be added nor emitted")
                else:
                    tuples_endpoint_measurement: List[tuple[str, Measurement]] = [
                        (controller.api_endpoint, measurement) for controller, measurement in zip(controllers, measurements)
                    ]
                    tuples_event_measurement: List[tuple[str, Measurement]] = [
                        (controller.socket_event, measurement) for controller, measurement in zip(controllers, measurements)
                    ]
                    await asyncio.gather(
                        api_client.add_measurements(tuples_endpoint_measurement=tuples_endpoint_measurement),
                        socket_client.emit_measurements(tuples_event_measurement=tuples_event_measurement),
                    )

                if global_config.environment.is_testing:
                    break
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
