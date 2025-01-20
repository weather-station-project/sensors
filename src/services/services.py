import asyncio
from abc import ABC, abstractmethod
from typing import List

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.model.measurement import Measurement


class Service(ABC):
    __SECONDS_BETWEEN_READINGS: int = 10

    __slots__ = ["_readings", "__getting_readings", "__logger"]

    def __init__(self):
        self.__logger = get_logger(name=self.__class__.__name__)

        self._readings = []
        self.__getting_readings = False

        asyncio.create_task(self.add_value_to_readings())

    async def add_value_to_readings(self) -> None:
        while True:
            try:
                if self.__getting_readings:
                    return

                reading = self.get_reading()
                self.readings.append(reading)

                if global_config.environment.is_testing:
                    break
            except Exception:
                pass
            finally:
                await asyncio.sleep(self.__SECONDS_BETWEEN_READINGS)

    @abstractmethod
    def get_reading(self):
        raise NotImplementedError("A sub-class must be implemented.")

    @property
    def readings(self) -> List[Measurement]:
        return self._readings

    def get_measurement(self) -> Measurement:
        pass


class AmbientTemperatureService(Service):
    def get_reading(self):
        pass
