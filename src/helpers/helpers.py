import requests

from src.model.models import Measurement


def get_bool_from_string(value: str) -> bool:
    return value.lower() in ["true", "t", "1"]


async def add_measurement_to_api(url: str, user: str, password: str, measurement: Measurement) -> None:
    try:
        # TODO AUTH!
        response = requests.post(url, auth=(user, password), json=measurement.to_dict())
        response.raise_for_status()
    except Exception as e:
        raise e
