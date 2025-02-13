from http import HTTPStatus

import aiohttp
from tenacity import retry, stop_after_attempt, wait_random

from src.colored_logging.colored_logging import get_logger
from src.exceptions.exceptions import AddingMeasurementException
from src.helpers.helpers import SingletonMeta
from src.model.models import Measurement


class MeasurementApiClient(metaclass=SingletonMeta):
    __NUMBER_OF_ATTEMPTS: int = 3
    __WAITING_TIME_MIN: int = 1
    __WAITING_TIME_MAX: int = 2

    __slots__ = ["__auth_url", "__user", "__password", "__logger", "__token"]

    def __init__(self, auth_url: str, user: str, password: str) -> None:
        self.__auth_url = auth_url
        self.__user = user
        self.__password = password
        self.__logger = get_logger(name=self.__class__.__name__)
        self.__token = ""

        self.__logger.debug(msg=f"MeasurementApiClient initialized with user {self.__user} and url {self.__auth_url}")

    async def __set_token(self) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self.__auth_url, json={"login": self.__user, "password": self.__password}, headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self.__token = data.get("access_token")

    async def __get_token(self) -> str:
        if not self.__token:
            await self.__set_token()

        return self.__token

    @retry(reraise=True, stop=(stop_after_attempt(__NUMBER_OF_ATTEMPTS)), wait=wait_random(min=__WAITING_TIME_MIN, max=__WAITING_TIME_MAX))
    async def add_measurement(self, end_point: str, measurement: Measurement) -> None:
        try:
            token = await self.__get_token()
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

            async with aiohttp.ClientSession() as session:
                async with session.post(url=end_point, json=measurement.to_dict(), headers=headers) as response:
                    if response.status == HTTPStatus.UNAUTHORIZED:
                        self.__logger.debug("Token expired, renewing token")
                        await self.__set_token()

                    response.raise_for_status()
        except aiohttp.ClientResponseError as e:
            raise AddingMeasurementException(response_message=e.message, response_status=e.status, e=e)
