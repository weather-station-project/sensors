import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from statistics import mode, mean
from typing import List

import bme280
import random
import smbus2
from bme280 import compensated_readings
from gpiozero import Button
from w1thermsensor import AsyncW1ThermSensor, Unit

from src.colored_logging.colored_logging import get_logger
from src.config.global_config import global_config
from src.model.models import Measurement, WindDirection
from src.sensors.anemometer import Anemometer
from src.sensors.vane import Vane


class Service(ABC):
    _SECONDS_BETWEEN_READINGS: int = 15

    __slots__ = ["__readings", "__getting_readings", "_logger"]

    def __init__(self) -> None:
        self._logger = get_logger(name=self.__class__.__name__)

        self.__readings = []
        self.__getting_readings = False

        asyncio.create_task(coro=self._add_value_to_readings())

    @property
    def readings(self) -> List[Measurement]:
        return self.__readings

    @property
    def getting_readings(self) -> bool:
        return self.__getting_readings

    async def _add_value_to_readings(self) -> None:
        while True:
            try:
                if self.__getting_readings:
                    return

                reading: Measurement = await self.get_reading()
                self.readings.append(reading)
                self._logger.debug(msg=f"Obtained reading: {reading.to_dict()}")

                if global_config.environment.is_testing:
                    break
            except Exception as e:
                self._logger.exception(msg="Error adding the reading to the list of samples", exc_info=e)
            finally:
                await asyncio.sleep(delay=self._SECONDS_BETWEEN_READINGS)

    async def get_measurement(self) -> Measurement:
        try:
            self.__getting_readings = True

            return await self._get_measurement_average()
        except Exception as e:
            self._logger.error(msg="Error getting a measurement", exc_info=e)
        finally:
            self.__readings.clear()
            self.__getting_readings = False

    @abstractmethod
    async def get_reading(self) -> Measurement:
        raise NotImplementedError("A sub-class must be implemented.")

    @abstractmethod
    async def _get_measurement_average(self) -> Measurement:
        raise NotImplementedError("A sub-class must be implemented.")


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

        return Measurement(temperature=random.randint(a=-10, b=40), pressure=random.randint(a=950, b=1050), humidity=random.randint(a=10, b=90))

    async def _get_measurement_average(self) -> Measurement:
        temperature: float = 0
        pressure: float = 0
        humidity: float = 0
        number_of_readings: int = len(self.readings) if len(self.readings) > 0 else 1

        for reading in self.readings:
            temperature += reading.temperature
            pressure += reading.pressure
            humidity += reading.humidity

        return Measurement(
            temperature=int(temperature / number_of_readings),
            pressure=int(pressure / number_of_readings),
            humidity=int(humidity / number_of_readings),
            date_time=datetime.now(),
        )


class GroundTemperatureService(Service):
    __slots__ = ["__sensor"]

    def __init__(self) -> None:
        super().__init__()

        if global_config.environment.is_production:
            self.__sensor = AsyncW1ThermSensor()

    async def get_reading(self) -> Measurement:
        if global_config.environment.is_production:
            return Measurement(temperature=int(await self.__sensor.get_temperature(unit=Unit.DEGREES_C)))

        return Measurement(temperature=random.randint(a=-10, b=40))

    async def _get_measurement_average(self) -> Measurement:
        average: int = int(mean([reading.temperature for reading in self.readings])) if len(self.readings) > 0 else 0
        return Measurement(temperature=average, date_time=datetime.now())


class RainfallService(Service):
    __slots__ = ["__sensor"]

    __BUCKET_SIZE_IN_MM: float = 0.2794

    def __init__(self) -> None:
        super().__init__()

        if global_config.environment.is_production:
            self.__sensor = Button(pin=global_config.device.rain_gauge_port)
            self.__sensor.when_pressed = self._sync_get_reading

    async def _add_value_to_readings(self) -> None:
        if global_config.environment.is_development:
            while True:
                try:
                    if self.getting_readings:
                        return

                    await self.get_reading()
                except Exception as e:
                    self._logger.exception(msg="Error adding the reading to the list of samples", exc_info=e)
                finally:
                    await asyncio.sleep(delay=self._SECONDS_BETWEEN_READINGS)
        else:
            # This sensor does not need to read from the sensor as the when_pressed event is triggered only when water is detected
            pass

    def _sync_get_reading(self) -> None:
        asyncio.run(self.get_reading())

    async def get_reading(self) -> None:
        if self.getting_readings:
            return

        reading: Measurement = Measurement(amount=1)
        self.readings.append(reading)
        self._logger.debug(msg=f"Obtained reading: {reading.to_dict()}")

    async def _get_measurement_average(self) -> Measurement:
        return Measurement(amount=int(round(number=len(self.readings) * self.__BUCKET_SIZE_IN_MM)), date_time=datetime.now())


class WindMeasurementService(Service):
    __slots__ = ["__anemometer", "__vane"]

    def __init__(self, anemometer_port: int) -> None:
        super().__init__()

        if global_config.environment.is_production:
            self.__anemometer = Anemometer(port_number=anemometer_port)
            self.__vane = Vane()

    async def get_reading(self) -> Measurement:
        if global_config.environment.is_production:
            return Measurement(speed=int(self.__anemometer.get_speed()), direction=self.__vane.get_direction())

        return Measurement(speed=random.randint(a=10, b=100), direction=random.choice(seq=list(WindDirection)).value)

    async def _get_measurement_average(self) -> Measurement:
        average_speed: int = int(mean([reading.speed for reading in self.readings])) if len(self.readings) > 0 else 0
        mode_wind_direction: str = mode([reading.direction for reading in self.readings]) if len(self.readings) > 0 else "-"

        return Measurement(
            speed=average_speed,
            direction=mode_wind_direction,
            date_time=datetime.now(),
        )
