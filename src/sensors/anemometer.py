import math
import time

from gpiozero import Button


class Anemometer(object):
    __slots__ = ["__spin_count", "__start_time", "__sensor"]

    __SENSOR_RADIUS_CM: float = 9.0
    __SENSOR_CIRCUMFERENCE_LONG_KM: float = (2 * math.pi) * __SENSOR_RADIUS_CM / 100000.0
    __SENSOR_ADJUSTMENT: float = 1.18

    def __init__(self, port_number: int) -> None:
        self.__spin_count = 0
        self.__start_time = time.time()
        self.__sensor = Button(pin=port_number)
        self.__sensor.when_pressed = self.__spin

    def __spin(self) -> None:
        self.__spin_count = self.__spin_count + 1

    def get_speed(self) -> float:
        try:
            current_count: int = self.__spin_count
            elapsed_seconds: float = time.time() - self.__start_time

            return self.__calculate_speed(current_spin_count=current_count, elapsed_seconds=elapsed_seconds)
        finally:
            self.__spin_count = 0
            self.__start_time = time.time()

    def __calculate_speed(self, current_spin_count: int, elapsed_seconds: float) -> float:
        rotations: float = current_spin_count / 2.0
        speed_per_hour: float = ((self.__SENSOR_CIRCUMFERENCE_LONG_KM * rotations) / elapsed_seconds) * 3600

        return speed_per_hour * self.__SENSOR_ADJUSTMENT
