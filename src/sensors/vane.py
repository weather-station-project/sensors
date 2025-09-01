import logging

from gpiozero import MCP3008

from src.model.models import WindDirection


class Vane(object):
    __slots__ = ["__mcp_chip", "__logger"]

    __CHANNEL: int = 0
    __VOLTAGE_IN: float = 3.3
    __UNKNOWN_WIND_DIRECTION: str = "-"
    __VANE_ANGLES_AND_DIRECTIONS_TABLE: list[tuple[float, str]] = sorted(
        [
            (0.4, WindDirection.N),
            (1.4, WindDirection.N_NE),
            (1.2, WindDirection.N_E),
            (2.8, WindDirection.E_NE),
            (2.7, WindDirection.E),
            (2.9, WindDirection.E_SE),
            (2.2, WindDirection.S_E),
            (2.5, WindDirection.S_SE),
            (1.8, WindDirection.S),
            (2.0, WindDirection.S_SW),
            (0.7, WindDirection.S_W),
            (0.8, WindDirection.W_SW),
            (0.1, WindDirection.W),
            (0.3, WindDirection.W_NW),
            (0.2, WindDirection.N_W),
            (0.6, WindDirection.N_NW),
        ],
        key=lambda x: x[0],
    )

    def __init__(self) -> None:
        self.__logger = logging.getLogger(name=self.__class__.__name__)
        self.__mcp_chip = MCP3008(channel=self.__CHANNEL)

    def get_direction(self) -> str:
        mcp_value: float = self.__mcp_chip.value
        gpio_value: float = round(mcp_value * self.__VOLTAGE_IN, 1)

        self.__logger.debug(msg=f"MCP reading {mcp_value}, GPIO value {gpio_value}.")

        return self.__get_direction_by_gpio_value(value=gpio_value)

    def __get_direction_by_gpio_value(self, value: float) -> str:
        last_direction: str = self.__UNKNOWN_WIND_DIRECTION

        for gpio_item_value, direction in self.__VANE_ANGLES_AND_DIRECTIONS_TABLE:
            gpio_item_value: float
            direction: WindDirection

            if value < gpio_item_value:
                return last_direction

            last_direction = direction.value

        return last_direction
