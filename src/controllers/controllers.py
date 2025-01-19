from abc import ABC

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.helpers.helpers import add_measurement_to_api
from src.model.measurement import Measurement
from src.services.service import Service

logger = get_logger(name=__name__)


class Controller(ABC):
    __slots__ = ["__service", "__api_endpoint"]

    def __init__(self, service: Service, api_endpoint: str) -> None:
        self.__service = service
        self.__api_endpoint = api_endpoint

    def execute(self) -> None:
        measurement: Measurement = self.__service.get_measurement()
        logger.info(msg=f"Measurement obtained from {self.__service.__name__}: {measurement.to_dict()}")

        add_measurement_to_api(url=self.__api_endpoint, user=global_config.api.user, password=global_config.api.password, measurement=measurement)


class AmbientTemperatureController(Controller):
    pass
