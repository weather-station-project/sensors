import os
from typing import final

from src.helpers.helpers import get_bool_from_string


class Environment:
    __DEVELOPMENT: str = "development"
    __PRODUCTION: str = "production"

    __slots__ = ["__is_production", "__read_only"]

    def __init__(self) -> None:
        environment: str = os.environ.get("ENVIRONMENT", self.__DEVELOPMENT)

        self.__is_production = environment == self.__PRODUCTION
        self.__read_only = get_bool_from_string(os.environ.get("READ_ONLY", "False"))

    @property
    def is_production(self) -> bool:
        return self.__is_production


class LoggingConfig:
    __slots__ = ["__level"]

    def __init__(self):
        self.__level = os.environ.get("LOG_LEVEL", "DEBUG")

    @property
    def level(self) -> str:
        return self.__level


class ApiConfig:
    __slots__ = [
        "__user",
        "__password",
        "__root_url",
        "__add_ambient_temperature_endpoint",
        "__add_ground_temperature_endpoint",
        "__add_air_measurement_endpoint",
        "__add_wind_measurement_endpoint",
        "__add_rainfall_measurement_endpoint",
    ]

    def __init__(self):
        self.__user = os.environ.get("USER", "sensors")
        self.__password = os.environ.get("PASSWORD", "123456")
        self.__root_url = os.environ.get("ROOT_URL", "http://localhost:8080")
        self.__add_ambient_temperature_endpoint = self.__root_url + "/measurements/ambient-temperature"
        self.__add_ground_temperature_endpoint = self.__root_url + "/measurements/ground-temperature"
        self.__add_air_measurement_endpoint = self.__root_url + "/measurements/air-measurement"
        self.__add_wind_measurement_endpoint = self.__root_url + "/measurements/wind-measurement"
        self.__add_rainfall_measurement_endpoint = self.__root_url + "/measurements/rainfall"

    @property
    def user(self) -> str:
        return self.__user

    @property
    def password(self) -> str:
        return self.__password

    @property
    def root_url(self) -> str:
        return self.__root_url

    @property
    def add_ambient_temperature_endpoint(self) -> str:
        return self.__add_ambient_temperature_endpoint

    @property
    def add_ground_temperature_endpoint(self) -> str:
        return self.__add_ground_temperature_endpoint

    @property
    def add_air_measurement_endpoint(self) -> str:
        return self.__add_air_measurement_endpoint

    @property
    def add_wind_measurement_endpoint(self) -> str:
        return self.__add_wind_measurement_endpoint

    @property
    def add_rainfall_measurement_endpoint(self) -> str:
        return self.__add_rainfall_measurement_endpoint


class DeviceConfig:
    __slots__ = [
        "__minutes_between_readings",
        "__bme280_sensor_enabled",
        "__ground_temperature_sensor_enabled",
        "__rain_gauge_enabled",
        "__anemometer_enabled",
        "__anemometer_port",
        "__rain_gauge_port",
    ]

    def __init__(self):
        self.__minutes_between_readings = int(os.environ.get("MINUTES_BETWEEN_READINGS", 5))
        self.__bme280_sensor_enabled = get_bool_from_string(os.environ.get("BME280_SENSOR_ENABLED", "False"))
        self.__ground_temperature_sensor_enabled = get_bool_from_string(os.environ.get("GROUND_TEMPERATURE_SENSOR_ENABLED", "False"))
        self.__rain_gauge_enabled = get_bool_from_string(os.environ.get("RAIN_GAUGE_ENABLED", "False"))
        self.__anemometer_enabled = get_bool_from_string(os.environ.get("ANEMOMETER_ENABLED", "False"))
        self.__anemometer_port = int(os.environ.get("ANEMOMETER_PORT", "22"))
        self.__rain_gauge_port = int(os.environ.get("RAIN_GAUGE_PORT", "25"))

    @property
    def minutes_between_readings(self) -> int:
        return self.__minutes_between_readings

    @property
    def bme280_sensor_enabled(self) -> bool:
        return self.__bme280_sensor_enabled

    @property
    def ground_temperature_sensor_enabled(self) -> bool:
        return self.__ground_temperature_sensor_enabled

    @property
    def rain_gauge_enabled(self) -> bool:
        return self.__rain_gauge_enabled

    @property
    def anemometer_enabled(self) -> bool:
        return self.__anemometer_enabled

    @property
    def anemometer_port(self) -> int:
        return self.__anemometer_port

    @property
    def rain_gauge_port(self) -> int:
        return self.__rain_gauge_port


@final
class GlobalConfig:
    __slots__ = ["__environment", "__log", "__api", "__device"]

    def __init__(self) -> None:
        self.__environment: Environment = Environment()
        self.__log: LoggingConfig = LoggingConfig()
        self.__api: ApiConfig = ApiConfig()
        self.__device: DeviceConfig = DeviceConfig()

    @property
    def environment(self) -> Environment:
        return self.__environment

    @property
    def log(self) -> LoggingConfig:
        return self.__log

    @property
    def api(self) -> ApiConfig:
        return self.__api

    @property
    def device(self) -> DeviceConfig:
        return self.__device


global_config = GlobalConfig()
