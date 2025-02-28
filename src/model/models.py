from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import final, Optional


@final
class WindDirection(Enum):
    N = "N"
    N_NE = "N-NE"
    N_E = "N-E"
    E_NE = "E-NE"
    E = "E"
    E_SE = "E-SE"
    S_E = "S-E"
    S_SE = "S-SE"
    S = "S"
    S_SW = "S-SW"
    S_W = "S-W"
    W_SW = "W-SW"
    W = "W"
    W_NW = "W-NW"
    N_W = "N-W"
    N_NW = "N-NW"
    UNKNOWN = "-"


@dataclass
@final
class Measurement:
    temperature: Optional[int] = None
    humidity: Optional[int] = None
    pressure: Optional[int] = None
    speed: Optional[int] = None
    direction: Optional[str] = None
    amount: Optional[int] = None
    date_time: Optional[datetime] = None

    def to_dict(self) -> dict[str, int | str | datetime]:
        return {
            ("dateTime" if key == "date_time" else key): value.strftime("%Y-%m-%dT%H:%M:%S") if isinstance(value, datetime) else value
            for key, value in self.__dict__.items()
            if value is not None
        }
