class MeasurementException(Exception):
    __slots__ = ["__service_name"]

    def __init__(self, service_name: str, e: Exception) -> None:
        super().__init__(e)

        self.__service_name = service_name

    @property
    def service_name(self) -> str:
        return self.__service_name
