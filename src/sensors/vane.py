from gpiozero import MCP3008

from src.colored_logging.colored_logging import get_logger
from src.model.models import VaneAngleDirection


class Vane(object):
    __slots__ = ["__mcp_chip", "__logger"]

    __CHANNEL: int = 0
    __VOLTAGE_IN: float = 3.3
    __UNKNOWN_WIND_DIRECTION: str = "-"
    __VANE_ANGLES_AND_DIRECTIONS_TABLE: dict[float, VaneAngleDirection] = {
        0.4: VaneAngleDirection(angle=0.0, direction="N"),
        1.4: VaneAngleDirection(angle=22.5, direction="N-NE"),
        1.2: VaneAngleDirection(angle=45.0, direction="N-E"),
        2.8: VaneAngleDirection(angle=67.5, direction="E-NE"),
        2.7: VaneAngleDirection(angle=90.0, direction="E"),
        2.9: VaneAngleDirection(angle=112.5, direction="E-SE"),
        2.2: VaneAngleDirection(angle=135.0, direction="S-E"),
        2.5: VaneAngleDirection(angle=157.5, direction="S-SE"),
        1.8: VaneAngleDirection(angle=180.0, direction="S"),
        2.0: VaneAngleDirection(angle=202.5, direction="S-SW"),
        0.7: VaneAngleDirection(angle=225.0, direction="S-W"),
        0.8: VaneAngleDirection(angle=247.5, direction="W-SW"),
        0.1: VaneAngleDirection(angle=270.0, direction="W"),
        0.3: VaneAngleDirection(angle=292.5, direction="W-NW"),
        0.2: VaneAngleDirection(angle=315.0, direction="N-W"),
        0.6: VaneAngleDirection(angle=337.5, direction="N-NW"),
    }

    def __init__(self) -> None:
        self.__logger = get_logger(name=self.__class__.__name__)
        self.__mcp_chip = MCP3008(channel=self.__CHANNEL)

    def get_direction(self) -> str:
        mcp_value: float = self.__mcp_chip.value
        gpio_value: float = round(mcp_value * self.__VOLTAGE_IN, 1)

        self.__logger.debug(msg=f"MCP reading {mcp_value}, GPIO value {gpio_value}.")

        return self.__get_direction_by_angle(angle=gpio_value)

    def __get_direction_by_angle(self, angle: float) -> str:
        current_direction: str = self.__UNKNOWN_WIND_DIRECTION

        for _, item in self.__VANE_ANGLES_AND_DIRECTIONS_TABLE.items():
            if item.angle > angle:
                return current_direction

            current_direction = item.direction

        return current_direction
