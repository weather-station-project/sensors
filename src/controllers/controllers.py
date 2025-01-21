from abc import ABC

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.helpers.helpers import add_measurement_to_api
from src.model.measurement import Measurement
from src.services.services import Service, AirMeasurementService, GroundTemperatureService


class Controller(ABC):
    __slots__ = ["__service", "__api_endpoint", "__logger"]

    def __init__(self, service: Service, api_endpoint: str) -> None:
        self.__service = service
        self.__api_endpoint = api_endpoint
        self.__logger = get_logger(name=self.__class__.__name__)

        self.__logger.debug(msg=f"Controller initialized with the service {self.__service.__class__.__name__} and API endpoint {self.__api_endpoint}")

    async def execute(self) -> None:
        measurement: Measurement = await self.__service.get_measurement()
        self.__logger.info(msg=f"Measurement obtained from {self.__service.__name__}: {measurement.to_dict()}")

        await add_measurement_to_api(
            url=self.__api_endpoint, user=global_config.api.user, password=global_config.api.password, measurement=measurement
        )
        self.__logger.info(msg=f"Measurement added through the endpoint {self.__api_endpoint} correctly")


class AirMeasurementsController(Controller):
    def __init__(self) -> None:
        super().__init__(service=AirMeasurementService(), api_endpoint=global_config.api.add_air_measurement_endpoint)


class GroundTemperatureController(Controller):
    def __init__(self) -> None:
        super().__init__(service=GroundTemperatureService(), api_endpoint=global_config.api.add_ground_temperature_endpoint)
