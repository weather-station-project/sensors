import json
from abc import ABC
from http import HTTPStatus
from typing import List

import aiohttp
import socketio
from socketio import exceptions
from tenacity import retry, stop_after_attempt, wait_random

from src.colored_logging.colored_logging import get_logger
from src.model.models import Measurement

NUMBER_OF_ATTEMPTS: int = 3
WAITING_TIME_MIN: int = 1
WAITING_TIME_MAX: int = 2


class Client(ABC):
    __slots__ = ["__auth_url", "__user", "__password", "_logger", "__token"]

    def __init__(self, auth_url: str, user: str, password: str) -> None:
        self._logger = get_logger(name=self.__class__.__name__)

        self.__auth_url = auth_url
        self.__user = user
        self.__password = password
        self.__token = ""

        self._logger.debug(msg=f"{self.__class__.__name__} initialized with user {self.__user} and url {self.__auth_url}")

    async def _set_token(self) -> None:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(
                url=self.__auth_url, json={"login": self.__user, "password": self.__password}, headers={"Content-Type": "application/json"}
            ) as response:
                response.raise_for_status()
                data = await response.json()
                self.__token = data.get("access_token")

    async def _get_token(self) -> str:
        if not self.__token:
            self._logger.debug("Token not set, setting token")
            await self._set_token()

        return self.__token

    def _reset_token(self) -> None:
        self.__token = None


class ApiClient(Client):
    async def add_measurements(self, tuples_endpoint_measurement: List[tuple[str, Measurement]]) -> None:
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                for end_point, measurement in tuples_endpoint_measurement:
                    await self.__process_request(session=session, end_point=end_point, measurement=measurement)
        except aiohttp.ClientResponseError as e:
            self._logger.error(msg=f"Error adding a measurement with the response ({e.status}) {e.message}", exc_info=e)

    @retry(reraise=True, stop=(stop_after_attempt(NUMBER_OF_ATTEMPTS)), wait=wait_random(min=WAITING_TIME_MIN, max=WAITING_TIME_MAX))
    async def __process_request(self, session: aiohttp.ClientSession, end_point: str, measurement: Measurement) -> None:
        token: str = await self._get_token()

        async with session.post(
            url=end_point, json=measurement.to_dict(), headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        ) as response:
            if response.status == HTTPStatus.UNAUTHORIZED:
                self._logger.debug("Token expired, resetting token")
                self._reset_token()

            response.raise_for_status()
            self._logger.info(msg=f"Measurement added through the endpoint {end_point} correctly")


class SocketClient(Client):
    __slots__ = ["__socket_url", "__client"]

    def __init__(self, socket_url: str, auth_url: str, user: str, password: str) -> None:
        super().__init__(auth_url=auth_url, user=user, password=password)

        self.__socket_url = socket_url
        self.__client = socketio.Client()

    @retry(reraise=True, stop=(stop_after_attempt(NUMBER_OF_ATTEMPTS)), wait=wait_random(min=WAITING_TIME_MIN, max=WAITING_TIME_MAX))
    async def emit_measurements(self, tuples_event_measurement: List[tuple[str, Measurement]]) -> None:
        @self.__client.on(event="connect")
        def connection_handler() -> None:
            self._logger.debug(msg=f"Socket connected to the server {self.__socket_url}")

        @self.__client.on(event="disconnect")
        def disconnect_handler(reason) -> None:
            self._logger.debug(msg=f"Socket disconnected with reason '{reason}'")

        @self.__client.on(event="exception")
        def exception_handler(msg: str) -> None:
            if "Invalid token" in msg:
                self._logger.debug("Token expired, resetting token")
                self._reset_token()
            else:
                self._logger.error(msg=f"Exception received from the server with message {msg}")

        try:
            token: str = await self._get_token()
            self.__client.connect(url=self.__socket_url, headers={"Authorization": f"Bearer {token}"}, transports=["websocket"])

            if not self.__client.connected:
                raise exceptions.ConnectionError()

            for event, measurement in tuples_event_measurement:
                self.__client.call(event=event, data=json.dumps(obj=measurement.to_dict()))
                self._logger.info(msg=f"Measurement passed through the event {event} correctly")
        except socketio.exceptions.ConnectionError as e:
            self._logger.error(msg=f"Socket not connected to the server {self.__socket_url}", exc_info=e)
            raise
        except Exception as e:
            self._logger.error(msg=f"Unexpected socket error {e}", exc_info=e)
            raise
        finally:
            if self.__client.connected:
                self.__client.disconnect()
