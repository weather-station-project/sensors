class GettingMeasurementException(Exception):
    __slots__ = ["__service_name"]

    def __init__(self, service_name: str, e: Exception) -> None:
        super().__init__(e)

        self.__service_name = service_name

    @property
    def service_name(self) -> str:
        return self.__service_name


class AddingMeasurementException(Exception):
    __slots__ = ["__response_message", "__response_status"]

    def __init__(self, response_message: str, response_status: int, e: Exception | None) -> None:
        super().__init__(e)

        self.__response_message = response_message
        self.__response_status = response_status

    @property
    def response_message(self) -> str:
        return self.__response_message

    @property
    def response_status(self) -> int:
        return self.__response_status


class EmittingMeasurementException(Exception):
    __slots__ = ["__message"]

    def __init__(self, message: str, e: Exception | None) -> None:
        super().__init__(e)

        self.__message = message

    @property
    def message(self) -> str:
        return self.__message
