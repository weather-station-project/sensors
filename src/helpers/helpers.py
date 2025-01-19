import requests

from src.model.measurement import Measurement


def get_bool_from_string(value: str) -> bool:
    return value.lower() in ["true", "t", "1"]


def add_measurement_to_api(url: str, user: str, password: str, measurement: Measurement) -> None:
    try:
        response = requests.post(url, auth=(user, password), json=measurement.to_dict())
        response.raise_for_status()
    except Exception as e:
        raise e
