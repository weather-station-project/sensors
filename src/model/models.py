from dataclasses import dataclass
from datetime import datetime
from typing import final, Optional


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
            ("dateTime" if key == "date_time" else key): value.isoformat() if isinstance(value, datetime) else value
            for key, value in self.__dict__.items()
            if value is not None
        }


@dataclass
@final
class VaneAngleDirection:
    angle: float
    direction: str
