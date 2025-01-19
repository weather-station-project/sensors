from abc import ABC

from src.model.measurement import Measurement


class Service(ABC):
    pass

    def get_measurement(self) -> Measurement:
        pass
