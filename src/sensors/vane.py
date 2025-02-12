from gpiozero import MCP3008

from src.colored_logging.colored_logging import get_logger


class Vane(object):
    __slots__ = ["__mcp_chip", "__logger"]

    __CHANNEL: int = 0
    __VOLTAGE_IN: float = 3.3
    __UNKNOWN_WIND_DIRECTION: str = "-"
    __VANE_ANGLES_AND_DIRECTIONS_TABLE: dict[float, str] = {
        0.4: "N",
        1.4: "N-NE",
        1.2: "N-E",
        2.8: "E-NE",
        2.7: "E",
        2.9: "E-SE",
        2.2: "S-E",
        2.5: "S-SE",
        1.8: "S",
        2.0: "S-SW",
        0.7: "S-W",
        0.8: "W-SW",
        0.1: "W",
        0.3: "W-NW",
        0.2: "N-W",
        0.6: "N-NW",
    }

    def __init__(self) -> None:
        self.__logger = get_logger(name=self.__class__.__name__)
        self.__mcp_chip = MCP3008(channel=self.__CHANNEL)

    def get_direction(self) -> str:
        mcp_value: float = self.__mcp_chip.value
        gpio_value: float = round(mcp_value * self.__VOLTAGE_IN, 1)

        self.__logger.debug(msg=f"MCP reading {mcp_value}, GPIO value {gpio_value}.")

        return self.__get_direction_by_gpio_value(value=gpio_value)

    def __get_direction_by_gpio_value(self, value: float) -> str:
        if value in self.__VANE_ANGLES_AND_DIRECTIONS_TABLE:
            return self.__VANE_ANGLES_AND_DIRECTIONS_TABLE[value]

        return self.__UNKNOWN_WIND_DIRECTION
