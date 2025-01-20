from dataclasses import dataclass
from datetime import datetime
from typing import final


@dataclass
@final
class Measurement:
    temperature: int | None
    humidity: int | None
    pressure: int | None
    speed: int | None
    direction: str | None
    amount: int | None
    date_time: datetime

    def to_dict(self) -> dict[str, int | str | datetime]:
        return {
            ("dateTime" if key == "date_time" else key): value.isoformat() if isinstance(value, datetime) else value
            for key, value in self.__dict__.items()
            if value is not None
        }
