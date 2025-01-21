import asyncio
from abc import ABC, abstractmethod
from typing import List

import bme280
import smbus2
from bme280 import compensated_readings

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.model.measurement import Measurement


class Service(ABC):
    __SECONDS_BETWEEN_READINGS: int = 15

    __slots__ = ["_readings", "__getting_readings", "__logger"]

    def __init__(self) -> None:
        self.__logger = get_logger(name=self.__class__.__name__)

        self._readings = []
        self.__getting_readings = False

        asyncio.create_task(coro=self.__add_value_to_readings())

    async def __add_value_to_readings(self) -> None:
        while True:
            try:
                if self.__getting_readings:
                    return

                reading: Measurement = await self.get_reading()
                self.readings.append(reading)
                self.__logger.debug(msg=f"Obtained reading: {reading.to_dict()}")

                if global_config.environment.is_testing:
                    break
            except Exception:
                pass
            finally:
                await asyncio.sleep(delay=self.__SECONDS_BETWEEN_READINGS)

    @abstractmethod
    async def get_reading(self) -> Measurement:
        raise NotImplementedError("A sub-class must be implemented.")

    @property
    def readings(self) -> List[Measurement]:
        return self._readings

    async def get_measurement(self) -> Measurement:
        pass


class AirMeasurementService(Service):
    __slots__ = ["__bus", "__address", "__calibration_params"]

    def __init__(self) -> None:
        super().__init__()

        if global_config.environment.is_production:
            self.__bus = smbus2.SMBus(bus=global_config.device.bme280_sensor_port)
            self.__address = int(global_config.device.bme280_sensor_address, 16)
            self.__calibration_params = bme280.load_calibration_params(bus=self.__bus, address=self.__address)

    async def get_reading(self) -> Measurement:
        if global_config.environment.is_production:
            data: compensated_readings = bme280.sample(bus=self.__bus, address=self.__address, compensation_params=self.__calibration_params)
            return Measurement(temperature=data.temperature, pressure=data.pressure, humidity=data.humidity)

        return Measurement(temperature=0, pressure=0, humidity=0)
