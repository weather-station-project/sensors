from abc import ABC
from typing import List

from src.model.measurement import Measurement


class Service(ABC):
    __slots__ = ["_readings"]

    def __init__(self):
        self._readings = []

    @property
    def readings(self) -> List[Measurement]:
        return self._readings

    def get_measurement(self) -> Measurement:
        pass
