import os
from typing import final


class Environment:
    __DEVELOPMENT: str = "development"
    __PRODUCTION: str = "production"

    __slots__ = ["__is_development", "__is_production"]

    def __init__(self) -> None:
        environment: str = os.environ.get("ENVIRONMENT", self.__DEVELOPMENT)

        self.__is_development: bool = environment == self.__DEVELOPMENT
        self.__is_production: bool = environment == self.__PRODUCTION

    @property
    def is_development(self) -> bool:
        return self.__is_development

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
    __slots__ = ["__user", "__password", "__root_url"]

    def __init__(self):
        self.__user = os.environ.get("USER", "sensors")
        self.__password = os.environ.get("PASSWORD", "123456")
        self.__root_url = os.environ.get("ROOT_URL", "http://localhost:8080")

    @property
    def user(self) -> str:
        return self.__user

    @property
    def password(self) -> str:
        return self.__password

    @property
    def root_url(self) -> str:
        return self.__root_url


@final
class GlobalConfig:
    __slots__ = ["__environment", "__log", "__api"]

    def __init__(self) -> None:
        self.__environment: Environment = Environment()
        self.__log: LoggingConfig = LoggingConfig()
        self.__api: ApiConfig = ApiConfig()

    @property
    def environment(self) -> Environment:
        return self.__environment

    @property
    def log(self) -> LoggingConfig:
        return self.__log

    @property
    def auth(self) -> ApiConfig:
        return self.__api


global_config = GlobalConfig()
